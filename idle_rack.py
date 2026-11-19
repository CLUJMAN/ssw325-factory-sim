import simpy 

class IdleRack:
    def __init__(self, env, position=(0, 0)):
        self.name = "IdleRack"
        self.position = position
        self.queue = simpy.Store(env)

    # d = Device
    def put(self, d):
        return self.queue.put(d)

    def size(self):
        return len(self.queue.items)

    def get(self):
        return self.queue.get()
