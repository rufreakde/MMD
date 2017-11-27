#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Import Libraries
import sys
import numpy as np
import random
import math

''' Explanation of the idea:
Given a set of points (x,y) with n elements and a polynomial P of degree d, the function we want to minimize 
is the sum of squared errors between P(x) and y for all points in the point set. 
For a polynomial of degree 2 this would yield: Q(w) = sum_i(w1 + w2 x_i + w3 x_i**2 - y_i). 
The gradient for a point sample i is thus a vector of the partial derivatives dQ_i(w)/dw = [dQ_i/dw1, dQ_i/dw2, dQ_i/dw3].
When we collect those gradients for all samples i in the point set we will end up with a matrix of the dimension n x d. 

Implementation of gradientDescent: We randomly sample x values and construct a matrix X where each row contains the following values for 
one x [1, x, x**2, x**3, ..., x**d]. 
When we then multiply our estimated weights vector [w1,...,wd] with this matrix we receive the estimated result y_est of 
the polynomial for each x and can compare it to the true y-value and receive the error for every x.
The gradient can then be computed by multiplying the error vector with the matrix X. 
'''


def gradientDescent(x, y, d, alpha, numIter):
    '''
    
    input:    x: matrix where each row contains [1,x,x**2,...x**d]
              y: true y-values for each x 
              d: degree of the polynomial which we want to estimate
              alpha: learning rate
              numIter: number of Iterations to perform
              
    output:   weights: vector of calculated weights [w1, ..., wd]
    
    '''
    xTrans = x.transpose()
    weights = np.random.randint(0,10,d+1) # initialize weights as random values 

    for i in range(0, numIter):
        hypothesis = np.dot(x, weights)
        error = hypothesis - y 
        cost = np.sum(error ** 2) / (2 * x.shape[0])
        print("Iteration %d | Cost: %f" % (i, cost))
        gradient = np.dot(xTrans, error) / x.shape[0]
        weights = weights - alpha * gradient
    
    return weights
    
    
def genData(true_weights, degree, n):
    ''' Function which samples x-values and constructs the above-mentioned matrix X as well as 
    the for each x corresponding true y-values. 
    
    input:   true_weights: true weights of the polynomial which we later want to estimate. 
             degree: degree of the polynomial
             n: number of samples
    
    output:  x_vals: matrix X of dimension n x d 
             y_vals: vector of length n containing the true y-value for each sample x
    
    '''
    true_weights_r = [x for x in reversed(true_weights)]
    sampled = np.random.randint(0,10,n) # sample x-values
    y_vals = n*[None]
    x_vals = np.zeros(n*(degree+1))
    x_vals.shape = (n, degree+1)
    
    # Fill the matrix X
    x_vals[:,0] = 1
    for i in range(0,len(sampled)):    
        for d in range(1, degree+1):
            x_vals[i,d] = sampled[i]**d
        # Compute corresponding true y-value
        y_vals[i] = np.asscalar(np.polyval(true_weights_r, sampled[i]))
    
    return x_vals, y_vals
   
    
if __name__ == '__main__':
    true_weights = [4,2,1] # Test polynomial: y = x**2 + 2x + 4
    x,y = genData(true_weights, degree=2, n=1001)
    weights = gradientDescent(x, y, d=2, alpha=0.001, numIter=20000)
    print('True polynomial: y = x**2 + 2x + 4')
    print('Estimated weights: ', weights)
    print('Estimated polynomial: y = ', weights[2], 'x**2 + ', weights[1], 'x + ', weights[0])
    