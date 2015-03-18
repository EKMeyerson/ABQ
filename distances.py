""" Generic distances for behaviors """

import numpy as np
import scipy.spatial.distance as sp

# b should be a list or np array

def hamming(b1,b2):
    if len(b1) != len(b2): b1,b2 = adjustLengths(b1,b2)
    return sp.hamming(b1,b2)

def euclidean(b1,b2):
    if len(b1) != len(b2): b1,b2 = adjustLengths(b1,b2)
    return sp.euclidean(b1,b2)

def manhatten(b1,b2):
    if len(b1) != len(b2): b1,b2 = adjustLengths(b1,b2)
    return sp.cityblock(b1,b2)  
