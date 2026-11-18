
import simpy
from factory_controller import FactoryController

env = simpy.Environment()
fc = FactoryController(env)
fc.run(until=30)

print("\nStill in IdleRack:", [d.device_id for d in fc.idle_rack.queue.items])
for cs in fc.charging_stations[:6]:
    print(cs.station_id, "->", cs.current_device.device_id if cs.current_device else None)