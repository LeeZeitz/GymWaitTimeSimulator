import simpy
from gym import Gym
import random
import numpy as np
import scipy.stats
import copy
import sys

'''
    Hours: 
    Sunday	    8a.m.–7p.m.
    Monday	    5:45a.m.–10p.m.
    Tuesday	    5:45a.m.–10p.m.
    Wednesday	5:45a.m.–10p.m.
    Thursday	5:45a.m.–10p.m.
    Friday	    5:45a.m.–10p.m.
    Saturday	8a.m.–7p.m.

    6510 minutes/week
    26040 minutes/month
'''

# Number of each type of equipment for each simulation
input_params = [
    # Original
    {
        'number_of_free_weights': 8,
        'number_of_racks': 2,
        'number_of_machines': 7,
        'number_of_bikes': 50,
        'number_of_cardio': 20,
        'number_of_benches': 2,
        'changed': 'original'
    },
    # Change cardio
    {
        'number_of_free_weights': 8,
        'number_of_racks': 3,
        'number_of_machines': 7,
        'number_of_bikes': 50,
        'number_of_cardio': 14,
        'number_of_benches': 2,
        'changed': 'cardio'
    },
    # Change free weights
    {
        'number_of_free_weights': 7,
        'number_of_racks': 3,
        'number_of_machines': 7,
        'number_of_bikes': 50,
        'number_of_cardio': 20,
        'number_of_benches': 2,
        'changed': 'free weights'
    },
    # Change bikes
    {
        'number_of_free_weights': 8,
        'number_of_racks': 3,
        'number_of_machines': 7,
        'number_of_bikes': 38,
        'number_of_cardio': 20,
        'number_of_benches': 2,
        'changed': 'bikes'
    },
    # Change machines
    {
        'number_of_free_weights': 8,
        'number_of_racks': 3,
        'number_of_machines': 5,
        'number_of_bikes': 50,
        'number_of_cardio': 20,
        'number_of_benches': 2,
        'changed': 'machines'
    },
    # Change Benches
    {
        'number_of_free_weights': 8,
        'number_of_racks': 3,
        'number_of_machines': 7,
        'number_of_bikes': 50,
        'number_of_cardio': 20,
        'number_of_benches': 1,
        'changed': 'benches'
    }
]

SIM_TIME = 26040
INTERARRAVAL_TIME = 3.5
NUMBER_OF_SIMULATIONS = 5
NUMBER_OF_CUSTOMERS = [0 for i in range(NUMBER_OF_SIMULATIONS)]

# Each sublist in this list is Ybar for a simulation
total_average_wait_times = [[] for i in range(NUMBER_OF_SIMULATIONS)]
wait_times_dict = [{
    'cardio_wait_time': 0,
    'bench_wait_time': 0,
    'machines_wait_time': 0,
    'rack_wait_time': 0,
    'free_weights_wait_time': 0
} for i in range(NUMBER_OF_SIMULATIONS)]


def weights(id, env, gym, wait_times_dict):
    arrive_time = env.now
    with gym.weights.request() as request:
        yield request
        #print ('Customer {0} starts using free weights at {1:2f}'.format(id, env.now))
        start_time = env.now
        wait_times_dict['free_weights_wait_time'] += start_time - arrive_time
        yield env.process(gym.lift_free_weights(id))
        #print ('Customer {0} finished using free weights at {1:2f}'.format(id, env.now))

def cardio(id, env, gym, wait_times_dict):
    arrive_time = env.now
    with gym.cardio.request() as request:
        yield request
        #print ('Customer {0} starts using cardio at {1:2f}'.format(id, env.now))
        start_time = env.now
        wait_times_dict['cardio_wait_time'] += start_time - arrive_time
        yield env.process(gym.do_cardio(id))
        #print ('Customer {0} finished doing cardio at {1:2f}'.format(id, env.now))

def racks(id, env, gym, wait_times_dict):
    arrive_time = env.now
    with gym.racks.request() as request:
        yield request
        #print ('Customer {0} starts using rack at {1:2f}'.format(id, env.now))
        start_time = env.now
        wait_times_dict['rack_wait_time'] += start_time - arrive_time
        yield env.process(gym.use_rack(id))
        #print ('Customer {0} finished using rack at {1:2f}'.format(id, env.now))

def machines(id, env, gym, wait_times_dict):
    arrive_time = env.now
    with gym.machines.request() as request:
        yield request
        #print ('Customer {0} starts using weight machines at {1:2f}'.format(id, env.now))
        start_time = env.now
        wait_times_dict['machines_wait_time'] += start_time - arrive_time
        yield env.process(gym.weight_machines(id))
        #print ('Customer {0} finished using weight machines at {1:2f}'.format(id, env.now))

def benches(id, env, gym, wait_times_dict):
    arrive_time = env.now
    with gym.benches.request() as request:
        yield request
        #print ('Customer {0} starts using a bench at {1:2f}'.format(id, env.now))
        start_time = env.now
        wait_times_dict['bench_wait_time'] += start_time - arrive_time
        yield env.process(gym.bench_press(id))
        #print ('Customer {0} finished using a bench at {1:2f}'.format(id, env.now))

weight_activities = [
    {'activity': weights, 'probability': 30}, 
    {'activity': racks, 'probability': 25}, 
    {'activity': machines, 'probability': 25}, 
    {'activity': benches, 'probability': 20}
]

