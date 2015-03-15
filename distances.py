""" Generic distances for behaviors """

import numpy as np

# b should be a list or np array

def hamming(b1,b2):
    if len(b1) != len(b2): b1,b2 = adjustLengths(b1,b2)
    return sum(int(b1[i]!=b2[i] for i in range(len(b1))))

def euclidean(b1,b2):
    if len(b1) != len(b2): b1,b2 = adjustLengths(b1,b2)
    return np.linalg.norm(np.array(b1)-np.array(b2))
