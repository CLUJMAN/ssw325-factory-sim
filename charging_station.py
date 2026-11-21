import random


class ChargingStation:
    def __init__(self, env, station_id, position, mean_charge_time=30):
        self.env = env
        self.station_id = station_id
        self.name = station_id               # used in MoveCommand descriptions
        self.position = position             # (x, y) grid location
        self.mean_charge_time = mean_charge_time
        self.current_device = None
        self.state = "AVAILABLE"             # AVAILABLE / RESERVED / CHARGING / CHARGED
        self.busy_time = 0.0                 # total time the station was occupied
        self.occupied_since = None

    def is_available_charging(self):
        return self.current_device is None

    # claim the station for d before the arm brings it over
    def reserve_charging(self, d):
        self.current_device = d
        self.state = "RESERVED"
        self.occupied_since = self.env.now

    # the arm puts d onto the station
    def load_charging(self, d):
        self.current_device = d

    # the arm takes the device off; the station is free again
    def unload_charging(self, d=None):
        d = self.current_device
        self.current_device = None
        self.state = "AVAILABLE"
        if self.occupied_since is not None:
            self.busy_time += self.env.now - self.occupied_since
            self.occupied_since = None
        return d

    def charge_device(self, d):
        charge_time = random.expovariate(1 / self.mean_charge_time)
        d.charge_start = self.env.now
        d.state = "CHARGING"
        self.state = "CHARGING"

        yield self.env.timeout(charge_time)

        d.charge_end = self.env.now
        d.battery_level = 100.0
        d.state = "CHARGED"
        self.state = "CHARGED"               # device stays here until the arm picks it up
        print(f"Time {self.env.now:.2f} Device {d.device_id} finished charging on {self.station_id}")

    # fraction of total_time this station was occupied (reserved, charging, or waiting for pickup)
    def utilization(self, total_time):
        busy = self.busy_time
        if self.occupied_since is not None:
            busy += self.env.now - self.occupied_since
        return busy / total_time if total_time > 0 else 0.0
