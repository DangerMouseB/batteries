#*******************************************************************************
#
#    Copyright (c) 2017-2019 David Briant
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
#
#*******************************************************************************


import math, numpy as np
from .pipeable import Pipeable
from .missing import Missing

class ArgumentError(Exception): pass


@Pipeable
def LogisticCDF(x, mu, s):
    return 1 / (1 + math.exp(-1 * (x - mu) / s))


@Pipeable
def LogisticCDFInv(p, mu, s):
    return mu + -s * math.log(1 / p - 1)


@Pipeable
def Len(lenable):
    return len(lenable)


@Pipeable
def Mean(pg):
    return np.mean(pg._values)


@Pipeable
def Std(pg):
    return np.std(pg._values)


@Pipeable
def Sqrt(x):
    return np.sqrt(x)


@Pipeable
def Str(a):
    return str(a)


@Pipeable
def Div(a, b):
    return a / b


@Pipeable
def Format(format, thing):
    return format.format(thing)


@Pipeable
def Flip(listOfLists):
    answer = []
    for i in range(len(listOfLists)):
        for j in range(len(listOfLists[0])):
            if i == 0:
                answer.append([])
            answer[j].append(listOfLists[i][j])
    return answer


def Sequence(*args, **kwargs):
    assert len(args) == 2
    n = kwargs.get('n', Missing)
    step = kwargs.get('step', Missing)
    sigmas = kwargs.get('sigmas', Missing)
    if step is Missing and n is Missing:
        first , last = args
        return list(range(first, last+1, 1))
    elif n is not Missing and sigmas is not Missing:
        mu, sigma = args
        low = mu - sigmas * sigma
        high = mu + sigmas * sigma
        return Sequence(low, high, n=n)
    elif n is not Missing and sigmas is Missing:
        first , last = args
        return list(np.linspace(first, last, n))
    elif n is Missing and step is not Missing:
        first , last = args
        return list(np.arange(first, last + step, step))
    else:
        raise TypeError('Must only specify either n or step')

@Pipeable
def CallFReturnX(f, x):
    f(x)
    return x
PP = CallFReturnX(print)

