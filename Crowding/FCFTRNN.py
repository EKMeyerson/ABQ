""" 
Fully-connected fixed-topology recurrent neural network;
for replicating Tartarus results.
"""

import numpy as np
import cPickle

class FCFTRNN:

    def __init__(self, config):
        
        self.numInput = config.getint('network','num_input')
        self.numHidden = config.getint('network','num_hidden')
        self.numOutput = config.getint('network','num_output')
        # first node is bias node
        self.numNodes = 1 + self.numInput + self.numHidden + self.numOutput
        self.inputEnd = 1 + self.numInput
        self.outputStart = 1 + self.numInput + self.numHidden
        self.weights = np.zeros( (self.numNodes, self.numNodes))
        self.activation = np.zeros(self.numNodes)

    def setWeight(u,v,w):
        self.weights[u,v] = w

    def setInput(self,input_array):
        self.activation[0] = 1 # bias
        self.activation[1:self.inputEnd] = input_array

    def readOutput(self):
        return self.activation[self.outputStart:self.numNodes]

    def flush(self):
        self.activation.fill(0)

    def step(self):
        self.activation[:] = np.dot(self.activation,self.weights)
        self.activation[:] = np.tanh(self.activation)

    def save(self):
        cPickle.dump(self,open(path,'wb'),2)

