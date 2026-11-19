import simpy 
import random 

class TestStation:
    def __init__(self, env, test_branch_id, mean_test_time = 20):
        self.env = env 
        self.test_branch_id = test_branch_id 
        self.current_device = None 

    def load_test(self, d):
        self.current_device = d
    
    def unload_test(self, d):
        d = self.current_device 
        self.current_device = None
        return d 
    
    def is_available_test(self):
        return self.current_device is None
    
    def reserve_test(self, d):
        self.current_device = d

    def test(self, d):
        test_time = random.expovariate(1 / self.mean_test_time)
        d.test_start = self.env.now 
        d.state = "TESTING"
        yield self.env.timeout(test_time)

        d.test_end = self.env.now
        d.state = "TESTED"
        print("Time", self.env.now, "Device", d.device_id, "finished testing")

