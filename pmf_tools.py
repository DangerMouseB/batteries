#************************************************************************************************************************************************
#
# Copyright 2017 David Briant
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#************************************************************************************************************************************************


# python
import sys, random

# 3rd party imports
import numpy as np
import scipy.stats

# local imports
from .pipeable import MoreArgsRequiredException, Pipeable
from .structs import PoD, NA, Sum
from .console_utils import PP


__all__ = ['PMF', 'd6', 'd8', 'd10', 'd12', 'd20', 'Mix', 'Mean', 'ExpectationOf', 'EX',
           'Normalised', 'RvAdd', 'RvSub', 'RvDiv', 'RvMul', 'RvMax', 'UpdatePrior', 'Sequence', 'VarOf', 'Var', 'SkewOf', 'Skew']

Missing = sys

# PMF - Probability Mass Function - the subset of all PMFs where xs (the values of the random variable) are discrete and known
# mean, median(s), stdev, percentile, CDF, etc of a DRV can be meaningfully calculated
# Bayes operates on the probs of the RV not the values - f(x) * g(x) / h(x)

class PMF(PoD):
    @staticmethod
    def Uniform(*xs):
        '''Makes a uniform PMF. xs can be sequence of values or [length]'''
        # if a single int it is a count else there must be many xs
        answer = PMF()
        if len(xs) == 1:
            arg = xs[0]
            if isinstance(arg, int):
                n = arg
                p = 1.0 / n
                for x in Sequence(0, n-1):
                    answer[float(x)] = p
                return answer
        p = 1.0 / len(xs)
        for x in xs:
            answer[float(x)] = p
        return answer


    @staticmethod
    def Triangle():
        #TODO think through interface and implement
        pass

    @staticmethod
    def Power(xs, alpha):
        answer = PMF()
        for x in xs:
            answer[x] = x ** (-alpha)
        return answer.Normalise()

    @staticmethod
    def Gaussian(mu, sigma, xs_or_num_sigmas, n=Missing):
        if n is not Missing:
            xs = Sequence(mu, sigma, sigmas=xs_or_num_sigmas, n=n)
        else:
            xs = xs_or_num_sigmas
        answer = PMF()
        for x in xs:
            p = scipy.stats.norm.pdf(x, mu, sigma)
            answer[x] = p
        return answer.Normalise()

    @staticmethod
    def Poisson(lamb, N):
        answer = PMF()
        for x in range(N):
            p = scipy.stats.poisson.pmf(x, lamb)
            answer[x] = p
        return answer.Normalise()

    @staticmethod
    def Binomial(n, p):
        answer = PMF()
        for k in range(n + 1):
            answer[k] = scipy.stats.binom.pmf(k, n, p)
        return answer

    @staticmethod
    @Pipeable
    def FromPdf(xs, pdf):
        '''FromPdf xs, pdf'''
        answer = PMF()
        for x in xs:
            p = pdf(x)
            if isinstance(p, (list, np.ndarray)):
                p = p[0]
            answer[x] = p
        return answer.Normalise()

    @staticmethod
    @Pipeable
    def Kde(xs, data):
        pdf = scipy.stats.gaussian_kde(data)
        answer = PMF()
        answer._kde = pdf
        for x in xs:
            answer[x] = pdf.evaluate(x)[0]
        return answer.Normalise()

    @staticmethod
    @Pipeable
    def FromSample(xs):
        answer = PMF()
        for x in xs:
            answer[x, 0] += 1
        return answer.Normalise()


    __slots__ = '_cmf', '_kde'

    def __init__(self, *args, **kwargs):
        object.__setattr__(self, '_cmf', None)
        object.__setattr__(self, '_kde', None)
        a = dict(PoDType='PMF')
        a.update(kwargs)
        if len(args) == 2 and hasattr(args[0], '__iter__') and  hasattr(args[1], '__iter__') and len(args[0]) == len(args[1]):
            args = zip(*args)
        try:
            # P2
            super(PMF, self).__init__(*args, **a)
        except:
            # P3
            super().__init__(*args, **a)

    def __setattr__(self, name, value):
        object.__setattr__(self, '_cmf', None)
        try:
            super(PMF, self).__setattr__(name, value)
        except:
            super().__setattr__(name, value)

    def __setitem__(self, key, value):
        object.__setattr__(self, '_cmf', None)
        try:
            super(PMF, self).__setitem__(key, value)
        except:
            super().__setitem__(key, value)

    def Percentile(self, y):
        cmf = self._GetCmf()
        if y < 0.0 or y > 1.0:
            raise ValueError("Must be between 0% and 100%")

        imax = cmf.shape[0] - 1
        i1, i2 = np.searchsorted(cmf[:, 1], y, side='left'), np.searchsorted(cmf[:, 1], y, side='right')
        if i1 != i2:
            return '{y:.1f}% => {amount:.1f}% in [{lower}, {upper})'.format(
                lower=cmf[i1, 0],
                upper=cmf[i2, 0],
                amount=cmf[i1, 1] * 100.0,
                y=y * 100.0,
            )
        if i1 == 0:
            return '{y:.1f}% => {amount1:.1f}% in [..., {upper1}) and {amount2:.1f}% in [{lower2}, {upper2})'.format(
                amount1=0,
                upper1=cmf[0, 0],
                amount2=cmf[0, 1] * 100.0,
                lower2=cmf[0, 0],
                upper2=cmf[1, 0],
                y=y * 100.0,
            )
        if i1 >= imax:
            return '{y:.1f}% => {amount1:.1f}% in [{lower1}, {upper1}) and {amount2:.1f}% in [{lower2}, ...)'.format(
                y=y * 100.0,
                amount1=cmf[imax - 1, 1] * 100.0,
                lower1=cmf[imax - 1, 0],
                upper1=cmf[imax, 0],
                amount2=100,
                lower2=cmf[imax, 0],
            )
        return '{y:.1f}% => {amount1:.1f}% in [{lower1}, {upper1}) and {amount2:.1f}% in [{lower2}, {upper2})'.format(
            amount1=cmf[i1 - 1, 1] * 100.0,
            lower1=cmf[i1 - 1, 0],
            upper1=cmf[i1, 0],
            amount2=cmf[i1, 1] * 100.0,
            lower2=cmf[i1, 0],
            upper2=cmf[i1 + 1, 0],
            y=y * 100.0,
        )

    def _GetCmf(self):
        cmf = object.__getattribute__(self, '_cmf')
        if cmf is None:
            cmf = np.array(list(self.KvIter()))
            cmf[:, 1] = np.cumsum(cmf[:, 1])
            object.__setattr__(self, '_cmf', cmf)
        return cmf

    def XsPs(self):
        xs, ps = [], []
        for x, p in self.KvIter():
            xs.append(x)
            ps.append(p)
        return xs, ps

    def Normalise(self):
        '''In place normalisation so total probability equals 1.0'''
        totalP = 0.0
        for x, p in self.KvIter():
            totalP += p
        for x, p in self.KvIter():
            self[x] = p / totalP
        return self

    def NormaliseAndSort(self):
        '''Another post processing operation'''
        _dict = object.__getattribute__(self, '_dict')
        secret = []
        xps = []
        totalP = 0.0
        for k, v in _dict.items():
            # TODO watch out for unicode in P2
            if isinstance(k, str) and k[:1] == '_':
                secret.append( (k, v) )
            else:
                xps.append( (k, v) )
                totalP += v
        xps.sort(key=lambda xp: xp[0])
        _dict = type(_dict)()
        for k, v in secret:
            _dict[k] = v
        for x, p in xps:
            _dict[x] = p / totalP
        object.__setattr__(self, '_dict', _dict)
        return self

    def Sample(self, n):
        kde = object.__getattribute__(self, '_kde')
        if kde is None:
            vals = []
            cmf = self._GetCmf()
            for _ in range(n):
                p = random.random()
                i = np.searchsorted(cmf[:, 1], p, side='left')
                vals.append(cmf[i, 0])
            return np.array(vals)
        else:
            return kde.resample(n).flatten()