# Weights:  90% -> 45
# racks:    40% -> 20
# machines: 30% -> 15
# benches:  40% -> 20

def get_weight_activity(activities, stream):
    x = stream.randint(0, 100)
    prob = 0
    for i, activity in enumerate(activities):
        prob += activity['probability'] 
        if x < prob:
            del activities
            return activity['activity']
    print ('ERROR, prob = {0}'.format(prob))    


def athlete(env, id, gym, wait_times_dict, stream):
    #print('Customer {0} has arrived at the gym at {1:2f}'.format(id, env.now))

    r = stream.randint(0, 100)

    # Athlete does cardio (56% of them do)
    if r < 58:

        yield env.process(cardio(id, env, gym, wait_times_dict))

        # Lift weights as well as doing cardio (32% do)
        if r < 32:
            activities = copy.deepcopy(weight_activities)
            # Do two weight lifting activities
            for i in range(2):
                activity = get_weight_activity(activities, stream)
                yield env.process(activity(id, env, gym, wait_times_dict))
            
   
    # Athlete only lifts weights, no cardio (42% of them do)
    else:
        activities = copy.deepcopy(weight_activities)
        # Do three weight lifting activities
        '''
        i = stream.randint(0, 3)
        del activities[i]

        for activity in activities:
            yield env.process(activity(id, env, gym, wait_times))
        '''
        for i in range(3):
            activity = get_weight_activity(activities, stream)
            yield env.process(activity(id, env, gym, wait_times_dict))


# Instantiates a Gym object and pre-fills it with athletes. 
# Parameters:
#       env:                    simulation environment
#       stream:                 a random number stream
#       NUMBER_OF_CUSTOMERS:    an array containing the number of customers for each sumulation run
#       n:                      an integer specifying which simulation run this is
#       session:                dictionary of input parameter values {number_of_free_weights, number_of_racks, number_of_machines, number_of_bikes, number_of_cardio, number_of_benches}
#
def setup(env, stream, NUMBER_OF_CUSTOMERS, n, session):
    gym = Gym(env, stream, session)
    for i in range(5):
        env.process(athlete(env, i, gym, wait_times_dict[n], stream))
        NUMBER_OF_CUSTOMERS[n] += 1

    while True:
        yield env.timeout(stream.exponential(INTERARRAVAL_TIME))
        i += 1
        NUMBER_OF_CUSTOMERS[n] += 1
        env.process(athlete(env, i, gym, wait_times_dict[n], stream))


# Calculates and returns the standard deviation of a given sequence of numbers.
# *Note* - The behavior of this function is undefined if a sequence of non-number types is provided
# Parameters:
#       sequence:   a list of numbers
#
def standard_deviation(sequence):
    sd = 0
    mean = sum(sequence) / len(sequence)

    for i, element in enumerate(sequence):
        sd += (element ** 2) - ((i + 1) * (mean ** 2))

    sd /= (len(sequence) - 1)
    return sd
    

# Calculates the confidence interval of a given set of data with a given confidence
# Parameters:
#       confidence:     (float) decimal from 0 to 1 specifying confidence level to calculate interval with
#       data:           (list) numerical data to calculate confidence interval on
#
def confidence_interval(confidence, data):
    float_data = np.array(data) * 1.0
    interval = scipy.stats.sem(float_data) * scipy.stats.t.ppf((confidence + 1) / float(2), len(float_data) - 1)
    return interval


def results(num_cust, n):
    total_average_wait_time = sum(wait_times_dict[n].values())/num_cust
    total_average_wait_times[n].append(total_average_wait_time)
    print ()
    print ('Number of Customers: {0}'.format(NUMBER_OF_CUSTOMERS[0]))
    print ('Simulation Length:   {0}'.format(SIM_TIME))
    print ('Average Wait Times: ')
    print ('    Cardio:         {0}'.format(wait_times_dict[n]['cardio_wait_time']/num_cust))
    print ('    Machines:       {0}'.format(wait_times_dict[n]['machines_wait_time']/num_cust))
    print ('    Free Weights:   {0}'.format(wait_times_dict[n]['free_weights_wait_time']/num_cust))
    print ('    Bench:          {0}'.format(wait_times_dict[n]['bench_wait_time']/num_cust))
    print ('    Rack:           {0}'.format(wait_times_dict[n]['rack_wait_time']/num_cust))
    print ('    Per Person:     {0}'.format(total_average_wait_time))


def session_results(n):
    print()
    print('Average Customer Wait Time: {0}'.format())


if __name__ == '__main__':

    try:
        seed = sys.argv[1]
    except:
        seed = input('Please provide a seed: \n')

    if len(sys.argv) < 6:
        print ('need more seeds please')
        exit()

    seeds = sys.argv[1:6]

    for session in input_params:
        print('\n\nSession: {0}'.format(session['changed']))
        for n in range(NUMBER_OF_SIMULATIONS):
            stream = np.random.RandomState(int(seeds[n]))
            env = simpy.Environment()
            env.process(setup(env, stream, NUMBER_OF_CUSTOMERS, n, session))
            env.run(until=SIM_TIME)
            results(NUMBER_OF_CUSTOMERS[n], n)

    print(total_average_wait_times)
    print(wait_times)



