# Novelty Search implemented on top of DNN EA

import dnn
from net_viz import visualize
import time
import ConfigParser
import sys
import numpy as np
import random


class Novelty_Search:
    
    def __init__(self,config):
        
        self.distance_func = config.get('novelty','distance_func')
        self.pmin = config.getfloat('novelty','pmin')
        self.padd = config.getfloat('novelty','padd')
        self.k = config.getint('novelty','k')
        self.archive_size = config.getint('novelty','archive_size')
        self.ea = dnn.DNN(config)
        self.archive = []
        self.current_behaviors = [None]*self.ea.population_size
        
    def dist(self,b1,b2):
        if len(b1) != len(b2):
            #raise Exception('Behavior length mismatch.')
            if len(b1) < len(b2):
                temp = np.zeros(len(b2))
                temp[:len(b1)] = b1[:]
                b1 = temp
            else:
                temp = np.zeros(len(b1))
                temp[:len(b2)] = b2[:]
                b2 = temp
            if len(b1) != len(b2):
                raise Exception('Behavior length mismatch.')
        if self.distance_func == 'hamming':
            return np.sum(np.array(b1)-np.array(b2))
        elif self.distance_func == 'euclidean':
            return np.linalg.norm(np.array(b1)-np.array(b2))
        else: raise Exception('Bad distance metric')
            
    def novelty(self,b):
        if len(self.archive) > 0:
            neighbors = sorted([self.dist(b,b0) for b0 in \
                        (self.archive+self.current_behaviors)])[:self.k]
            #return float(1/self.k)*sum(neighbors)
            return sum(neighbors)
        else: return 10
        
    def get_indiv(self,i):
        return self.ea.population[i]

    def eval_indiv(self,i,b):
        self.current_behaviors[i] = b[:]

    def next_gen(self):
        for i in range(self.ea.population_size):
            f = self.novelty(self.current_behaviors[i])
            self.ea.fitness[i] = f
        if random.random() >= self.padd:
            self.archive.append(self.current_behaviors[i])
        #if f >= self.pmin:
        #    self.archive.append(self.current_behaviors[i])
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

