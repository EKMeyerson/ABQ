# Direct Encoding of Neural Networks Evolutionary Process (see Mouret)

import RNN
import numpy as np
import random
import copy
import sys
import ConfigParser
import time
from net_viz import visualize

MIN_FITNESS = -1000000

class DNN:

    def __init__(self,num_input,num_output,config):
        # load task parameters
        self.config = config
        self.num_input = num_input
        self.num_output = num_output
        
        # load GA parameters
        self.population_size = config.getint('evolution',
                                'population_size')
        self.add_connection_rate = config.getfloat('evolution',
                                'add_connection_rate')
        self.remove_connection_rate = config.getfloat('evolution',
                                'remove_connection_rate')
        self.add_neuron_rate = config.getfloat('evolution',
                                'add_neuron_rate')
        self.remove_neuron_rate = config.getfloat('evolution',
                                'remove_neuron_rate')
        self.minimum_weight = config.getfloat('evolution',
                                'minimum_weight')
        self.maximum_weight = config.getfloat('evolution',
                                'maximum_weight')
        self.mutation_st_dev = config.getfloat('evolution',
                                'mutation_st_dev')
        self.parent_rate = config.getfloat('evolution',
                                'parent_rate')
        self.num_parents = self.parent_rate*self.population_size
        self.children_per_parent = self.population_size/self.num_parents
        if not self.num_parents.is_integer() \
        or not self.children_per_parent.is_integer():
            raise Exception("Unstable population dynamics.")
        else:
            self.num_parents = int(self.num_parents)
            self.children_per_parent = int(self.children_per_parent)#-1

        
        # initialize population
        self.population = [self.random_indiv() for i in range(self.population_size)]
        self.fitness = np.empty(self.population_size)

        # initialize status
        self.best_net_so_far = None
        self.best_fitness_so_far = MIN_FITNESS
        self.best_curr_fitness = MIN_FITNESS
    
    def random_indiv(self):
        indiv = rnn.RNN(self.num_input,self.num_output,self.config)
        indiv.initializePerceptron()
        for (u,v) in indiv.present_connections.union(indiv.bias_connections):
            indiv.weights[u,v] = np.random.uniform(-1,1)
        return indiv
    
    def get_population_size(self):
        return self.population_size

    def get_indiv(self,i):
        return self.population[i]

    def eval_indiv(self,i,f):
        self.fitness[i] = f
        if f > self.best_curr_fitness:
            self.best_curr_fitness = f
            if f > self.best_fitness_so_far:
                self.best_fitness_so_far = f
                self.best_net_so_far = copy.deepcopy(self.population[i])

    def mutate(self,original):
        #indivs should just be weight array
        indiv = copy.deepcopy(original) # initialize mutant
        indiv.flush()

        # add neuron
        if np.random.random() < self.add_neuron_rate \
        and len(indiv.present_connections) > 0:
            indiv.addHidden()
            (u,v) = random.choice(tuple(indiv.present_connections))
            w = indiv.weights[u,v]
            indiv.removeConnection(u,v)
            indiv.addConnection(u,indiv.numNodes-1)
            indiv.setWeight(u,indiv.numNodes-1,w)
            indiv.addConnection(indiv.numNodes-1,v)
            indiv.setWeight(indiv.numNodes-1,v,w)

        # remove neuron
        if np.random.random() < self.remove_neuron_rate \
        and indiv.numNodes > 1+indiv.numInput+indiv.numOutput:
            indiv.removeHidden(np.random.randint(1+indiv.numInput+indiv.numOutput,
                                                    indiv.numNodes))

        # add connection
        if np.random.random() < self.add_connection_rate \
        and len(indiv.absent_connections) > 0:
            indiv.addConnection(*random.choice(tuple(indiv.absent_connections)))

        # remove connection
        if np.random.random() < self.remove_connection_rate \
        and len(indiv.present_connections) > 0:
            indiv.removeConnection(*random.choice(tuple(indiv.present_connections)))
        # mutate weights (can optimize)
        for (u,v) in indiv.present_connections.union(indiv.bias_connections):
            w = indiv.weights[u,v]+self.mutation_st_dev*np.random.standard_cauchy()
            indiv.weights[u,v] = min(5,max(-5,w))
        
        return indiv


    def next_gen(self):
        # sort individuals by fitness
        parents = self.fitness.argsort()[-self.num_parents:]
        
        # top individuals repopulate with mutants
        new_pop = []
        for i in parents:
            #new_pop.append(copy.deepcopy(self.population[i]))
            for c in range(self.children_per_parent):
                new_pop.append(self.mutate(self.population[i]))
        self.population = new_pop

        self.best_curr_fitness = MIN_FITNESS


if __name__=='__main__':
    # Test XOR evolution
    data = ((0,0,0),(0,1,1),(1,0,1),(1,1,0))

    # read settings file
    config = ConfigParser.ConfigParser()
    config.read(sys.argv[1])

    ne = DNN(config)
    print 'loaded'

    best_net = None
    best_fitness = 0
    generation = 0
    evolving = True
    while evolving:
        for i in range(ne.population_size):
            net = ne.get_indiv(i)
            f = 0
            #print 'Output:'
            for d in data:
                net.flush()
                net.setInput(d[:2])
                net.step()
                net.step()
                output = net.readOutput()
                #print output
                f += 1 - abs(output - d[2])
            if f >= best_fitness:
                best_fitness = f
                best_net = net
                print 'New Best: ' + str(f)
                visualize(net)
                if f > 3.8:
                    evolving = False
            ne.eval_indiv(i,f)
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
  
        
