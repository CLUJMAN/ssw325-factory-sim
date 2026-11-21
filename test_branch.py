import random


class TestStation:
    def __init__(self, env, station_id, position, mean_test_time=20, pass_rate=0.95):
        self.env = env
        self.station_id = station_id         # e.g. "T(1-1)"
        self.name = station_id               # used in MoveCommand descriptions
        self.position = position             # (x, y) grid location
        self.mean_test_time = mean_test_time
        self.pass_rate = pass_rate           # chance a device passes its test
        self.current_device = None
        self.state = "AVAILABLE"             # AVAILABLE / RESERVED / TESTING / TESTED
        self.busy_time = 0.0
        self.occupied_since = None

    def is_available_test(self):
        return self.current_device is None

    def reserve_test(self, d):
        self.current_device = d
        self.state = "RESERVED"
        self.occupied_since = self.env.now

    def load_test(self, d):
        self.current_device = d

    def unload_test(self, d=None):
        d = self.current_device
        self.current_device = None
        self.state = "AVAILABLE"
        if self.occupied_since is not None:
            self.busy_time += self.env.now - self.occupied_since
            self.occupied_since = None
        return d

    def test(self, d):
        test_time = random.expovariate(1 / self.mean_test_time)
        d.test_start = self.env.now
        d.state = "TESTING"
        self.state = "TESTING"

        yield self.env.timeout(test_time)

        d.test_end = self.env.now
        d.test_result = random.random() < self.pass_rate
        d.state = "TESTED"
        self.state = "TESTED"
        result = "PASS" if d.test_result else "FAIL"
        print(f"Time {self.env.now:.2f} Device {d.device_id} finished testing on {self.station_id}: {result}")

    def utilization(self, total_time):
        busy = self.busy_time
        if self.occupied_since is not None:
            busy += self.env.now - self.occupied_since
        return busy / total_time if total_time > 0 else 0.0
