
import GeneralizedTartarus
import copy
import cPickle

SIZE = 6
NUM_BRICKS = 6

EMPTY = 0
WALL = 1
BRICK = 2

def get_surrounding(x,y):
    return ((x,y+1),(x+1,y+1),(x+1,y),(x+1,y-1), \
            (x,y-1),(x-1,y-1),(x-1,y),(x-1,y+1))

def clear_surrounding(x,y,tar):
    for (x,y) in get_surrounding(x,y):
        if tar.board[x,y] == BRICK:
            tar.board[x,y] == EMPTY

def has_way_out(x,y,tar):
    s = get_surrounding(x,y)
    if not EMPTY in [tar.board[x,y] for (x,y) in \
                     [s[0],s[2],s[4],s[6]]]:
        return False
    else: return True

def brick_configs(old_tar,x,y,configs,num_bricks):
    configs.add(old_tar.sense())
    print x,y,num_bricks
    for (x0,y0) in get_surrounding(x,y):
        if old_tar.board[x0,y0] == EMPTY and num_bricks>0:
            new_tar = copy.deepcopy(old_tar)
            new_tar.board[x0,y0] = BRICK
            if has_way_out(x,y,new_tar):
                brick_configs(new_tar,x,y,configs,num_bricks-1)
    




# initialize empty tartarus
tar = GeneralizedTartarus.GeneralizedTartarus({})
tar.configs = None

# keep track of all possible configs
configs = set()
cPickle.dump(configs,open('sensor_events.pkl','w'),2)


# clear out bricks
for x in range(1,SIZE+1):
    for y in range(1,SIZE+1):
        if tar.board[x,y] == BRICK:
            tar.board[x,y] = EMPTY

# for each bulldozer location
print tar
for x in range(1,SIZE+1):
    for y in range(1,SIZE+1):
        if (x,y) in ((1,1),(1,2),(1,6),
                     (2,6),(6,6),(6,5),
                     (6,1),(5,1),(2,2)):
            tar.x = x
            tar.y = y
            brick_configs(tar,x,y,configs,NUM_BRICKS)
            print x,y
            print configs
            print len(configs)


print configs
print len(configs)
cPickle.dump(configs,open('sensor_events.pkl','w'),2)


        
