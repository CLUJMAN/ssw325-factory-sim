import simpy
import random 

class ChargingStation:
    def __init__(self, env, station_id, mean_charge_time=30):   
        self.env = env                                           
        self.station_id = station_id
        self.mean_charge_time = mean_charge_time
        self.current_device = None


    def load(self, d):
        self.current_device = d

    def is_available(self):
        return self.current_device is None

    def reserve(self, d):
        self.current_device = d

    def charging(self, d):
        charge_time = random.expovariate(1 / self.mean_charge_time)
        d.charge_start = self.env.now

        yield self.env.timeout(charge_time)

        d.charge_end = self.env.now
        d.state = "CHARGED"  # Use the state name your model expects
        self.current_device = None  # Station is available again
        print("Time", self.env.now, "Device", d.device_id, "finished charging")
