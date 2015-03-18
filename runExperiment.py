""" General script for running experiments """

import sys
sys.path.append('./Tartarus')
import numpy as np
import random
import cPickle
import importlib
import ConfigParser
import multiprocessing


import behaviors
import distances

MIN_FITNESS = -1000000

# Load settings
configfile = sys.argv[1]
config = ConfigParser.ConfigParser()
config.read(configfile)

num_gens = config.getint('evolution','num_generations')
ea_kind = config.get('evolution','drive')
if ea_kind == 'novelty': from NoveltySearch import NoveltySearch as ea
else: from DNN import DNN as ea



# Load domain
domain_name = config.get('domain','domain_name')
Domain = importlib.import_module(domain_name)
domain_init = getattr(Domain,domain_name)
domain = domain_init(config)
num_input = config.getint('domain','num_input')
num_output = config.getint('domain','num_output')
completion_threshold = config.getfloat('domain','completion_threshold')
task_set = cPickle.load(open(config.get('domain','task_set'),'rb'))

# Load metric
behavior = config.get('metric','behavior')
if behavior == 'hand_coded':
    get_behavior = domain.getHandCoded
elif behavior == 'event_counts':
    get_behavior = behaviors.eventCounts
elif behavior == 'sensory_action_history': 
    get_behavior = behaviors.sensoryActionHistory
elif behavior == 'action_history':
    get_behavior = behaviors.actionHistory
elif behavior == 'fitness': 
    get_behavior = behaviors.fitness
elif behavior == 'random':
    get_behavior = behaviors.random

distance = config.get('metric','distance')
if ea_kind == 'novelty':
    if distance == 'hand_coded':
        ea.score = domain.hand_coded_distance
    elif distance == 'euclidean':
        ea.score = distances.euclidean
    elif distance == 'hamming':
        ea.score = distances.hamming
    elif distance == 'manhattan':
        ea.score = distances.manhattan

if config.get('metric','features') != '':
    features = cPickle.load(open(config.get('metric','features'),'rb'))

# Set up output files
file_prefix = config.get('output','prefix')
file_prefix = 'results/{}'.format(file_prefix)
RESULTS_FILE = file_prefix + '.results'
PROGRESS_FILE = file_prefix + '.progress'
SAMPLES_FILE = file_prefix + '.samples'
sampling = config.getboolean('output','collect_samples')
success_sample_threshold = config.getfloat('output','success_sample_threshold')
failure_sample_prob = config.getfloat('output','failure_sample_prob')

# Run experiment
t = 0
total_fitness = 0
for task in task_set:
    t += 1
    ne = ea(num_input,num_output,config)
    best_fitness = MIN_FITNESS
    curr_gen = 1
    evolving = True
    while evolving:
        curr_best_fitness = MIN_FITNESS
        for i in range(ne.get_population_size()): # multi process (pool) this
            print curr_gen,best_fitness,curr_best_fitness
            task.reset()
            brain = ne.get_indiv(i)
            b = []
            while not task.done():
                sensors = task.sense()
                brain.setInput(sensors)
                brain.step()
                action = np.argmax(brain.readOutput())
                task.act(action)
                b.extend(list(sensors))
                b.append(action)
                if task.trial_done(): brain.flush()
            f = task.get_fitness()
            b = task.get_fitness()
            ne.eval_indiv(i,b)
            if f > best_fitness: best_fitness = f
            if f > curr_best_fitness: curr_best_fitness = f
            if sampling:
                if f >= success_sample_threshold \
                or random.random >= failure_sample_prob:
                    #write_sample(f,brain,b)
                    with open(SAMPLES_FILE,'a') as samples_file:
                        samples_file.write('{} {}\n'.format(f,b))
        if best_fitness >= completion_threshold: 
            evolving = False
        elif curr_gen >= num_gens:
            evolving = False
            curr_gen += 1
        else:
            ne.next_gen()
            curr_gen += 1
    total_fitness += best_fitness
    #write_result(curr_gen,best_fitness)
    with open(RESULT_FILE,'a') as result_file:
        result_file.write('{} {}\n'.format(curr_gen,best_fitness))
    #write_progress(behavior,t,total_fitness/float(t))
    with open(PROGRESS_FILE,'a') as progress_file:
        progress_file.write('{} {} {}\n'.format(behavior,t,total_fitness/float(t)))
print 'Complete.'

