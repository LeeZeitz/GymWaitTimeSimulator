import numpy as np

b = 1/10
b = 10

seed = 5

stream = np.random.RandomState(int(seed))

for i in range(14):
    print (stream.exponential(b))

print ()

for i in range(12):
    print (stream.normal(5))