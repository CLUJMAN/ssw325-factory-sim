import simpy
from device import Device
from idle_rack import IdleRack
from charging_station import ChargingStation
from test_branch import TestStation
from done_rack import DoneRack
from robotic_arm import RoboticArm
from move_command import MoveCommand


class FactoryController:
    def __init__(self, env, num_chargers=24, num_benches=20, arrival_interval=1,
                 base_travel_rate=0.2, mean_charge_time=30, mean_test_time=20):
        self.env = env
        self.arrival_interval = arrival_interval

        # Layout (grid units, used for Manhattan distance):
        #   IdleRack        (0, 0)
        #   Chargers        C1..C24 in rows of 6 starting at (2, 0): C1=(2,0) ... C24=(7,3)
        #   Test benches    T(r-c) in a grid of 5 columns starting at (2, 5): T(1-1)=(2,5) ... T(4-5)=(6,8)
        #   DoneRack        (0, 9)
        self.idle_rack = IdleRack(env, position=(0, 0))

        self.charging_stations = []
        for i in range(1, num_chargers + 1):
            pos = (2 + (i - 1) % 6, (i - 1) // 6)
            self.charging_stations.append(ChargingStation(env, f"C{i}", pos, mean_charge_time))

        self.test_stations = []
        for i in range(num_benches):
            r, c = i // 5 + 1, i % 5 + 1
            pos = (2 + (c - 1), 5 + (r - 1))
            self.test_stations.append(TestStation(env, f"T({r}-{c})", pos, mean_test_time))

        self.done_rack = DoneRack(position=(0, 9))
        self.arm = RoboticArm(env, "Arm1", position=(0, 0), base_travel_rate=base_travel_rate)

        # bookkeeping for stats
        self.move_log = []                 # every MoveCommand issued
        self.arrived = 0
        self.tested = 0
        self.safety_violations = 0         # devices that reached testing without a full charge (should stay 0)

    def run(self, until):
        def arrivals():
            device_id = 1
            while True:
                yield self.env.timeout(self.arrival_interval)
                self.on_arrival_idle_rack(Device(device_id))
                device_id += 1
        self.env.process(arrivals())
        self.env.process(self.dispatcher())
        self.env.run(until=until)

    # ---------- Arrival ----------
    # Puts a device onto the IdleRack and logs when the device was put onto the Idle Rack
    def on_arrival_idle_rack(self, d):
        d.arrival_time = self.env.now
        d.state = "IDLE"
        d.location = self.idle_rack.name
        self.idle_rack.put(d)
        self.arrived += 1
        print(f"Time {self.env.now:.2f} Device {d.device_id} State {d.state}"
              f" | rack size {self.idle_rack.size()}")

    # ---------- IdleRack -> Charger ----------
    # pulls devices off the IdleRack, assigns a charger, has the arm move it there, starts charging
    def dispatcher(self):
        while True:
            d = yield self.idle_rack.get()           # wait for a device in the rack
            cs = self.assign_charger(d)
            while cs is None:                        # all chargers busy -> retry every minute
                yield self.env.timeout(1)
                cs = self.assign_charger(d)

            d.state = "MOVING"
            yield self.env.process(self.issue_move(d, self.idle_rack, cs))   # wait for the arm to deliver it

            self.env.process(self.device_lifecycle(d, cs))

    def assign_charger(self, d):
        for cs in self.charging_stations:
            if cs.is_available_charging():
                cs.reserve_charging(d)               # hold the station so nobody else takes it
                print(f"Time {self.env.now:.2f} Device {d.device_id} assigned to {cs.station_id}")
                return cs
        return None

    # charge -> test -> done for one device
    def device_lifecycle(self, d, cs):
        yield self.env.process(cs.charge_device(d))
        yield self.env.process(self.on_charge_complete(d, cs))

    # ---------- Charger -> Test bench ----------
    def on_charge_complete(self, d, cs):
        print(f"Time {self.env.now:.2f} Device {d.device_id} charge complete on {cs.station_id}")

        # safety rule: a device may only be tested once it is fully charged
        if not self.can_test(d):
            self.safety_violations += 1
            print(f"Time {self.env.now:.2f} SAFETY: Device {d.device_id} not fully charged, keep charging")
            yield self.env.process(cs.charge_device(d))

        # the device stays on its charger (keeping it busy) until a bench is free
        tb = self.assign_test_bench(d)
        while tb is None:
            yield self.env.timeout(1)
            tb = self.assign_test_bench(d)

        d.state = "MOVING"
        yield self.env.process(self.issue_move(d, cs, tb))    # arm unloads the charger and loads the bench
        yield self.env.process(tb.test(d))
        yield self.env.process(self.on_test_complete(d, tb))

    def can_test(self, d):
        return d.state == "CHARGED" and d.is_fully_charged()

    def assign_test_bench(self, d):
        for ts in self.test_stations:
            if ts.is_available_test():
                ts.reserve_test(d)
                print(f"Time {self.env.now:.2f} Device {d.device_id} assigned to {ts.station_id}")
                return ts
        return None

    # ---------- Test bench -> DoneRack ----------
    def on_test_complete(self, d, ts):
        d.state = "MOVING"
        yield self.env.process(self.issue_move(d, ts, self.done_rack))   # arm unloads the bench
        d.state = "DONE"
        d.done_time = self.env.now
        self.tested += 1
        print(f"Time {self.env.now:.2f} Device {d.device_id} DONE | cycle time {d.cycle_time():.2f} min")

    # ---------- Arm commands ----------
    # creates a MoveCommand, logs it, and runs it on the arm
    def issue_move(self, d, source, destination):
        cmd = MoveCommand(d, source, destination, issued_at=self.env.now)
        self.move_log.append(cmd)
        yield self.env.process(self.arm.execute(cmd))
        return cmd

    # ---------- Statistics ----------
    def stats(self, total_time):
        finished = self.done_rack.get_finished()
        cycle_times = [d.cycle_time() for d in finished]
        waits = [c.started_at - c.issued_at for c in self.move_log if c.started_at is not None]
        n_c, n_t = len(self.charging_stations), len(self.test_stations)
        return {
            "arrived": self.arrived,
            "tested": self.tested,
            "passed": sum(1 for d in finished if d.test_result),
            "throughput_per_hour": self.tested / total_time * 60 if total_time > 0 else 0.0,
            "avg_cycle_time": sum(cycle_times) / len(cycle_times) if cycle_times else 0.0,
            "idle_rack_size": self.idle_rack.size(),
            "arm_utilization": self.arm.utilization(total_time),
            "arm_moves": self.arm.moves_completed,
            "avg_arm_wait": sum(waits) / len(waits) if waits else 0.0,
            "charger_utilization": sum(cs.utilization(total_time) for cs in self.charging_stations) / n_c if n_c else 0.0,
            "bench_utilization": sum(ts.utilization(total_time) for ts in self.test_stations) / n_t if n_t else 0.0,
            "safety_violations": self.safety_violations,
        }
