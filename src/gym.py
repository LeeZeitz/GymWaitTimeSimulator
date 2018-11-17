import simpy
import random

NUMBER_OF_FREE_WEIGHTS = 5
NUMBER_OF_RACKS = 3
NUMBER_OF_MACHINES = 4
NUMBER_OF_BIKES = 50
NUMBER_OF_CARDIO = 20
NUMBER_OF_BENCHES = 2

FREE_WEIGHT_TIME = 30
BIKE_TIME = 30
CARDIO_TIME = 60
MACHINE_TIME = 30
RACK_TIME = 15
BENCH_TIME = 15

class Gym(object):

    def __init__(self, env):
        self.env = env
        self.weights = simpy.Resource(env, capacity=NUMBER_OF_FREE_WEIGHTS)
        self.racks = simpy.Resource(env, capacity=NUMBER_OF_RACKS)
        self.machines = simpy.Resource(env, capacity=NUMBER_OF_MACHINES)
        self.cardio = simpy.Resource(env, capacity=NUMBER_OF_CARDIO)
        self.bikes = simpy.Resource(env, capacity=NUMBER_OF_BIKES)
        self.benches = simpy.Resource(env, capacity=NUMBER_OF_BENCHES)

    
    def lift_free_weights(self, id):
        yield self.env.timeout(FREE_WEIGHT_TIME)
        print ('Customer {0} leaving free weights at {1:2f}...'.format(id, self.env.now))

    def use_rack(self, id):
        yield self.env.timeout(RACK_TIME)
        print ('Customer {0} leaving a rack at {1:2f}...'.format(id, self.env.now))

    def do_cardio(self, id):
        yield self.env.timeout(CARDIO_TIME)
        print ('Customer {0} leaving cardio at {1:2f}'.format(id, self.env.now))

    def ride_bike(self, id):
        yield self.env.timeout(BIKE_TIME)
        print ('Customer {0} leaving bike at {1:2f}'.format(id, self.env.now))

    def weight_machines(self, id):
        yield self.env.timeout(MACHINE_TIME)
        print ('Customer {0} leaving machines at {1:2f}'.format(id, self.env.now))

    def bench_press(self, id):
        yield self.env.timeout(BENCH_TIME)
        print ('Customer {0} leaving bench at {1:2f}'.format(id, self.env.now))
