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
from numbers import Number

# 3rd party imports
import numpy as np
import scipy.stats

# local imports
from .pipeable import MoreArgsRequiredException, Pipeable
from .structs import PoD, NA, Sum
from .useful import Sequence
from .missing import Missing


__all__ = ['PMF', 'd6', 'd8', 'd10', 'd12', 'd20', 'Mix', 'Mean', 'ExpectationOf', 'EX',
           'Normalised', 'RvAdd', 'RvSub', 'RvDiv', 'RvMul', 'RvMax', 'UpdatePrior', 'Sequence', 'VarOf', 'Var',
           'SkewOf', 'Skew', 'ToXY']

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
        answer = PoD()
        for x in xs:
            answer[x] = x ** (-alpha)
        return answer >> Normalised

    @staticmethod
    def Gaussian(mu, sigma, xs_or_num_sigmas, n=Missing):
        """
        e.g. PMF.Gaussian(0, 1, Sequence(-3, 3, step=0.1))
        e.g. PMF.Gaussian(0, 1, 3, 60)
        :param mu: 
        :param sigma: 
        :param xs_or_num_sigmas: 
        :param n: 
        :return: 
        """
        if n is not Missing:
            xs = Sequence(mu, sigma, sigmas=xs_or_num_sigmas, n=n)
        else:
            xs = xs_or_num_sigmas
        answer = PoD()
        for x in xs:
            p = scipy.stats.norm.pdf(x, mu, sigma)
            answer[x] = p
        return answer >> Normalised

    @staticmethod
    def Poisson(lamb, N):
        answer = PoD()
        for x in range(N):
            p = scipy.stats.poisson.pmf(x, lamb)
            answer[x] = p
        return answer >> Normalised

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
        answer = PoD()
        for x in xs:
            p = pdf(x)
            if isinstance(p, (list, np.ndarray)):
                p = p[0]
            answer[x] = p
        return answer >> Normalised

    @staticmethod
    @Pipeable
    def Kde(xs, data):
        pdf = scipy.stats.gaussian_kde(data)
        answer = PoD()
        answer._kde = pdf
        for x in xs:
            answer[x] = pdf.evaluate(x)[0]
        return answer >> Normalised

    @staticmethod
    @Pipeable
    def FromSample(xs):
        answer = PoD()
        for x in xs:
            answer[x, 0] += 1
        return answer >> Normalised


    __slots__ = '_cmf', '_kde'

    def __init__(self, *args, **kwargs):
        ""
        object.__setattr__(self, '_cmf', None)
        object.__setattr__(self, '_kde', None)
        a = dict(PoDType='PMF')
        a.update(kwargs)
        if len(args) == 2 and hasattr(args[0], '__iter__') and  hasattr(args[1], '__iter__') and len(args[0]) == len(args[1]) and len(args[0]) != 2:
            raise Exception("PMF(ks, vs) is no longer allowed")
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


@Pipeable(minNumArgs=2)
def Mix(*argsOrListOfArgs):
    """Mix(*argsOrListOfArgs) where arg is (beta, pmf) or pmf (beta is assumed to be 1.0)"""
    if len(argsOrListOfArgs) == 1 and isinstance(argsOrListOfArgs[0], list):
            args = argsOrListOfArgs[0]
    else:
        args = argsOrListOfArgs
    if len(args) < 2:
        raise MoreArgsRequiredException()
    result = {}
    for arg in args:
        beta, pmf = arg if isinstance(arg, tuple) else (1.0, arg)
        for x, p in pmf.KvIter():
            result[x] = result.setdefault(x, 0) + beta * p
    return PMF(*_sortAndNormaliseVPs(list(result.items())))


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


def _normaliseKNumVs(kvs):
    '''In place normalisation so total probability equals 1.0 - avoiding labels'''
    sum = 0.0
    for k, v in kvs:
        if isinstance(v, Number):
            sum += v
    for i, kv in enumerate(kvs):
        if isinstance(kv[1], Number):
            kvs[i] = (kv[0], kv[1] / sum)
    return kvs


