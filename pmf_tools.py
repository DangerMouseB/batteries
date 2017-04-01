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
import sys

# 3rd party imports
import numpy as np
import scipy.stats

# local imports
from .pipeable import MoreArgsRequiredException, Pipeable
from .structs import PoD, NA, Sum
from .console_utils import PP


__all__ = ['PMF', 'd6', 'd8', 'd10', 'd12', 'd20', 'Mix', 'Mean', 'ExpectationOf', 'EX',
           'Normalised', 'RvAdd', 'RvSub', 'CalcPosterior', 'Update', 'Sequence']

Missing = sys

# PMF - Probability Mass Function - the subset of all PMFs where xs (the values of the random variable) are discrete and known
# mean, median(s), stdev, percentile, CDF, etc of a DRV can be meaningfully calculated
# Bayes operates on the probs of the RV not the values - f(x) * g(x) / h(x)

class PMF(PoD):
    @staticmethod
    def Uniform(*xs):
        # if a single int it is a count else there must be many xs
        answer = PMF()
        if len(xs) == 1:
            arg = xs[0]
            if isinstance(arg, int):
                n = arg
                p = 1.0 / n
                for x in Sequence(0, n-1):
                    answer[x] = p
                return answer
            else:
                raise ValueError('args must be either a single int or a sequence of labels')
        p = 1.0 / len(xs)
        for x in xs:
            answer[x] = p
        return answer

    @staticmethod
    def Power(xs, alpha):
        answer = PMF()
        for x in xs:
            answer[x] = x ** (-alpha)
        return answer.Normalise()

    @staticmethod
    def Gaussian(mu, sigma, num_sigmas, n):
        answer = PMF()
        low = mu - num_sigmas * sigma
        high = mu + num_sigmas * sigma
        for x in Sequence(low, high, n):
            p = scipy.stats.norm.pdf(x, mu, sigma)
            answer[x] = p
        return answer.Normalise()

    @staticmethod
    def FromPdf(xs, pdf):
        answer = PMF()
        for x in xs:
            p = pdf.Density(x)
            if isinstance(p, (list, np.ndarray)):
                p = p[0]
            answer[x] = p
        return answer.Normalise()

    @staticmethod
    @Pipeable
    def Kde(xs, data):
        pdf = scipy.stats.gaussian_kde(data)
        answer = PMF()
        for x in xs:
            answer[x] = pdf.evaluate(x)[0]
        return answer.Normalise()


    __slots__ = '_cmf'

    def __init__(self, *args, **kwargs):
        object.__setattr__(self, '_cmf', None)
        a = dict(PoDType='PMF')
        a.update(kwargs)
        if len(args) == 2 and hasattr(args[0], '__iter__') and  hasattr(args[1], '__iter__') and len(args[0]) == len(args[1]):
            args = zip(*args)
        try:
            super(PMF, self).__init__(*args, **a)
        except:
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


@Pipeable
def Mix(*argsOrListOfArgs):
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
def CalcPosterior(prior, likelihood):
    if isinstance(prior, PMF):
        p_times_l = prior * likelihood
        return p_times_l >> Normalised
    else:
        raise ValueError('Unhandled prior type %s' % str(type(prior)))

Update = CalcPosterior


def Sequence(first, last, n=Missing, step=Missing):
    # TODO move somewhere else
    if step is Missing and n is Missing:
        return list(range(first, last+1, 1))
    elif step is Missing:
        return list(np.linspace(first, last, n))
    elif n is Missing:
        return list(np.arange(first, last + step, step))
    else:
        raise TypeError('Must not specify n and step')



d6 = PMF.Uniform(*Sequence(1, 6))
d8 = PMF.Uniform(*Sequence(1, 8))
d10 = PMF.Uniform(*Sequence(1, 10))
d12 = PMF.Uniform(*Sequence(1, 12))
d20 = PMF.Uniform(*Sequence(1, 20))



