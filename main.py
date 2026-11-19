import random
import simpy
from factory_controller import FactoryController

SIM_TIME = 120
random.seed(42)                       # same results every run

env = simpy.Environment()
fc = FactoryController(env)
fc.run(until=SIM_TIME)

print("\nStill in IdleRack:", [d.device_id for d in fc.idle_rack.queue.items])
for cs in fc.charging_stations[:6]:
    print(cs.station_id, cs.position, "->", cs.current_device.device_id if cs.current_device else None)
print(f"\nArm moves completed: {fc.arm.moves_completed}")
print(f"Arm utilization: {fc.arm.utilization(SIM_TIME):.1%}")
