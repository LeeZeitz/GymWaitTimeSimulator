import simpy
import random
import numpy as np

FREE_WEIGHT_TIME = 26.68
BIKE_TIME = 35.6
CARDIO_TIME = 52.2
MACHINE_TIME = 28.05
RACK_TIME = 16.61
BENCH_TIME = 8.57

# Reps: U ~ [8 - 12]
# Time per rep: [1s - 4s]
# Sets: 3
# Rest Period: normally distributed around 600 seconds per exercise
# Exercises: 6-12

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
        yield self.env.timeout(self.get_exercise_time(5))

    def use_rack(self, id):
        yield self.env.timeout(self.get_exercise_time(3))

    def do_cardio(self, id):
        yield self.env.timeout(self.stream.normal(CARDIO_TIME))

    def ride_bike(self, id):
        yield self.env.timeout(self.stream.normal(BIKE_TIME))

    def weight_machines(self, id):
        yield self.env.timeout(self.get_exercise_time(5))

    def bench_press(self, id):
        yield self.env.timeout(self.get_exercise_time(2))

    
    # Returns a random amount of time a piece of equipment will be in use for
    # Parameters:
    #       number_of_exercises:    (int) the number of exercises to calculate the service time of
    #
    def get_exercise_time(self, number_of_exercises):
        # Initialize equipment_time with 5 minute rest/prep period
        equipment_time = self.stream.normal(600)
        for i in range(number_of_exercises):
            reps = self.stream.randint(8, 12)
            time_per_rep =  self.stream.randint(1, 4)
            equipment_time += reps * time_per_rep
        #print (equipment_time/60)
        return equipment_time/60

