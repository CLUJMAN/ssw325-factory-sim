import random
import simpy
from factory_controller import FactoryController

SIM_TIME = 8 * 60                     # one 8-hour shift, in minutes
random.seed(42)                       # same results every run

env = simpy.Environment()
fc = FactoryController(env)
fc.run(until=SIM_TIME)

s = fc.stats(SIM_TIME)
print("\n===== Results =====")
print(f"Simulated time:        {SIM_TIME} min")
print(f"Devices arrived:       {s['arrived']}")
print(f"Devices tested (done): {s['tested']}  (passed {s['passed']})")
print(f"Throughput:            {s['throughput_per_hour']:.2f} devices/hour")
print(f"Avg cycle time:        {s['avg_cycle_time']:.1f} min")
print(f"Still in IdleRack:     {s['idle_rack_size']}")
print(f"Arm utilization:       {s['arm_utilization']:.1%}  ({s['arm_moves']} moves, avg wait {s['avg_arm_wait']:.1f} min)")
print(f"Charger utilization:   {s['charger_utilization']:.1%}")
print(f"Bench utilization:     {s['bench_utilization']:.1%}")
print(f"Safety violations:     {s['safety_violations']}")
