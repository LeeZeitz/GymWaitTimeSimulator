

def one():
    print ('one')

def two():
    print ('two')

calls = [one, two]

for i in calls:
    i()