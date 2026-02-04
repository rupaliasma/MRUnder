#!/usr/bin/env python

"""
This module generates Uniform sampling mask (like that is used in Grappa)
"""

import numpy as np



def createUniformMask(slice, stepsize, ROdir, returnPercent=False):
    mask = np.zeros(slice.shape)

    if ROdir == 2:
        mask = _maskForROdir(mask, stepsize, 0)
        mask = _maskForROdir(mask, stepsize, 1)
    else:
        mask = _maskForROdir(mask, stepsize, ROdir)

    if returnPercent:
        return mask, np.count_nonzero(mask)/mask.size
    else:
        return mask

def _maskForROdir(mask, stepsize, ROdir):
    shape = mask.shape[ROdir]
    B = np.zeros(shape)

    B[(shape//2-shape//(shape//4))-1 : shape//2+shape//(shape//4)] = 1
    B[range(0,shape,stepsize)] = 1 

    if ROdir == 0:
        mask[B==1,:] = 1
    else: #ROdir == 1:
        mask[:,B==1] = 1


    return mask
