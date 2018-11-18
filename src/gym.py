import simpy
import random
import numpy as np

NUMBER_OF_FREE_WEIGHTS = 5
NUMBER_OF_RACKS = 2
NUMBER_OF_MACHINES = 3
NUMBER_OF_BIKES = 50
NUMBER_OF_CARDIO = 20
NUMBER_OF_BENCHES = 2

FREE_WEIGHT_TIME = 30
BIKE_TIME = 35.6
CARDIO_TIME = 52.2
MACHINE_TIME = 28.05
RACK_TIME = 12.61
BENCH_TIME = 8.57

class Gym(object):

    def __init__(self, env, stream):
        self.env = env
        self.stream = stream
        self.weights = simpy.Resource(env, capacity=NUMBER_OF_FREE_WEIGHTS)
        self.racks = simpy.Resource(env, capacity=NUMBER_OF_RACKS)
        self.machines = simpy.Resource(env, capacity=NUMBER_OF_MACHINES)
        self.cardio = simpy.Resource(env, capacity=NUMBER_OF_CARDIO)
        self.bikes = simpy.Resource(env, capacity=NUMBER_OF_BIKES)
        self.benches = simpy.Resource(env, capacity=NUMBER_OF_BENCHES)

    
    def lift_free_weights(self, id):
        yield self.env.timeout(self.stream.exponential(FREE_WEIGHT_TIME))

    def use_rack(self, id):
        yield self.env.timeout(self.stream.exponential(RACK_TIME))

    def do_cardio(self, id):
        yield self.env.timeout(self.stream.exponential(CARDIO_TIME))

    def ride_bike(self, id):
        yield self.env.timeout(self.stream.exponential(BIKE_TIME))

    def weight_machines(self, id):
        yield self.env.timeout(self.stream.exponential(MACHINE_TIME))

    def bench_press(self, id):
        yield self.env.timeout(self.stream.exponential(BENCH_TIME))