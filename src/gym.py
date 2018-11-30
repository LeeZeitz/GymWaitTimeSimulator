import simpy
import random
import numpy as np

FREE_WEIGHT_TIME = 26.68
BIKE_TIME = 35.6
CARDIO_TIME = 52.2
MACHINE_TIME = 28.05
RACK_TIME = 16.61
BENCH_TIME = 8.57

class Gym(object):

    def __init__(self, env, stream, session):
        self.env = env
        self.stream = stream
        self.weights = simpy.Resource(env, capacity=session['number_of_free_weights'])
        self.racks = simpy.Resource(env, capacity=session['number_of_racks'])
        self.machines = simpy.Resource(env, capacity=session['number_of_machines'])
        self.cardio = simpy.Resource(env, capacity=session['number_of_cardio'])
        self.bikes = simpy.Resource(env, capacity=session['number_of_bikes'])
        self.benches = simpy.Resource(env, capacity=session['number_of_benches'])

    
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