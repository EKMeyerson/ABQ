# Novelty Search implemented on top of DNN EA

import DNN
import time
import ConfigParser
import sys
import numpy as np
import random
from copy import deepcopy

class NoveltySearch:
    
    def __init__(self,num_input,num_output,config):
        
        self.padd = config.getfloat('novelty','padd')
        self.k = config.getint('novelty','k')
        self.archive_size = config.getint('novelty','archive_size')
        self.ea = DNN.DNN(num_input,num_output,config)
        self.archive = []
        self.current_behaviors = [None]*self.ea.population_size
    
    def get_best_fitness(self): return self.ea.get_best_fitness()

    def get_avg_fitness(self): return self.ea.get_avg_fitness()

    def score(self,b1,b2): raise NotImplementedError
            
    def novelty(self,b):
        if len(self.archive) > 0:
            neighbors = sorted([self.score(b,b0) for b0 in \
                        (self.archive+self.current_behaviors)])[:self.k]
            return sum(neighbors)
        else: return 10

    def get_population_size(self):
        return self.ea.get_population_size()

    def get_indiv(self,i):
        return self.ea.population[i]

    def eval_indiv(self,i,b):
        self.current_behaviors[i] = deepcopy(b)

    def next_gen(self):
        for i in range(self.ea.population_size):
            f = self.novelty(self.current_behaviors[i])
            self.ea.fitness[i] = f
        if random.random() >= self.padd:
            self.archive.append(self.current_behaviors[i])
        if len(self.archive) > self.archive_size: 
            del self.archive[0]

        self.ea.next_gen()

if __name__=='__main__':
    # Test XOR evolution
    data = ((0,0,0),(0,1,1),(1,0,1),(1,1,0))

    # read settings file
    config = ConfigParser.ConfigParser()
    config.read(sys.argv[1])

    ne = Novelty_Search(config)
    print 'loaded'

    best_net = None
    best_fitness = 0
    generation = 0
    evolving = True
    while evolving:
        for i in range(ne.ea.population_size):
            net = ne.get_indiv(i)
            b = []
            f = 0
            for d in data:
                net.flush()
                net.setInput(d[:2])
                net.step()
                net.step()
                output = net.readOutput()
                f += 1 - abs(output - d[2])
                b.append(float(output[0]))
            if f > best_fitness:
                best_fitness = f
                best_net = net
                print 'New Best: ' + str(f)
                visualize(net)
                if f > 3.8:
                    evolving = False
            ne.eval_indiv(i,b)
        ne.next_gen()
        generation += 1
        print generation
    
    print 'Task Complete.'
    visualize(best_net)
    print best_net.weights
    for d in data:
        best_net.flush()
        best_net.setInput(d[:2])
        print best_net.activation
        best_net.step()
        print best_net.activation
        best_net.step()
        print best_net.activation
        output = best_net.readOutput()
        print d,output

    time.sleep(100)

