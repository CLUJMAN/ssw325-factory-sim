import simpy
import random 

class ChargingStation:
    def __init__(self, env, station_id, position, mean_charge_time=30):   
        self.env = env                                           
        self.station_id = station_id
        self.name = station_id               # used in MoveCommand descriptions
        self.position = position             # (x, y) grid location
        self.mean_charge_time = mean_charge_time
        self.current_device = None


    def load(self, d):
        self.current_device = d

    def is_available(self):
        return self.current_device is None

    def reserve(self, d):
        self.current_device = d

    def unload(self):
        d = self.current_device
        self.current_device = None
        return d

    def charging(self, d):
        charge_time = random.expovariate(1 / self.mean_charge_time)
        d.charge_start = self.env.now

        yield self.env.timeout(charge_time)

        d.charge_end = self.env.now
        d.state = "CHARGED"  # Use the state name your model expects
        self.current_device = None  # Station is available again
        print(f"Time {self.env.now:.2f} Device {d.device_id} finished charging on {self.station_id}")
