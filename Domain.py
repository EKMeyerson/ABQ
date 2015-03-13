
class Domain:

    def reset(self): raise NotImplementedError

    def sense(self): raise NotImplementedError

    def act(self): raise NotImplementedError

    def get_fitness(self): raise NotImplementedError

    def get_hand_coded_behavior(self): raise NotImplementedError

    def done(self): raise NotImplementedError

    def __str__(self): raise NotImplementedError