@Pipeable
def Mix(*argsOrListOfArgs):
    """Mix(*argsOrListOfArgs) where arg is (beta, pmf) or pmf (beta is assumed to be 1.0)"""
    if len(argsOrListOfArgs) == 1 and isinstance(argsOrListOfArgs[0], list):
            args = argsOrListOfArgs[0]
    else:
        args = argsOrListOfArgs
    if len(args) < 2:
        raise MoreArgsRequiredException()
    answer = PMF()
    for arg in args:
        if isinstance(arg, tuple):
            beta, pmf = arg
        else:
            beta = 1.0
            pmf = arg
        for x, p in pmf.KvIter():
            answer[x] += beta * p
    return answer.NormaliseAndSort()


@Pipeable
def ExpectationOf(pmf):
    assert isinstance(pmf, PMF)
    answer = NA
    for x, p in pmf.KvIter():
        if answer is NA:
            answer = float(x * p)
        else:
            answer += x * p
    return answer

Mean = EX = ExpectationOf


@Pipeable
def VarOf(pmf):
    assert isinstance(pmf, PMF)
    answer = NA
    mean = NA
    for x, p in pmf.KvIter():
        if mean is NA:
            mean = float(x * p)
        else:
            mean += x * p
    for x, p in pmf.KvIter():
        x = x - mean
        if answer is NA:
            answer = float(x * x * p)
        else:
            answer += x *x * p
    return answer

