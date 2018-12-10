import simpy
from gym import Gym
import random
import numpy as np
import scipy.stats
import copy
import sys
import matplotlib.pyplot as plt
import csv

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
    338520 minutes/year
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
    }]
'''
    ,
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
'''

labels = (
    'original',
    'cardio',
    'free weights',
    'bikes',
    'machines'
)


SIM_TIME = 338520
INTERARRAVAL_TIME = 3.62
NUMBER_OF_SIMULATIONS = 10
NUMBER_OF_CUSTOMERS = [0 for i in range(NUMBER_OF_SIMULATIONS)]

# Each sublist in this list is Ybar for a simulation
total_average_wait_times = [[] for i in range(NUMBER_OF_SIMULATIONS)]
wait_times_dict = [{
    'cardio_wait_time': [],
    'bench_wait_time': [],
    'machines_wait_time': [],
    'rack_wait_time': [],
    'free_weights_wait_time': []
} for i in range(NUMBER_OF_SIMULATIONS)]

sim_averages = [[] for i in range(len(input_params))]
sim_vars = [[] for i in range(len(input_params))]

def weights(id, env, gym, wait_times_dict):
    arrive_time = env.now
    with gym.weights.request() as request:
        yield request
        #print ('Customer {0} starts using free weights at {1:2f}'.format(id, env.now))
        start_time = env.now
        wait_times_dict['free_weights_wait_time'].append(start_time - arrive_time)
        yield env.process(gym.lift_free_weights(id))
        #print ('Customer {0} finished using free weights at {1:2f}'.format(id, env.now))

def cardio(id, env, gym, wait_times_dict):
    arrive_time = env.now
    with gym.cardio.request() as request:
        yield request
        #print ('Customer {0} starts using cardio at {1:2f}'.format(id, env.now))
        start_time = env.now
        wait_times_dict['cardio_wait_time'].append(start_time - arrive_time)
        yield env.process(gym.do_cardio(id))
        #print ('Customer {0} finished doing cardio at {1:2f}'.format(id, env.now))

def racks(id, env, gym, wait_times_dict):
    arrive_time = env.now
    with gym.racks.request() as request:
        yield request
        #print ('Customer {0} starts using rack at {1:2f}'.format(id, env.now))
        start_time = env.now
        wait_times_dict['rack_wait_time'].append(start_time - arrive_time)
        yield env.process(gym.use_rack(id))
        #print ('Customer {0} finished using rack at {1:2f}'.format(id, env.now))

def machines(id, env, gym, wait_times_dict):
    arrive_time = env.now
    with gym.machines.request() as request:
        yield request
        #print ('Customer {0} starts using weight machines at {1:2f}'.format(id, env.now))
        start_time = env.now
        wait_times_dict['machines_wait_time'].append(start_time - arrive_time)
        yield env.process(gym.weight_machines(id))
        #print ('Customer {0} finished using weight machines at {1:2f}'.format(id, env.now))

def benches(id, env, gym, wait_times_dict):
    arrive_time = env.now
    with gym.benches.request() as request:
        yield request
        #print ('Customer {0} starts using a bench at {1:2f}'.format(id, env.now))
        start_time = env.now
        wait_times_dict['bench_wait_time'].append(start_time - arrive_time)
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


# Prints the simulation results in a nice, readable way
# Parameters:
#       num_cust:   (int) the number of customers served in the simulation    
#       n:          (int) the index in the wait_time_dict for the current simulation
#
def single_sim_results(num_cust, n, i):

    avg_rack_wt = sum(wait_times_dict[n]['rack_wait_time']) / num_cust
    avg_weights_wt = sum(wait_times_dict[n]['free_weights_wait_time']) / num_cust
    avg_cardio_wt = sum(wait_times_dict[n]['cardio_wait_time']) / num_cust
    #avg_bike_wt = sum(wait_times_dict[n]['bike_wait_time']) / num_cust
    avg_bench_wt = sum(wait_times_dict[n]['bench_wait_time']) / num_cust
    avg_machine_wt = sum(wait_times_dict[n]['machines_wait_time']) / num_cust
    avg_person_wt = avg_bench_wt + avg_cardio_wt + avg_machine_wt + avg_rack_wt + avg_weights_wt

    var_rack = np.var(wait_times_dict[n]['rack_wait_time'])
    var_weights = np.var(wait_times_dict[n]['free_weights_wait_time'])
    var_cardio = np.var(wait_times_dict[n]['cardio_wait_time'])
    var_bench = np.var(wait_times_dict[n]['bench_wait_time'])
    var_machine = np.var(wait_times_dict[n]['machines_wait_time'])
    var_person =  var_rack + var_weights + var_cardio + var_bench + var_machine

    '''
    {
        'cardio_wait_time': [],
        'bench_wait_time': [],
        'machines_wait_time': [],
        'rack_wait_time': [],
        'free_weights_wait_time': []
    }

    sim_averages['cardio_wait_time'].append(avg_cardio_wt)
    sim_averages['bench_wait_time'].append(avg_bench_wt)
    sim_averages['machines_wait_time'].append(avg_machine_wt)
    sim_averages['rack_weight_time'].append(avg_rack_wt)
    sim_averages['free_weights_wait_time'].append(avg_weights_wt)
    '''

    sim_averages[i].append(avg_person_wt)
    sim_vars[i].append(var_person)

    print ()
    print ('Number of Customers: {0}'.format(NUMBER_OF_CUSTOMERS[0]))
    print ('Simulation Length:   {0}'.format(SIM_TIME))
    print ('Average Wait Times: ')
    print ('    Cardio:         {0}'.format(avg_cardio_wt))
    print ('    Machines:       {0}'.format(avg_machine_wt))
    print ('    Free Weights:   {0}'.format(avg_weights_wt))
    print ('    Bench:          {0}'.format(avg_bench_wt))
    print ('    Rack:           {0}'.format(avg_rack_wt))
    print ('    Per Person:     {0}'.format(avg_person_wt))


