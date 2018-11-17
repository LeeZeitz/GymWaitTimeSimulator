import simpy
from gym import Gym
import random
import numpy as np
import copy

# 50% men and 50% women
# women: 50% use only cardio, 10% use only weights, 40% use both
#           15% use rack
# men: 10% use only cardio, 80% use only weights, 10% use both
            # 60% use racks

SIM_TIME = 1000
INTERARRAVAL_TIME = 10

def weights(id, env, gym):
    with gym.weights.request() as request:
        yield request
        print ('Customer {0} starts using free weights at {1:2f}'.format(id, env.now))
        yield env.process(gym.lift_free_weights(id))
        print ('Customer {0} finished using free weights at {1:2f}'.format(id, env.now))

def cardio(id, env, gym):
    with gym.cardio.request() as request:
        yield request
        print ('Customer {0} starts using cardio at {1:2f}'.format(id, env.now))
        yield env.process(gym.do_cardio(id))
        print ('Customer {0} finished doing cardio at {1:2f}'.format(id, env.now))

def racks(id, env, gym):
    with gym.racks.request() as request:
        yield request
        print ('Customer {0} starts using rack at {1:2f}'.format(id, env.now))
        yield env.process(gym.use_rack(id))
        print ('Customer {0} finished using rack at {1:2f}'.format(id, env.now))

def machines(id, env, gym):
    with gym.machines.request() as request:
        yield request
        print ('Customer {0} starts using weight machines at {1:2f}'.format(id, env.now))
        yield env.process(gym.weight_machines(id))
        print ('Customer {0} finished using weight machines at {1:2f}'.format(id, env.now))

def benches(id, env, gym):
    with gym.machines.request() as request:
        yield request
        print ('Customer {0} starts using a bench at {1:2f}'.format(id, env.now))
        yield env.process(gym.benches(id))
        print ('Customer {0} finished using a bench at {1:2f}'.format(id, env.now))

weight_activities = [weights, racks, machines, benches]



def athlete(env, id, gym):
    print('Customer {0} has arrived at the gym at {1:2f}'.format(id, env.now))

    r = random.randint(0, 100)

    # Athlete does cardio
    if r < 55:
        yield cardio(id, env, gym)

        # Lift weights as well as doing cardio
        if r < 25:
            activities = copy.deepcopy(weight_activities)
            # Do two weight lifting activities
            i = random.randint(0, 3)
            j = i
            while j == i:
                j = random.randint(0, 3)

            yield activities[i](id, env, gym)
            yield activities[j](id, env, gym)

    # Athlete only lifts weights
    else:
        activities = copy.deepcopy(weight_activities)
        # Do three weight lifting activities
        i = random.randint(0, 3)
        del activities[i]

        for activity in activities:
            yield activity(id, env, gym)


def setup(env):
    gym = Gym(env)
    for i in range(4):
        env.process(athlete(env, i, gym))

    while True:
        yield env.timeout(random.randint(INTERARRAVAL_TIME - 2, INTERARRAVAL_TIME + 2))
        i += 1
        env.process(athlete(env, i, gym))


if __name__ == '__main__':

    env = simpy.Environment()
    env.process(setup(env))

    env.run(until=SIM_TIME)

