import simpy 

class IdleRack:
    def __init__(self, env):
        self.queue = simpy.Store(env)

    # d = Device
    def put(self, d):
        return self.queue.put(d)

    def size(self):
        return len(self.queue.items)
