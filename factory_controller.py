import simpy 
from device import Device  
from idle_rack import IdleRack
from charging_station import ChargingStation 


class FactoryController:
    def __init__(self, env):
        self.env = env
        self.idle_rack = IdleRack(env)
        self.charging_station = {
            
            }

    def run(self, until):
        def arrivals():
            device_id = 1
            while True:
                yield self.env.timeout(5)
                self.on_arrival(Device(device_id))
                device_id += 1
        self.env.process(arrivals())
        self.env.run(until = until)

    # d = Device
    def on_arrival(self, d):
        d.arrival_time = self.env.now
        d.state = "IDLE"
        self.idle_rack.put(d)
        print("Time", self.env.now, "Device", d.device_id, "State", d.state)

    def assign_charger(self, d):
