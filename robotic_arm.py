import random
import simpy


class RoboticArm:
    def __init__(self, env, arm_id, position=(0, 0), base_travel_rate=0.2):
        self.env = env
        self.arm_id = arm_id
        self.position = position                      # (x, y) grid location of the arm
        self.state = "IDLE"                           # IDLE or MOVING
        self.resource = simpy.Resource(env, capacity=1)   # only one move at a time
        self.held_device = None
        self.base_travel_rate = base_travel_rate      # minutes per grid unit
        self.busy_time = 0.0
        self.moves_completed = 0

    # Manhattan distance * base rate * random +/-5%
    def travel_time(self, src, dst):
        distance = abs(src[0] - dst[0]) + abs(src[1] - dst[1])
        return distance * self.base_travel_rate * random.uniform(0.95, 1.05)

    def pick(self, d, loc):
        if hasattr(loc, "unload"):                    # stations/benches; IdleRack already gave d up via get()
            loc.unload()
        self.held_device = d

    def place(self, d, loc):
        loc.load(d)
        self.held_device = None

    # SimPy process: wait for the arm, travel to source, pick, travel to destination, place
    def execute(self, cmd):
        with self.resource.request() as req:
            yield req                                 # wait in line if the arm is busy
            cmd.started_at = self.env.now
            self.state = "MOVING"
            print(f"Time {self.env.now:.2f} {self.arm_id} start: {cmd.describe()}")

            # leg 1: from wherever the arm is to the source
            yield self.env.timeout(self.travel_time(self.position, cmd.source.position))
            self.position = cmd.source.position
            self.pick(cmd.device, cmd.source)

            # leg 2: carry the device to the destination
            yield self.env.timeout(self.travel_time(self.position, cmd.destination.position))
            self.position = cmd.destination.position
            self.place(cmd.device, cmd.destination)

            cmd.completed_at = self.env.now
            self.busy_time += cmd.completed_at - cmd.started_at
            self.moves_completed += 1
            self.state = "IDLE"
            print(f"Time {self.env.now:.2f} {self.arm_id} done:  {cmd.describe()}")

    def utilization(self, total_time):
        return self.busy_time / total_time if total_time > 0 else 0.0
