""" Interface for implementing domains in ABQ framework """

class Domain:

    def __init__(self,args): raise NotImplementedError

    def reset(self): raise NotImplementedError

    def sense(self): raise NotImplementedError
    
    def get_num_sensors(self): raise NotImplementedError

    def act(self,a): raise NotImplementedError

    def get_num_actions(self): raise NotImplementedError

    def get_fitness(self): raise NotImplementedError

    def get_hand_coded_behavior(self): raise NotImplementedError
    
    def hand_coded_distance(self,b1,b2): raise NotImplementedError

    def done(self): raise NotImplementedError

    def __str__(self): raise NotImplementedError
