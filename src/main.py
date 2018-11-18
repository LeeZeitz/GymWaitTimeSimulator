import simpy
from gym import Gym
import random
import numpy as np
import copy
import sys

# 50% men and 50% women
# women: 50% use only cardio, 10% use only weights, 40% use both
#           15% use rack
# men: 10% use only cardio, 80% use only weights, 10% use both
            # 60% use racks

SIM_TIME = 10000
INTERARRAVAL_TIME = 5
NUMBER_OF_SIMULATIONS = 5
NUMBER_OF_CUSTOMERS = [0 for i in range(NUMBER_OF_SIMULATIONS)]

wait_times = [{
    'cardio_wait_time': 0,
    'bench_wait_time': 0,
    'machines_wait_time': 0,
    'rack_wait_time': 0,
    'free_weights_wait_time': 0
} for i in range(NUMBER_OF_SIMULATIONS)]

def weights(id, env, gym, wait_times):
    arrive_time = env.now
    with gym.weights.request() as request:
        yield request
        #print ('Customer {0} starts using free weights at {1:2f}'.format(id, env.now))
        start_time = env.now
        wait_times['free_weights_wait_time'] += start_time - arrive_time
        yield env.process(gym.lift_free_weights(id))
        #print ('Customer {0} finished using free weights at {1:2f}'.format(id, env.now))

def cardio(id, env, gym, wait_times):
    arrive_time = env.now
    with gym.cardio.request() as request:
        yield request
        #print ('Customer {0} starts using cardio at {1:2f}'.format(id, env.now))
        start_time = env.now
        wait_times['cardio_wait_time'] += start_time - arrive_time
        yield env.process(gym.do_cardio(id))
        #print ('Customer {0} finished doing cardio at {1:2f}'.format(id, env.now))

def racks(id, env, gym, wait_times):
    arrive_time = env.now
    with gym.racks.request() as request:
        yield request
        #print ('Customer {0} starts using rack at {1:2f}'.format(id, env.now))
        start_time = env.now
        wait_times['rack_wait_time'] += start_time - arrive_time
        yield env.process(gym.use_rack(id))
        #print ('Customer {0} finished using rack at {1:2f}'.format(id, env.now))

def machines(id, env, gym, wait_times):
    arrive_time = env.now
    with gym.machines.request() as request:
        yield request
        #print ('Customer {0} starts using weight machines at {1:2f}'.format(id, env.now))
        start_time = env.now
        wait_times['machines_wait_time'] += start_time - arrive_time
        yield env.process(gym.weight_machines(id))
        #print ('Customer {0} finished using weight machines at {1:2f}'.format(id, env.now))

def benches(id, env, gym, wait_times):
    arrive_time = env.now
    with gym.benches.request() as request:
        yield request
        #print ('Customer {0} starts using a bench at {1:2f}'.format(id, env.now))
        start_time = env.now
        wait_times['bench_wait_time'] += start_time - arrive_time
        yield env.process(gym.bench_press(id))
        #print ('Customer {0} finished using a bench at {1:2f}'.format(id, env.now))

weight_activities = [weights, racks, machines, benches]



def athlete(env, id, gym, wait_times, stream):
    #print('Customer {0} has arrived at the gym at {1:2f}'.format(id, env.now))

    r = stream.randint(0, 100)

    # Athlete does cardio (56% of them do)
    if r < 58:

        yield env.process(cardio(id, env, gym, wait_times))

        # Lift weights as well as doing cardio (32% do)
        if r < 32:
            activities = copy.deepcopy(weight_activities)
            # Do two weight lifting activities
            i = stream.randint(0, 3)
            j = i
            while j == i:
                j = stream.randint(0, 3)

            yield env.process(activities[i](id, env, gym, wait_times))
            yield env.process(activities[j](id, env, gym, wait_times))
   
    # Athlete only lifts weights, no cardio (42% of them do)
    else:
        activities = copy.deepcopy(weight_activities)
        # Do three weight lifting activities
        i = stream.randint(0, 3)
        del activities[i]

        for activity in activities:
            yield env.process(activity(id, env, gym, wait_times))


def setup(env, stream, NUMBER_OF_CUSTOMERS, n):
    gym = Gym(env, stream)
    for i in range(2):
        env.process(athlete(env, i, gym, wait_times[n], stream))
        NUMBER_OF_CUSTOMERS[n] += 1

    while True:
        yield env.timeout(stream.exponential(INTERARRAVAL_TIME))
        i += 1
        NUMBER_OF_CUSTOMERS[n] += 1
        env.process(athlete(env, i, gym, wait_times[n], stream))


def results(num_cust, n):
    print ()
    print ('Number of Customers: {0}'.format(NUMBER_OF_CUSTOMERS[0]))
    print ('Simulation Length:   {0}'.format(SIM_TIME))
    print ('Average Wait Times: ')
    print ('    Cardio:         {0}'.format(wait_times[n]['cardio_wait_time']/num_cust))
    print ('    Machines:       {0}'.format(wait_times[n]['machines_wait_time']/num_cust))
    print ('    Free Weights:   {0}'.format(wait_times[n]['free_weights_wait_time']/num_cust))
    print ('    Bench:          {0}'.format(wait_times[n]['bench_wait_time']/num_cust))
    print ('    Rack:           {0}'.format(wait_times[n]['rack_wait_time']/num_cust))
    print ()


if __name__ == '__main__':

    try:
        seed = sys.argv[1]
    except:
        seed = input('Please provide a seed: \n')

    if len(sys.argv) < 6:
        print ('need more seeds please')
        exit()

    seeds = sys.argv[1:6]

    print (wait_times)


    for n in range (NUMBER_OF_SIMULATIONS):
        stream = np.random.RandomState(int(seeds[n]))
        env = simpy.Environment()
        env.process(setup(env, stream, NUMBER_OF_CUSTOMERS, n))
        env.run(until=SIM_TIME)
        results(NUMBER_OF_CUSTOMERS[n], n)



