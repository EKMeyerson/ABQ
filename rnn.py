# Recurrent neural network class.

import numpy as np
import cPickle
import copy
'''
def sigmoid(x):
    return (np.tanh(2*(x-0.5))+1)/2
'''
'''
def linear(x):
    return x

def sigmoid(x):
    return np.tanh(x)
'''
# min and maximum activations (for linear units)
MAX_A = 100
MIN_A = -100


class RNN:
    
    def __init__(self, numInput, numOutput, config):
        
        self.output_type = config.get('network','output_type')

        self.numInput = numInput
        self.numOutput = numOutput
        self.numHidden = 0
        self.numNodes = 1 + numInput + numOutput # include bias node
        self.weights = np.zeros( (self.numNodes,self.numNodes) )
        self.activation = np.zeros(self.numNodes) # current activation
        self.present_connections = set()
        self.absent_connections = set()
        self.bias_connections = set()
        
        for o in range(1+self.numInput,self.numNodes):
            self.bias_connections.add((0,o))

        for u in range(1,self.numNodes):
            for v in range(1,self.numNodes):
                self.absent_connections.add((u,v))


    def setInput(self,inputs):
        input_arr = np.array(inputs)
        self.activation[0] = 1 # bias
        self.activation[1:self.numInput+1] = input_arr

    def readOutput(self):
        return self.activation[self.numInput+1:self.numInput+1+self.numOutput]
    
    def addConnection(self,u,v):
        if (u,v) in self.present_connections:
            raise Exception("Connection {} already exists.".format((u,v)))
        elif (u,v) not in self.absent_connections:
            raise Exception("Connection {} not meaningful.".format((u,v)))
        self.present_connections.add((u,v))
        self.absent_connections.remove((u,v))

    def removeConnection(self,u,v):
        if (u,v) not in self.present_connections:
            raise Exception("Connection does not exist.")
        self.present_connections.remove((u,v))
        self.absent_connections.add((u,v))
        self.weights[u,v] = 0

    def addHidden(self):
        temp = np.zeros( (self.numNodes+1,self.numNodes+1) )
        temp[:self.numNodes,:self.numNodes] = self.weights
        self.weights = temp
        
        for u in range(1,self.numNodes+1):
            self.absent_connections.add((u,self.numNodes))
            self.absent_connections.add((self.numNodes,u))
        self.bias_connections.add((0,self.numNodes))
        
        self.numNodes += 1
        self.numHidden += 1    
        self.activation = np.zeros(self.numNodes)

    def removeHidden(self,u):
        if u < 1+self.numInput+self.numOutput:
            raise Exception("Not a hidden node.")
        elif u > self.numNodes:
            raise Exception("Not a node.")
        self.weights = np.delete(np.delete(self.weights,u,0),u,1)
        new_present = set()
        new_absent = set()
        for (s,t) in self.present_connections:
            if s > u: new_s = s - 1
            else: new_s  = s
            if t > u: new_t = t - 1
            else: new_t = t
            if s != u and t != u:
                new_present.add((new_s,new_t))
        for (s,t) in self.absent_connections:
            if s > u: new_s = s - 1
            else: new_s  = s
            if t > u: new_t = t - 1
            else: new_t = t
            if s != u and t != u:
                new_absent.add((new_s,new_t))
        self.present_connections = copy.copy(new_present)
        self.absent_connections = copy.copy(new_absent)
        
        self.bias_connections.remove((0,self.numNodes-1))

        self.numNodes -= 1
        self.numHidden -= 1
        self.activation = np.zeros(self.numNodes)

    def initializePerceptron(self):
        for u in range(1,self.numInput+1):
            for v in range(self.numInput+1,self.numInput+1+self.numOutput):
                self.addConnection(u,v)

    def setWeight(self,u,v,w):
        if (u,v) in self.present_connections.union(self.bias_connections):
            self.weights[u,v] = w
        else: raise Exception("Connection does not exist.")

    def flush(self):
        self.activation.fill(0)
        self.activation[0] = 1
    
    def step(self):
        self.activation = np.dot(self.activation,self.weights)
        if self.output_type == 'sigmoid':
            self.activation[:] = np.tanh(self.activation[:])
        else:
            self.activation[:self.numInput+self.numOutput+1] = \
                self.activation[:self.numInput+self.numOutput+1].clip(MIN_A,MAX_A)
            self.activation[1+self.numInput+self.numOutput:] = \
                np.tanh(2*self.activation[1+self.numInput+self.numOutput:])

            

    def save(self,path):
        cPickle.dump(self,open(path,'wb'),2)

if __name__=='__main__':
    # Test XOR network
    xor = RNN(2,1)
    xor.addHidden()
    xor.addHidden()
    for u,v in [(1,5),(1,4),(2,5),(2,4),(4,3),(5,3)]:
        xor.addConnection(u,v)
    xor.setWeight(0,3,0)
    xor.setWeight(0,4,-1)
    xor.setWeight(0,5,0)
    xor.setWeight(1,5,1)
    xor.setWeight(1,4,1)
    xor.setWeight(2,5,1)
    xor.setWeight(2,4,1)
    xor.setWeight(5,3,1)
    xor.setWeight(4,3,-1)
    print xor.weights

    data = ((0,0,0),(0,1,1),(1,0,1),(1,1,0))

    for d in data:
        xor.flush()
        xor.setInput(d[:2])
        print xor.activation
        xor.step()
        print xor.activation
        xor.step()
        print xor.activation
        output = xor.readOutput()
        print d,output

