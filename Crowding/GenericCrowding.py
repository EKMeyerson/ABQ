"""
Generic Crowding algorithm;
for replicating Tartarus results
"""

import sys
sys.path.append('..')
sys.path.append('../Tartarus')
import numpy as np
import FCFTRNN as nn

MIN_SCORE = -1000000
MAX_DISTANCE = 1000000

def hamming(b1,b2):
    return (b1 != b2).sum()

class GenericCrowding:
    
    def __init__(self,task,config):
        self.task = task
        self.config = config
        self.num_iterations = config.getint('evolution','num_iterations')
        self.curr_iteration = 0
        self.mutationRate = config.getfloat('evolution','mutation_rate')
        self.tournamentSize = config.getint('evolution','tournament_size')
        self.populationSize = config.getint('evolution','population_size')
        self.population = [self.random_indiv() for i in range(self.populationSize)]
        for indiv in self.population: self.evaluate(indiv)
        self.total_fitness = float(sum(indiv.fitness for indiv in self.population))
        self.best_fitness = max(indiv.fitness for indiv in self.population)

    def done(self):
        return self.curr_iteration == self.num_iterations

    def step(self):
        parentA = self.tournamentSelect()
        parentB = self.tournamentSelect()
        childA,childB = self.crossover(parentA,parentB)
        self.mutate(childA)
        self.evaluate(childA)
        self.mutate(childB)
        self.evaluate(childB)
        loserA = self.crowdingSelect(childA)
        loserB = self.crowdingSelect(childB)
        self.replace(loserA,childA)
        self.replace(loserB,childB)
        self.curr_iteration += 1

    def tournamentSelect(self):
        max_score = MIN_SCORE
        for i in range(self.tournamentSize):
            j = np.random.randint(self.populationSize)
            indiv = self.population[j]
            score = indiv.fitness
            if score > max_score:
                max_score = score
                winner = indiv
                index = j
        return winner

    def crossover(self,parentA,parentB):
        parentAgenome = parentA.brain.weights.flatten()
        parentBgenome = parentB.brain.weights.flatten()
        childAgenome = np.zeros(parentAgenome.size)
        childBgenome = np.zeros(parentBgenome.size)
        point = np.random.randint(parentAgenome.size)
        childAgenome[:point] = parentAgenome[:point]
        childAgenome[point:] = parentBgenome[point:]
        childBgenome[:point] = parentBgenome[:point]
        childBgenome[point:] = parentAgenome[point:]
        childA = Individual(self.config)
        childB = Individual(self.config)
        childA.brain.weights = childAgenome.reshape(childA.brain.weights.shape)
        childB.brain.weights = childBgenome.reshape(childB.brain.weights.shape)
        return childA,childB

    def mutate(self,child):
        for u in range(child.brain.numNodes):
            for v in range(child.brain.numUnits):
                if np.random.random() < self.mutationRate:
                    child.brain.weights[u,v] = np.random.uniform(-10,10)

    def evaluate(self,indiv):
        task = self.task
        task.reset()
        indiv.brain.flush()
        b = []
        sensors = task.inputs
        while not task.done():
            #task.update_inputs()
            indiv.brain.setInput(sensors)
            indiv.brain.step()
            action = np.argmax(indiv.brain.readOutput())
            task.act(action)
            #b.extend(list(sensors))
            b.append(action)
            if task.trial_done(): indiv.brain.flush()
        indiv.fitness = task.get_fitness()
        indiv.replacementBehavior = np.array(b)

    def crowdingSelect(self,child):
        min_distance = MAX_DISTANCE
        for i in range(self.tournamentSize):
            j = np.random.randint(self.populationSize)
            distance = hamming(child.replacementBehavior,
                               self.population[j].replacementBehavior)
            if distance < min_distance:
                min_distance = distance
                loser = j
        return loser

    def replace(self,loser,child):
        self.total_fitness -= self.population[loser].fitness
        self.total_fitness += child.fitness
        self.population[loser] = child
        if child.fitness > self.best_fitness:
            self.best_fitness = child.fitness

    def random_indiv(self):
        indiv = Individual(self.config)
        indiv.brain.weights[:] = np.random.uniform(-10,10,indiv.brain.weights.shape)
        return indiv

    def get_best_fitness(self): 
        return self.best_fitness

    def get_avg_fitness(self): 
        return self.total_fitness / self.populationSize


class Individual:
    
    def __init__(self,config):

        self.brain = nn.FCFTRNN(config)
        self.fitness = None
        self.selectionBehavior = None
        self.replacementBehavior = None

        









