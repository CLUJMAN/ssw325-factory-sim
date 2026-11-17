import simpy

class ChargingStation:
    def __init__(self, station_id, mean_charge_time = 30):
        self.station_id = station_id 
        self.mean_charge_time = mean_charge_time
        self.current_device = None

    # d = Device
    def load(self, d):
        self.current_device = d