def _normaliseVPs(vps):
    '''In place normalisation so total probability equals 1.0'''
    sum = 0.0
    for _, p in vps:
        sum += p
    for i, vp in enumerate(vps):
        vps[i] = (vp[0], vp[1] / sum)
    return vps


def _sortAndNormaliseVPs(vps):
    vps.sort(key=lambda vp: vp[0])
    _normaliseVPs(vps)
    return vps


@Pipeable
def Normalised(pod):
    return PMF(*_normaliseKNumVs(pod.KVs()))


@Pipeable
def RvAdd(lhs, rhs):
    if not isinstance(lhs, PMF): raise TypeError('lhs mist be a PMF')
    if not isinstance(rhs, PMF): raise TypeError('rhs mist be a PMF')
    result = {}
    for x1, p1 in lhs.KNumVs():
        for x2, p2 in rhs.KNumVs():
            k = x1 + x2
            result[k] = result.setdefault(k, 0.0) + p1 * p2
    return PMF(*_sortAndNormaliseVPs(list(result.items())))


@Pipeable
def RvSub(lhs, rhs):
    if not isinstance(lhs, PMF): raise TypeError('lhs mist be a PMF')
    if not isinstance(rhs, PMF): raise TypeError('rhs mist be a PMF')
    result = {}
    for x1, p1 in lhs.KNumVs():
        for x2, p2 in rhs.KNumVs():
            k = x1 - x2
            result[k] = result.setdefault(k, 0.0) + p1 * p2
    return PMF(*_sortAndNormaliseVPs(list(result.items())))


@Pipeable
def RvDiv(lhs, rhs):
    if not isinstance(lhs, PMF): raise TypeError('lhs mist be a PMF')
    if not isinstance(rhs, PMF): raise TypeError('rhs mist be a PMF')
    result = {}
    for x1, p1 in lhs.KNumVs():
        for x2, p2 in rhs.KNumVs():
            k = x1 / x2
            result[k] = result.setdefault(k, 0.0) + p1 * p2
    return PMF(*_sortAndNormaliseVPs(list(result.items())))


@Pipeable
def RvMul(lhs, rhs):
    if not isinstance(lhs, PMF): raise TypeError('lhs mist be a PMF')
    if not isinstance(rhs, PMF): raise TypeError('rhs mist be a PMF')
    result = {}
    for x1, p1 in lhs.KNumVs():
        for x2, p2 in rhs.KNumVs():
            k = x1 * x2
            result[k] = result.setdefault(k, 0.0) + p1 * p2
    return PMF(*_sortAndNormaliseVPs(list(result.items())))


@Pipeable
def RvMax(lhs, rhs):
    if not isinstance(lhs, PMF): raise TypeError('lhs mist be a PMF')
    if not isinstance(rhs, PMF): raise TypeError('rhs mist be a PMF')
    result = {}
    for x1, p1 in lhs.KNumVs():
        for x2, p2 in rhs.KNumVs():
            k = x1 if x1 > x2 else x2
            result[k] = result.setdefault(k, 0.0) + p1 * p2
    return PMF(*_sortAndNormaliseVPs(list(result.items())))


@Pipeable(minNumArgs=2)
def UpdatePrior(arg1, arg2, arg3=sys):
    """UpdatePrior(arg1, arg2, [arg3])
    if UpdatePrior(likelihoodFn, priorPmf, data) return priorPmf * likelihoodFn(data) >> Normalised
    if UpdatePrior(priorPmf, likelihoodPmf) answer priorPmf * likelihoodPmf >> Normalised"""
    if isinstance(arg1, PMF) and arg3 == sys:
        return arg1 * arg2 >> Normalised
    else:
        return arg2 * arg1(arg3)  >> Normalised


@Pipeable
def ToXY(pod):
    return tuple(zip(*pod.KNumVs()))



d4 = PMF.Uniform(*Sequence(1, 4))
d6 = PMF.Uniform(*Sequence(1, 6))
d8 = PMF.Uniform(*Sequence(1, 8))
d10 = PMF.Uniform(*Sequence(1, 10))
d12 = PMF.Uniform(*Sequence(1, 12))
d20 = PMF.Uniform(*Sequence(1, 20))



