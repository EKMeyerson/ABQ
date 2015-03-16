""" Generic behavior extraction functions """

import random

# h is complete sensory-action history of an agent
# f is fitness

def eventCounts(f,h,salientEvents):
    b = [0]*len(salientEvents)
    for event in h:
        if event in salientEvents:
            b[salientEvents[event]]+=1
    return b

def sensoryActionHistory(f,h,none):
    b = []
    for event in h:
        for subevent in event:
            for item in subevent:
                b.append(item)
    return b

def actionHistoy(f,h,none):
    b = []
    for event in h:
        for item in event[1]:
            b.append(item)
    return b

def fitness(f,h,none): return f

def random(f,h,none): return random.random()
