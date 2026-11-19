import simpy
import random 

class ChargingStation:
    def __init__(self, env, station_id, mean_charge_time=30):   
        self.env = env                                           
        self.station_id = station_id
        self.mean_charge_time = mean_charge_time
        self.current_device = None


    def load_charging(self, d):
        self.current_device = d

    def unload_charging(self, d):
        d = self.current_device 
        self.current_device = None
        return d 

    def is_available_charging(self):
        return self.current_device is None

    def reserve_charging(self, d):
        self.current_device = d

    def charge_device(self, d):
        charge_time = random.expovariate(1 / self.mean_charge_time)
        d.charge_start = self.env.now
        d.state = "CHARGING"

        yield self.env.timeout(charge_time)

        d.charge_end = self.env.now
        d.state = "CHARGED"  # Use the state name your model expects
        print("Time", self.env.now, "Device", d.device_id, "finished charging")

    