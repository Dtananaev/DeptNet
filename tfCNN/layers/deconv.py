#
# Author: Denis Tananaev
# File: deconv.py
# Date: 9.02.2017
# Description: transposed convolutions functions for neural networks
#

#include libs
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
import os
from six.moves import xrange
import os
import re
import sys
import tarfile
import math 
import tensorflow as tf
import summary as sm

def _variable_on_cpu(name, shape, initializer, FLOAT16=False):
  """Helper to create a Variable stored on CPU memory.

  Args:
    name: name of the variable
    shape: list of ints
    initializer: initializer for Variable

  Returns:
    Variable Tensor
  """
  with tf.device('/cpu:0'):
    if(FLOAT16==True):
      dtype = tf.float16 
    else:
      dtype = tf.float32
    var = tf.get_variable(name, shape, initializer=initializer, dtype=dtype)
  return var


def _variable_with_weight_decay(name, shape, stddev, wd,FLOAT16=False):
  """Helper to create an initialized Variable with weight decay.
                                                  
  Note that the Variable is initialized with a truncated normal distribution.
  A weight decay is added only if one is specified.

  Args:
    name: name of the variable
    shape: list of ints
    stddev: standard deviation of a truncated Gaussian
    wd: add L2Loss weight decay multiplied by this float. If None, weight
        decay is not added for this Variable.

  Returns:
    Variable Tensor
  """
  if(FLOAT16==True):
    dtype = tf.float16 
  else:
    dtype = tf.float32
  var = _variable_on_cpu(
      name,
      shape,
      tf.truncated_normal_initializer(stddev=stddev, dtype=dtype))
  if wd is not None:
    weight_decay = tf.mul(tf.nn.l2_loss(var), wd, name='weight_loss')
    tf.add_to_collection('losses', weight_decay)
  return var



def deconv(data,output_shape,scope,shape,stride=[1, 2, 2, 1],padding='SAME',wd=0.0,FLOAT16=False,reuse=None):
  with tf.variable_scope(scope, 'DeConv', [data], reuse=reuse):
    STDdev=1/tf.sqrt(shape[0]*shape[1]*shape[2]/2) #Xavier/2 initialization      
    kernel = _variable_with_weight_decay('weights',
                                         shape=shape,
                                         stddev=STDdev,
                                         wd=wd,FLOAT16=FLOAT16)
    deconv = tf.nn.conv2d_transpose(data, kernel,output_shape, stride, padding=padding)
    biases = _variable_on_cpu('biases', [shape[2]], tf.constant_initializer(0.00001))#positive biases
    pre_activation = tf.nn.bias_add(deconv, biases)
    sm._activation_summary(pre_activation)
  return pre_activation    

