import simpy

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