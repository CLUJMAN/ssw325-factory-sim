import simpy 
from device import Device  
from idle_rack import IdleRack
from charging_station import ChargingStation 
from test_branch import TestStation 


class FactoryController:
    def __init__(self, env):
        self.env = env
        self.idle_rack = IdleRack(env)
        self.charging_stations = []
        self.test_stations = []
        for i in range(1, 25):                                   # FIX: 24 chargers
            self.charging_stations.append(ChargingStation(env, f"CS{i}"))
        for i in range(1,20):
            self.test_stations.append(TestStation(env, f"CS{i}"))

    def run(self, until):
        def arrivals():
            device_id = 1
            while True:
                yield self.env.timeout(1)
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
            self.env.process(cs.charge_device(d)) 


    def assign_charger(self, d):
        for cs in self.charging_stations:
            if cs.is_available_charging():
                cs.reserve_charging(d)
                d.state = "CHARGING"
                print("Time", self.env.now, "Device", d.device_id, "assigned to", cs.station_id)
                return cs
        return None

    def on_charge_complete(self, d, cs):
        cs.unload_charging(d)
        print("Time", round(self.env.now, 2), "Device", d.device_id,
            "charge complete, unloaded from", cs.station_id)

    def assign_test_bench(self, d):
        for ts in self.test_stations:
            if ts.is_available_test():
                ts.reserve_test(d)
                d.state = "TESTING"
                print("Time", self.env.now, "Device", d.device_id, "assigned to", ts.station_id)
                return ts
        return None 

    def on_test_complete(self, d, ts):
        ts.unload_test(d)
        print("Time", round(self.env.now, 2), "Device", d.device_id,
              "test complete, unloaded from", ts.station_id)

    
    



       

    
        


