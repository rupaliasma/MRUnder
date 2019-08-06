#!/usr/bin/env python

"""
This module generates Variable Density mask in One Dimension and in two dimensions.
In one dimension:-
Any of the two read-out direction can be choosen.
Also, a special kind of mask can be generated by overlapping same pattern on top of each other for both the directions.
This special mask can not be treated as Variable Density mask in two dimensions. 
In two dimension:-
This module can also be used for generating variable density mask in two dimensions (aka Gauss Mask).

"""

import numpy as np
import math 
from scipy.stats import norm
from scipy.stats import multivariate_normal as mvn

__author__ = "Mariio Breitkopf, Soumick Chatterjee"
__copyright__ = "Copyright 2019, Mario Breitkopf, Soumick Chatterjee & OvGU:ESF:MEMoRIAL"
__credits__ = ["Mariio Breitkopf", "Soumick Chatterjee"]

__license__ = "GPL"
__version__ = "0.0.1"
__email__ = "soumick.chatterjee@ovgu.de"
__status__ = "Finished"

def createVardenMask1D(slice, percent, maxAmplitude4PDF, ROdir, returnPDF=False):  
    mask = np.zeros(slice.shape)
    if ROdir == 2:
        percent = percent/2
        if slice.shape[0] == slice.shape[1]:
            mask, distfunc, randseed = _mask1DForROdir(mask, percent, maxAmplitude4PDF, 0)
            mask, _, _ = _mask1DForROdir(mask, percent, maxAmplitude4PDF, 1, distfunc, randseed)
        elif slice.shape[0] > slice.shape[1]:
            mask, distfunc, randseed = _mask1DForROdir(mask, percent, maxAmplitude4PDF, 0)
            dim_difference = slice.shape[0] - slice.shape[1]
            _distfunc = distfunc[dim_difference//2:(slice.shape[1]+dim_difference//2)]
            _randseed = randseed[dim_difference//2:(slice.shape[1]+dim_difference//2)]
            mask, _, _ = _mask1DForROdir(mask, percent, maxAmplitude4PDF, 1, _distfunc, _randseed)
        else:
            mask, distfunc, randseed = _mask1DForROdir(mask, percent, maxAmplitude4PDF, 1)
            dim_difference = slice.shape[1] - slice.shape[0]
            _distfunc = distfunc[dim_difference//2:(slice.shape[0]+dim_difference//2)]
            _randseed = randseed[dim_difference//2:(slice.shape[0]+dim_difference//2)]
            mask, _, _ = _mask1DForROdir(mask, percent, maxAmplitude4PDF, 0, _distfunc, _randseed)
    else:
        mask, distfunc, _ = _mask1DForROdir(mask, percent, maxAmplitude4PDF, ROdir)

    if returnPDF:
        if slice.shape[0] > slice.shape[1]:
            return mask, np.tile(distfunc,(slice.shape[1],1))
        else:
            return mask, np.tile(distfunc,(slice.shape[0],1))
    else:
        return mask

def _mask1DForROdir(mask, percent, maxAmplitude4PDF, ROdir, distfunc=None, randseed=None):
    shape = mask.shape[ROdir]
    if distfunc is None or randseed is None:
        #Random Numbers Seed
        randseed = np.random.random(shape)

        #Initialize variables
        x = np.array(range(shape))
        mu = np.floor(x.size/2)
        sigma = np.floor(x.size/2)

        currentPercent=1
        while currentPercent > percent:
            #Distribution function
            distfunc = maxAmplitude4PDF*math.sqrt(2*math.pi)*sigma*norm.pdf(x,mu,sigma);       # 0.8 

            #Selection of k-space lines
            B = np.zeros(shape)
            #B[randseed>distfunc] = 0
            B[randseed<distfunc] = 1
            B[round(shape/2-shape/round(shape/4)):round(shape/2+shape/round(shape/4))] = 1
            currentPercent = np.count_nonzero(B)/B.size
            sigma = np.floor(0.95*sigma)
    else:
        #Selection of k-space lines
        B = np.zeros(shape)
        #B[randseed>distfunc] = 0
        B[randseed<distfunc] = 1
        B[round(shape/2-shape/round(shape/4)):round(shape/2+shape/round(shape/4))] = 1

    if ROdir == 0:
        mask[B==1,:] = 1
    else: #ROdir == 1:
        mask[:,B==1] = 1

    return mask, distfunc, randseed

def createVardenMask2D(slice, percent, returnPDF=False):
    #AKA Gauss Mask
    
    #Xie1 = 1000
    #Xie2 = 10000
    
    #r1 = 0.8
    #r2 = 1.3
     
    #creates a mask that captures approximately 50% of the k-space data
    #with SIGMA old 15% -> new: compression factor Xie / (2 * pi)

    sigma = 1
    currentPercent=1
    while currentPercent > percent:         
        #Random Numbers Seed
        randseed = np.random.random(slice.shape)
        Xie1 = 5000/(2*math.pi) #Sharpness of the distribution 1, 0 <r <r0
        Xie2 = sigma*1000000/(2*math.pi) #Sharpness of distribution 2, r0 <r <r_max
        s = 0 #diagonal extension of distribution - / +
        r1 = 1.3 #> = 1, Determines the size of the full coverage of the k-space center, the height of the distribution 1
        r2 = 0.60 #<= 1, influence on the probabilities in the edge of the k-space, height of the distribution 2

        #Fit to mask size
        x1 = np.array(range(slice.shape[0]))
        x2 = np.array(range(slice.shape[1]))     
        X1, X2 = np.meshgrid(x1,x2) 

        #Distribution function 0 <r <r0
        mu1 = np.array([slice.shape[0]//2, slice.shape[1]//2])                         #Average
        #Sigma1 = 1/(2*math.pi)*np.array([[Xie1,Xie1*s], [Xie1*s,Xie1]])         #Covariance matrix, alternative
        Sigma1 = np.array([[Xie1,Xie1*s], [Xie1*s,Xie1]])                     # Covariance matrix
        F1 = (r1*Xie1)*2*math.pi*mvn.pdf(np.array([X1.flatten(), X2.flatten()]).transpose(),mu1,Sigma1)    # 2d Normal distribution 1

        F1 = np.reshape(F1,(len(x2),len(x1))).transpose()

        #Distribution function r0 <r <r_max
        mu2 = np.array([slice.shape[0]//2, slice.shape[1]//2])                        #Average
        #Sigma2 = 1/(2*math.pi)*np.array([[Xie2,Xie2*s], [Xie2*s,Xie2]])         #Covariance matrix, alternative
        Sigma2 = np.array([[Xie2,Xie2*s], [Xie2*s,Xie2]])                     # Covariance matrix
        F2 = (r2*Xie2)*2*math.pi*mvn.pdf(np.array([X1.flatten(), X2.flatten()]).transpose(),mu2,Sigma2)    #2d Normal distribution 2

        F2 = np.reshape(F2,(len(x2),len(x1))).transpose()

        #Overlay of both distributions
        #F = (F1 + F2)/2;

        #Transfer to dot mask
        mask = np.zeros(slice.shape)
        #mask[A>F2] = 0 #not needed
        #mask[A>F1] = 0 #not needed 
        mask[randseed<F2] = 1 
        mask[randseed<F1] = 1 
        PDF = F1
        idx = PDF <= F2
        PDF[idx] = F2[idx]
        PDF[PDF>=1] = 1

        currentPercent = np.count_nonzero(mask)/mask.size
        sigma = 0.95*sigma

    if returnPDF:
        return mask, PDF
    else:
        return mask