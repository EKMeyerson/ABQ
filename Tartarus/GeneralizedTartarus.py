""" Generalized Tartarus Domain """

import sys
sys.path.append('..')
import random
from copy import deepcopy
import numpy as np

from Domain import Domain

# cell states
EMPTY = 0
WALL = 1
MIN_BRICK = 2 # brick values are all greater than or equal to 2

# actions
FORWARD = 0
LEFT = 1
RIGHT = 2

# orientations
NORTH = 0
EAST = 1
SOUTH = 2
WEST = 3


class GeneralizedTartarus(Domain):

    """ Required domain methods """

    def __init__(self,config):
        self.size = config.getint('tartarus','size')
        self.num_bricks = config.getint('tartarus','num_bricks')
        self.num_score_loc = config.getint('tartarus','num_score_loc')
        self.num_steps = config.getint('tartarus','num_steps')
        self.num_init_configs = config.getint('tartarus','num_init_configs')
        self.board = np.zeros((self.size+2,self.size+2),dtype='int16')
        self.empty_board = np.zeros((self.size+2,self.size+2),dtype='int16')
        self.bricks = np.zeros((self.num_bricks,2),dtype='int16')
        self.init_empty_board()
        self.init_score_locations()
        self.bricks = np.zeros((self.num_bricks,2),dtype='int16')
        self.orientation = NORTH
        self.configs = np.zeros((self.num_init_configs,self.num_bricks+1,2),
                                    dtype='int16')
        self.gen_init_configs()
        self.sensors = np.zeros(8)
        #self.inputs = np.zeros(16)
        self.inputs = np.zeros(24)
        self.hand_coded = np.zeros(2*self.num_bricks*self.num_init_configs,
                                    dtype='int16') 
        self.reset()

    def reset(self):
        self.curr_config = 0
        self.next_config()
        self.orientation = NORTH
        self.total_fitness = 0
        self.hand_coded.fill(0)

    def sense(self):
        return self.inputs

    def update_inputs(self):
        self.update_sensors()
        i = 0
        for s in self.sensors:
            if s==EMPTY: self.inputs[i:i+3] = (1,0,0)
            elif s==WALL: self.inputs[i:i+3] = (0,1,0)
            else: self.inputs[i:i+3] = (0,0,1)
            i += 3

    def get_num_sensors(self): return 16

    def act(self,a):
        # BAD ORG
        self.curr_step+=1
        if a == FORWARD: self.forward()
        elif a == LEFT: self.left()
        elif a == RIGHT: self.right()
        else: raise Exception ('Bad Action Specified')

        if self.trial_done():
            self.update_fitness()
            #self.update_hand_coded()
            self.curr_config += 1
            if not self.done(): 
                self.next_config()

    def get_num_actions(self): return 3

    def get_fitness(self):
        return self.total_fitness

    def getHandCoded(self,b,f):
        return deepcopy(self.hand_coded)

    def hand_coded_distance(self,b1,b2):
        d = 0
        for c in range(self.num_init_configs):
            d += manhatten(b1[c],b2[c])
        return d/float(self.num_init_configs)

    def done(self): return self.curr_config == self.num_init_configs

    def __str__(self):
        s = ''
        for y in range(self.size+1,-1,-1):
            s += '\n'
            for x in range(0,self.size+2):
                if self.board[x,y] == WALL: s += '|'
                elif self.board[x,y] >= MIN_BRICK: s += str(self.board[x,y])
                elif (self.x,self.y) == (x,y):
                    if self.orientation == NORTH: s += '^'
                    elif self.orientation == EAST: s += '>'
                    elif self.orientation == SOUTH: s += 'v'
                    else: s += '<'
                elif (x,y) in self.score_locations: 
                    s += 'X'
                else: s += ' '
            s += str(y)
        return s

    """ Other methods """
    
    def clear_board(self): self.board[:] = self.empty_board

    def init_empty_board(self):
        for x in range(0,self.size+2):
            for y in range(0,self.size+2):
                if x in (0,self.size+1) or y in (0,self.size+1):
                    self.empty_board[x,y] = WALL
                else: self.board[x,y] = EMPTY

    def gen_init_configs(self):
        genned_configs = 0
        while genned_configs < self.num_init_configs:
            self.clear_board()
            for b in range(self.num_bricks):
                x,y = self.random_inner_place()
                self.board[x,y] = b+MIN_BRICK
                self.bricks[b,0] = x
                self.bricks[b,1] = y
            self.x,self.y = self.random_inner_place()
            if self.valid_board():
                self.configs[genned_configs,:self.num_bricks] = self.bricks
                self.configs[genned_configs,self.num_bricks:] = (self.x,self.y)
                genned_configs += 1
    
    def valid_board(self):
        """
        for (x,y) in self.bricks:
            if ((x+1,y) in self.bricks) \
            and ((x,y+1) in self.bricks) \
            and ((x+1,y+1) in self.bricks):
                print x,y
                print self.bricks
                return False
        return True
        """
        for x in range(1,self.size+1):
            for y in range(1,self.size+1):
                if self.board[x,y] >= MIN_BRICK \
                and self.board[x+1,y] >= MIN_BRICK \
                and self.board[x,y+1] >= MIN_BRICK \
                and self.board[x+1,y+1] >= MIN_BRICK:
                    print self
                    return False
        return True

    def init_score_locations(self):
        #self.score_locations = set()
        #for l in range(self.num_score_loc): 
        #    self.score_locations.add(self.random_wall_place())
        self.score_locations = {(1,1),(1,6),(6,1),(6,6)}

    def set_default_score_locations(self):
        self.score_locations = {(1,1),(1,6),(6,1),(6,6)}

    def next_config(self):
        self.clear_board()
        self.bricks[:] = self.configs[self.curr_config,:self.num_bricks]
        self.x = self.configs[self.curr_config,-1,0]
        self.y = self.configs[self.curr_config,-1,1]
        for b in range(self.num_bricks): 
            self.board[self.bricks[b,0],self.bricks[b,1]] = b + MIN_BRICK
        self.curr_step = 0
        self.update_inputs()

    def random_inner_place(self):
        while(True):
            # choose location not on wall
            x = random.randrange(2,self.size)
            y = random.randrange(2,self.size)
            if self.board[x,y] == EMPTY:
                return x,y

    def on_wall(self,x,y):
        if (x in (1,self.size)) or (y in (1,self.size)): return True
        else: return False

    def random_wall_place(self):
        while(True):
            # choose location on wall
            x = random.randrange(1,self.size+1)
            y = random.randrange(1,self.size+1)
            if (x,y) not in self.score_locations \
            and self.on_wall(x,y):
                return x,y

    def update_sensors(self):
        self.sensors[0] = self.board[self.x,self.y+1] # N
        self.sensors[1] = self.board[self.x+1,self.y+1] # NE
        self.sensors[2] = self.board[self.x+1,self.y] # E
        self.sensors[3] = self.board[self.x+1,self.y-1] # SE
        self.sensors[4] = self.board[self.x,self.y-1] # S
        self.sensors[5] = self.board[self.x-1,self.y-1] # SW
        self.sensors[6] = self.board[self.x-1,self.y] # W
        self.sensors[7] = self.board[self.x-1,self.y+1] # NW
    
    def update_hand_coded(self):
        self.hand_coded[2*self.num_bricks*self.curr_config:
            2*self.num_bricks*(self.curr_config+1)] = self.bricks.flatten()
    
    def update_fitness(self):
        fitness = 0
        """
        for (x,y) in self.bricks:
        """
        for b in range(self.num_bricks):
            x,y = self.bricks[b,0],self.bricks[b,1]
            if (x,y) in self.score_locations:
                fitness += 2
            elif self.on_wall(x,y):
                fitness += 1
        self.total_fitness += fitness
  
    def forward(self):
        # (x1,y1) space one ahead, (x2,y2) two ahead
        if self.orientation==NORTH:
            x1,y1 = self.x,self.y+1
            x2,y2 = self.x,self.y+2
        elif self.orientation==EAST:
            x1,y1 = self.x+1,self.y
            x2,y2 = self.x+2,self.y
        elif self.orientation==SOUTH:
            x1,y1 = self.x,self.y-1
            x2,y2  = self.x,self.y-2
        else:
            x1,y1 = self.x-1,self.y
            x2,y2 = self.x-2,self.y
        
        if self.board[x1,y1]==EMPTY:
            self.x,self.y = x1,y1
            self.update_inputs()
        elif self.board[x1,y1] >= MIN_BRICK and self.board[x2,y2]==EMPTY:
            self.board[x2,y2] = self.board[x1,y1]
            self.board[x1,y1] = EMPTY
            self.x,self.y = x1,y1
            self.bricks[self.board[x2,y2]-MIN_BRICK,0] = x2
            self.bricks[self.board[x2,y2]-MIN_BRICK,1] = y2
            self.update_inputs()
            
    def left(self):
        self.orientation = (self.orientation - 1) % 4

    def right(self):
        self.orientation = (self.orientation + 1) % 4

    def trial_done(self): return self.curr_step == self.num_steps

if __name__=='__main__':
    import ConfigParser
    config = ConfigParser.ConfigParser()
    config.read(sys.argv[1])
    tartarus = GeneralizedTartarus(config)
    actions = [FORWARD,LEFT,LEFT,LEFT,FORWARD,FORWARD,RIGHT,FORWARD]
    print 'Begin'
    while(not tartarus.done()):
        print tartarus
        print tartarus.total_fitness
        tartarus.act(int(raw_input())%3)
    print tartarus.get_fitness()






