class Device:
    def __init__(self, device_id):
        self.device_id = device_id
        self.state = "NEW"
        self.battery_level = 0.0          # percent, 0..100
        self.location = None              # name of where the device currently is
        self.arrival_time = None
        self.charge_start = None
        self.charge_end = None
        self.test_start = None
        self.test_end = None
        self.test_result = None           # True = passed, False = failed
        self.done_time = None

    def is_fully_charged(self):
        return self.battery_level >= 100

    def set_state(self, s):
        self.state = s

    # total time in the factory, from arrival to reaching the DoneRack
    def cycle_time(self):
        if self.done_time is None or self.arrival_time is None:
            return None
        return self.done_time - self.arrival_time
