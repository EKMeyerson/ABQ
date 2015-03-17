# Generate tartarus task set

import sys
import GeneralizedTartarus
import cPickle
import ConfigParser

NUM_TASKS = 100
OUT_FILE = 'tartarus_test_mazes.pkl'


config = ConfigParser.ConfigParser()
config.read(sys.argv[1])

cPickle.dump([GeneralizedTartarus.GeneralizedTartarus(config) for n in range(NUM_TASKS)],open(OUT_FILE,'w'),2)
