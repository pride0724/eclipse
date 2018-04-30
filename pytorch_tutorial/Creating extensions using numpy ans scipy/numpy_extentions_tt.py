'''
Created on 2018. 4. 25.

@author: DMSL-CDY
'''


'''
In this tutorial, we shall go the trhough two tasks:

1. Create a neural network layer with no parameters.
    - This call into numpy as part of it's implementation

2. Create a neural network layer that has learnable weights
    - This call into SciPy as part of it's implem


'''
import torch
from torch.autograd import Function
from torch.autograd import Variable

'''
Parameter-less example

this layer donesn't particularly do anything useful or mathematically correct.

It is aptly named BadFFTFunction


Layer Implementation
'''

from numpy.fft import rfft2, irfft2

class BadFFTFunction(Function):
    
    def forward(self, input):
        #numpy_input = input.detach().numpy() # detach() is not working
        numpy_input = input.numpy()
        result = abs(rfft2(numpy_input))
        return input.new(result)
    
    def backward(self, grad_output):
        numpy_go = grad_output.numpy()
        result = irfft2(numpy_go)
        return grad_output.new(result)
    
# since this layer does not have nay paramters, we can
# simply declare this as a function, rather than as an nn.Module class

def incorrect_fft(input):
    return BadFFTFunction()(input)


'''
Example usage of the create layer:
'''


input = torch.randn(8, 8)
input = Variable(input, requires_grad = True)

result = incorrect_fft(input)
print(result)
result.backward(torch.randn(result.size()))
print(input)
"""
input = torch.randn(8, 8, requires_grad = True)
result = incorrect_fft(input)
print(result)
result.backward(torch.randn(result.size()))
print(input)
"""


"""
Parameterized example

This implements a layer with learnable weights.

It implements the Cross-correlation with a learnable kernel.

In deep learning literature, it's confusingly referred to as Convolution.

The backward computes the gradients wrt the input and gradients wrt the filter.

Inplementation.

Please Note that the implementation serves as an illustration, and we did not verify it's correctness
"""

from scipy.signal import convolve2d, correlate2d
from torch.nn.modules.module import Module
from torch.nn.parameter import Parameter
"""
class ScipyConv2dFunction(Function):
    @staticmethod
    def forward(ctx, input, filter):
        #input, filter = input.detach(), filter.detach() # detach so we can cast to NumPy
        input, filter = input, filter # detach so we can cast to NumPy
        result = correlate2d(input.numpy(), filter.numpy(), mode='valid')
        ctx.save_for_backward(input, filter)
        return input.new(result)
    
    @staticmethod
    def backward(ctx, grad_output):
        grad_output = grad_output.detach()
        input, filter = ctx.saved_tensors
        grad_input = convolve2d(grad_output.numpy(), filter.t().numpy(), mode='full')
        grad_filter = convolve2d(input.numpy(), grad_output.numpy(), mode='valid')
        
        return grad_output.new_tensor(grad_input), grad_output.new_tensor(grad_filter)

"""
class ScipyConv2dFunction(Function):
    @staticmethod
    def forward(ctx, input, filter):
        input, filter = input, filter  # detach so we can cast to NumPy
        result = correlate2d(input.numpy(), filter.numpy(), mode='valid')
        ctx.save_for_backward(input, filter)
        return input.new(result)

    @staticmethod
    def backward(ctx, grad_output):
        grad_output = grad_output.detach()
        input, filter = ctx.saved_tensors
        grad_input = convolve2d(grad_output.numpy(), filter.t().numpy(), mode='full')
        grad_filter = convolve2d(input.numpy(), grad_output.numpy(), mode='valid')

        return grad_output.new_tensor(grad_input), grad_output.new_tensor(grad_filter)
    

class ScipyConv2d(Module):
    
    def __init__(self, kh, kw):
        super(ScipyConv2d, self).__init__()
        self.filter = Parameter(torch.randn(kh, kw))
    
    def forward(self, input):
        return ScipyConv2dFunction.apply(input, self.filter)
    

module = ScipyConv2d(3,3)
print(list(module.parameters()))

#input = torch.randn(10, 10, requires_grad = True)
input = Variable(torch.randn(10, 10), requires_grad = True)
output = module(input)
print(output)
output.backward(torch.randn(8,8))
print(input.grad)




"""

!!!!!!!!!!!!!!!!!! Not working !!!!!!!!!!!!!!!!!!!!!!!

"""