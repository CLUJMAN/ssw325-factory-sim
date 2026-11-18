import simpy

class Device:
    def __init__(self, device_id):
        self.device_id = device_id
        self.state = "NEW"
        self.arrival_time = None
        self.charge_start = None
        self.charge_end = None 
        self.battery_level = None