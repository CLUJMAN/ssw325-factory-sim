import simpy 
from device import Device  
from idle_rack import IdleRack
from charging_station import ChargingStation 


class FactoryController:
    def __init__(self, env):
        self.env = env
        self.idle_rack = IdleRack(env)
        self.charging_stations = []
        for i in range(1, 25):                                   # FIX: 24 chargers
            self.charging_stations.append(ChargingStation(env, f"CS{i}"))

    def run(self, until):
        def arrivals():
            device_id = 1
            while True:
                yield self.env.timeout(5)
                self.on_arrival_idle_rack(Device(device_id))
                device_id += 1
        self.env.process(arrivals())
        self.env.process(self.dispatcher())                      # FIX: start the dispatcher
        self.env.run(until=until)

    # d = Device
    #Puts a device onto the IdleRack and logs when the device was put onto the Idle Rack
    def on_arrival_idle_rack(self, d):
        d.arrival_time = self.env.now
        d.state = "IDLE"
        self.idle_rack.put(d)
        print("Time", self.env.now, "Device", d.device_id, "State", d.state,
              "| rack size", self.idle_rack.size())

     # pulls devices off the IdleRack and assigns them a charger
    def dispatcher(self):
        while True:
            d = yield self.idle_rack.get()           # wait for a device in the rack
            print("Time", self.env.now, "Device", d.device_id, "taken from IdleRack",
                  "| rack size", self.idle_rack.size())
            cs = self.assign_charger(d)
            while cs is None:                        # all chargers busy → retry every minute
                yield self.env.timeout(1)
                cs = self.assign_charger(d)
            self.env.process(cs.charging(d)) 


    def assign_charger(self, d):
        for cs in self.charging_stations:
            if cs.is_available():
                cs.reserve(d)
                d.state = "CHARGING"
                print("Time", self.env.now, "Device", d.device_id, "assigned to", cs.station_id)
                return cs
        return None

       

    
        