# Calculates the confidence interval of a given set of data with a given confidence
# Parameters:
#       confidence:     (float) decimal from 0 to 1 specifying confidence level to calculate interval with
#
def confidence_interval(confidence, sd, n):
    t = scipy.stats.t.ppf((confidence + 1) / float(2), n - 1)
    se = sd / (n**0.5)
    interval = t * se
    return interval


def results(cis):
    colors = ['red', 'blue', 'green', 'purple', 'orange', 'brown', 'yellow', 'black', 'grey']

    '''
    for i, ci in enumerate(cis):
        plotline, caplines, barlinecols = plt.errorbar([j for j in range(NUMBER_OF_SIMULATIONS)], sim_averages[i], yerr=ci, ecolor=colors[i])
        plotline.set_color(colors[i])
        plotlines.append(plotline)
    plt.ylim(bottom=0)
    plt.title('Average Gym Waiting Time When Replacing Equip. with Rack')
    plt.ylabel('Waiting Time (minutes)')
    plt.xlabel('Simulation Number')
    plt.legend(tuple(plotlines), labels)
    plt.show()
    '''

    plt.ylim(bottom=0)
    plt.ylabel('Waiting Time (minutes)')
    plt.xlabel('Simulation Number')

    plotline, caplines, barlinecols = plt.errorbar([j for j in range(NUMBER_OF_SIMULATIONS)], sim_averages[0], yerr=cis[0], ecolor=colors[0])
    plotline.set_color(colors[0])
    plotlines.append(plotline)

    for i, ci in enumerate(cis):
        plotlines = []
        if i != 0:
            plotline, caplines, barlinecols = plt.errorbar([j for j in range(NUMBER_OF_SIMULATIONS)], sim_averages[i], yerr=ci, ecolor=colors[i])
            plotline.set_color(colors[i])
            plotlines.append(plotline)

            print (plotlines)

            plt.title('Average Gym Waiting Time When Replacing {0} with Rack'.format(labels[i]))
            plt.legend(tuple(plotlines), [labels[0], labels[i]])
            
            plt.show()
            plotlines.pop()


if __name__ == '__main__':

    try:
        seed = sys.argv[1]
    except:
        seed = input('Please provide a seed: \n')

    if len(sys.argv) < 6:
        print ('need more seeds please')
        exit()

    seeds = sys.argv[1:]

    with open('results.csv', 'w',  newline='') as csv_file:

        # Run NUMBER_OF_SIMULATION simulations for each configuration of equipment parameters
        for i, session in enumerate(input_params):
            # Reset waiting_times_dict to get rid of results from last configuration
            wait_times_dict = [{
                'cardio_wait_time': [],
                'bench_wait_time': [],
                'machines_wait_time': [],
                'rack_wait_time': [],
                'free_weights_wait_time': []
            } for i in range(NUMBER_OF_SIMULATIONS)]

            print('\n\nSession: {0}'.format(session['changed']))
            # Run simulation NUMBER_OF_SIMULATIONS times
            for n in range(NUMBER_OF_SIMULATIONS):
                stream = np.random.RandomState(int(seeds[n]))
                env = simpy.Environment()
                env.process(setup(env, stream, NUMBER_OF_CUSTOMERS, n, session))
                env.run(until=SIM_TIME)
                single_sim_results(NUMBER_OF_CUSTOMERS[n], n, i)

        # After simulation has run all times for a given configuration, calculate and store ci

        print (sim_averages)

        cis = []

        for sim_average in sim_averages:
            writer = csv.writer(csv_file)
            writer.writerow(sim_average)
            average_wait_time = np.mean(sim_average)
            average_var = np.var(sim_average)
            cis.append(confidence_interval(0.95, average_var**0.5, len(sim_average)))

        print (cis)

        results(cis)