Var = VarOf


@Pipeable
def SkewOf(pmf):
    assert isinstance(pmf, PMF)
    answer = NA
    mean = NA
    for x, p in pmf.KvIter():
        if mean is NA:
            mean = float(x * p)
        else:
            mean += x * p
    for x, p in pmf.KvIter():
        x = x - mean
        if answer is NA:
            answer = float(x * x * x * p)
        else:
            answer += x *x * x * p
    return answer

Skew = SkewOf


@Pipeable
def Normalised(pmf):
    return pmf / Sum(pmf)


@Pipeable
def RvAdd(lhs, rhs):
    if isinstance(lhs, PMF) and isinstance(rhs, PMF):
        answer = PMF()
        for x1, p1 in lhs.KvIter():
            for x2, p2 in rhs.KvIter():
                answer[x1 + x2] += p1 * p2
        return answer.NormaliseAndSort()
    else:
        raise TypeError('unhandle types of lhs and / or rhs')


@Pipeable
def RvSub(lhs, rhs):
    if isinstance(lhs, PMF) and isinstance(rhs, PMF):
        answer = PMF()
        for x1, p1 in lhs.KvIter():
            for x2, p2 in rhs.KvIter():
                answer[x1 - x2] += p1 * p2
        return answer.NormaliseAndSort()
    else:
        raise TypeError('unhandle types of lhs and / or rhs')


@Pipeable
def RvDiv(lhs, rhs):
    if isinstance(lhs, PMF) and isinstance(rhs, PMF):
        answer = PMF()
        for x1, p1 in lhs.KvIter():
            for x2, p2 in rhs.KvIter():
                answer[x1 / x2] += p1 * p2
        return answer.NormaliseAndSort()
    else:
        raise TypeError('unhandle types of lhs and / or rhs')


@Pipeable
def RvMul(lhs, rhs):
    if isinstance(lhs, PMF) and isinstance(rhs, PMF):
        answer = PMF()
        for x1, p1 in lhs.KvIter():
            for x2, p2 in rhs.KvIter():
                answer[x1 * x2] += p1 * p2
        return answer.NormaliseAndSort()
    else:
        raise TypeError('unhandle types of lhs and / or rhs')


@Pipeable
def RvMax(lhs, rhs):
    if isinstance(lhs, PMF) and isinstance(rhs, PMF):
        answer = PMF()
        for x1, p1 in lhs.KvIter():
            for x2, p2 in rhs.KvIter():
                answer[x1 if x1 > x2 else x2] += p1 * p2
        return answer.NormaliseAndSort()
    else:
        raise TypeError('unhandle types of lhs and / or rhs')


@Pipeable(minNumArgs=2)
def UpdatePrior(arg1, arg2, arg3=sys):
    """UpdatePrior(arg1, arg2, [arg3])
    if UpdatePrior(likelihoodFn, priorPmf, data) return priorPmf * likelihoodFn(data) >> Normalised
    if UpdatePrior(priorPmf, likelihoodPmf) answer priorPmf * likelihoodPmf >> Normalised"""
    if isinstance(arg1, PMF) and arg3 == sys:
        return arg1 * arg2 >> Normalised
    else:
        return arg2 * arg1(arg3)  >> Normalised


def Sequence(*args, **kwargs):
    # TODO move somewhere else
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





d6 = PMF.Uniform(*Sequence(1, 6))
d8 = PMF.Uniform(*Sequence(1, 8))
d10 = PMF.Uniform(*Sequence(1, 10))
d12 = PMF.Uniform(*Sequence(1, 12))
d20 = PMF.Uniform(*Sequence(1, 20))



