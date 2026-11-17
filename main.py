import simpy
from factory_controller import FactoryController 

if __name__ == "__main__":
    env = simpy.Environment()
    fc = FactoryController(env)
    fc.run(until=30)
    print("In IdleRack:", fc.idle_rack.size()) 