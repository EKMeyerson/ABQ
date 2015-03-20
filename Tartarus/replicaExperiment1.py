"""
Replicate generic crowding + hamming distance result from '09 paper
"""

import sys
sys.path.append('../Crowding')
import ConfigParser
import GenericCrowding
import GeneralizedTartarus

config = ConfigParser.ConfigParser()
config.read(sys.argv[1])

task = GeneralizedTartarus.GeneralizedTartarus(config)
task.set_default_score_locations()

ne = GenericCrowding.GenericCrowding(task,config)

while not ne.done():
    print ne.curr_iteration,ne.get_best_fitness(),ne.get_avg_fitness()
    ne.step()

