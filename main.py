
import simpy
from factory_controller import FactoryController

env = simpy.Environment()
fc = FactoryController(env)
fc.run(until=30)

print("\nStill in IdleRack:", [d.device_id for d in fc.idle_rack.queue.items])
