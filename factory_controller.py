import simpy
from device import Device
from idle_rack import IdleRack
from charging_station import ChargingStation
from test_branch import TestStation
from robotic_arm import RoboticArm
from move_command import MoveCommand


class FactoryController:
    def __init__(self, env, num_chargers=24, arrival_interval=1, base_travel_rate=0.2):
        self.env = env
        self.arrival_interval = arrival_interval

        # Layout (grid units): IdleRack at (0, 0), chargers C1..C24 in a block of 6 columns
        # starting at x=2, so C1=(2,0), C6=(7,0), C7=(2,1), ... C24=(7,3)
        self.idle_rack = IdleRack(env, position=(0, 0))
        self.charging_stations = []
        self.test_stations = []
        for i in range(1, num_chargers + 1):
            pos = (2 + (i - 1) % 6, (i - 1) // 6)
            self.charging_stations.append(ChargingStation(env, f"C{i}", pos))
        for i in range(1,20):
            self.test_stations.append(TestStation(env, f"CS{i}"))

        self.arm = RoboticArm(env, "Arm1", position=(0, 0), base_travel_rate=base_travel_rate)
        self.move_log = []                              # every MoveCommand issued

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

    # d = Device
    # Puts a device onto the IdleRack and logs when the device was put onto the Idle Rack
    def on_arrival_idle_rack(self, d):
        d.arrival_time = self.env.now
        d.state = "IDLE"
        self.idle_rack.put(d)
        print(f"Time {self.env.now:.2f} Device {d.device_id} State {d.state}"
              f" | rack size {self.idle_rack.size()}")

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

            self.env.process(cs.charge_device(d))

    def assign_charger(self, d):
        for cs in self.charging_stations:
            if cs.is_available_charging():
                cs.reserve_charging(d)               # hold the station so nobody else takes it
                print(f"Time {self.env.now:.2f} Device {d.device_id} assigned to {cs.station_id}")
                return cs
        return None

    # creates a MoveCommand, logs it, and runs it on the arm
    def issue_move(self, d, source, destination):
        cmd = MoveCommand(d, source, destination, issued_at=self.env.now)
        self.move_log.append(cmd)
        yield self.env.process(self.arm.execute(cmd))
        return cmd

    def on_charge_complete(self, d, cs):
        cs.unload_charging(d)
        print("Time", round(self.env.now, 2), "Device", d.device_id,
            "charge complete, unloaded from", cs.station_id)

    def assign_test_bench(self, d):
        for ts in self.test_stations:
            if ts.is_available_test():
                ts.reserve_test(d)
                d.state = "TESTING"
                print("Time", self.env.now, "Device", d.device_id, "assigned to", ts.station_id)
                return ts
        return None

    def on_test_complete(self, d, ts):
        ts.unload_test(d)
        print("Time", round(self.env.now, 2), "Device", d.device_id,
              "test complete, unloaded from", ts.station_id)
