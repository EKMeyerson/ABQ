""" 
Fully-connected fixed-topology recurrent neural network;
for replicating Tartarus results.
"""

import numpy as np
from scipy.special import expit as sigm
import cPickle

class FCFTRNN:

    def __init__(self, config):
        
        self.numInput = config.getint('network','num_input')
        self.numHidden = config.getint('network','num_hidden')
        self.numOutput = config.getint('network','num_output')
        self.numNodes = 1 + self.numInput + self.numHidden + self.numOutput
        self.inputEnd = 1 + self.numInput
        self.numUnits = self.numHidden + self.numOutput
        self.outputStart = 1 + self.numInput + self.numHidden
        self.weights = np.zeros( (self.numNodes, self.numUnits))
        self.activation = np.zeros(self.numNodes)
        self.activation[0] = 1 # bias

    def setWeight(u,v,w):
        self.weights[u,v] = w

    def setInput(self,input_array):
        self.activation[1:self.inputEnd] = input_array

    def readOutput(self):
        return self.activation[self.outputStart:self.numNodes]

    def flush(self):
        self.activation[self.inputEnd:].fill(0)

    def step(self):
        self.activation[self.inputEnd:] = np.dot(self.activation,self.weights)
        self.activation[self.inputEnd:] = sigm(self.activation[self.inputEnd:])

    def save(self):
        cPickle.dump(self,open(path,'wb'),2)

