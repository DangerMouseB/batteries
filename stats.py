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


# 3rd party imports
import numpy as np
import scipy.stats


# local imports
from .pipeable import MoreArgsRequiredException, Pipeable
from .structs import PoD, PoDGroup, Absent, NA

__all__ = ['PMF', 'd6', 'd8', 'd10', 'd12', 'd20', 'Mix', 'Sum', 'Mean', 'N', 'Avg', 'ExpectationOf', 'EX',
           'Normalised', 'MakeKdePMF', 'RvAdd', 'RvSub', 'CalcPosterior', 'Chained', 'PoissonProb', 'Update']


# PMF xs are the values of a RV, and ys are it's probability
# PMF has mean, median(s), stdev, percentile, CDF, etc
# Bayes operates on the probs of the RV not the values - f(x) * g(x) / h(x)
# or (even clearer?) f(v) * g(v) / h(v)

class PMF(PoD):
    @staticmethod
    def Uniform(*args):
        # if a single int it is a count else there must be many keys
        answer = PMF()
        if len(args) == 1:
            arg = args[0]
            if isinstance(arg, int):
                n = arg
                p = 1.0 / n
                for i in range(n):
                    answer.Add(p)
                return answer
            else:
                raise ValueError('args must be either a single int or a sequence of labels')
        p = 1.0 / len(args)
        for arg in args:
            answer[arg] = p
        return answer

    @staticmethod
    def Power(n, alpha):
        answer = PMF()
        for i in range(n):
            answer.Add((i + 1.0) ** (-alpha))
        return answer >> Normalised

    @staticmethod
    def FromPdf(xs, pdf):
        answer = PMF()
        for x in xs:
            y = pdf.Density(x)
            if isinstance(y, (list, np.ndarray)):
                y = y[0]
            answer[x] = y
        return answer >> Normalised

    __slots__ = '_cmf'

    def __init__(self, *args, **kwargs):
        object.__setattr__(self, '_cmf', None)
        a = dict(PoDType='PMF')
        a.update(kwargs)
        super().__init__(*args, **a)

    def __setattr__(self, name, value):
        object.__setattr__(self, '_cmf', None)
        super().__setattr__(name, value)

    def __setitem__(self, key, value):
        object.__setattr__(self, '_cmf', None)
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
            cmf = np.array(list(self._KvIter()))
            cmf[:, 1] = np.cumsum(cmf[:, 1])
            object.__setattr__(self, '_cmf', cmf)
        return cmf

    def XsPs(self):
        xs, ps = [], []
        for x, p in self._KvIter():
            xs.append(x)
            ps.append(p)
        return xs, ps


d6 = PMF.Uniform(*range(1, 7))
d8 = PMF.Uniform(*range(1, 9))
d10 = PMF.Uniform(*range(1, 11))
d12 = PMF.Uniform(*range(1, 13))
d20 = PMF.Uniform(*range(1, 21))



@Pipeable
def Mix(*args):
    if len(args) == 1:
        if isinstance(args[0], list):
            args = args[0]
    if len(args) < 2:
        raise MoreArgsRequiredException()
    answer = PMF()
    for arg in args:
        if isinstance(arg, tuple):
            beta, pmf = arg
        else:
            beta = 1.0
            pmf = arg
        for k, v in pmf.KvIter():
            answer[k] += beta * v
    return answer >> Normalised


@Pipeable
def Sum(summable):
    if isinstance(summable, PoD):
        return _Sum(list(summable))
    elif isinstance(summable, PoDGroup):
        return _Sum(summable._values)
    else:
        return np.sum(summable)

def _Sum(values, ignoreAbsent=False):
    answer = NA
    if ignoreAbsent:
        for v in values:
            if v is not Absent:
                if answer is NA:
                    answer = v
                else:
                    answer += v
    else:
        for v in values:
            if answer is NA:
                answer = v
            else:
                answer += v
    return NA if answer is NA else 1.0 * answer


@Pipeable
def N(countable):
    if isinstance(countable, PoD):
        return _N(list(countable))
    elif isinstance(countable, PoDGroup):
        return _N(countable._values)
    else:
        return len(countable)

def _N(values, ignoreAbsent=False):
    answer = NA
    if ignoreAbsent:
        for v in values:
            if v is not Absent:
                if answer is NA:
                    if v is not NA:
                        answer = 1
                else:
                    if v is not NA:
                        answer += 1
    else:
        for v in values:
            if answer is NA:
                if v is not NA:
                    answer = 1
            else:
                if v is not NA:
                    answer += 1
    return answer


@Pipeable
def Avg(numberSequence):
    return Sum(numberSequence) / N(numberSequence)

@Pipeable
def ExpectationOf(pmf):
    assert isinstance(pmf, PMF)
    answer = NA
    for x, p in pmf._KvIter():
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
def MakeKdePMF(lower, upper, n, values):
    pdf = scipy.stats.gaussian_kde(values)
    answer = PMF()
    for x in np.linspace(lower, upper, n):
        answer[x] = pdf.evaluate(x)[0]
    return answer >> Normalised

@Pipeable
def RvAdd(lhs, rhs):
    answer = PMF()
    for k1, p1 in lhs.KvIter():
        for k2, p2 in rhs.KvIter():
            answer[k1 + k2] += p1 * p2
    return answer >> Normalised

@Pipeable
def RvSub(lhs, rhs):
    answer = PMF()
    for k1, p1 in lhs.KvIter():
        for k2, p2 in rhs.KvIter():
            answer[k1 - k2] += p1 * p2
    return answer >> Normalised


@Pipeable
def CalcPosterior(prior, likelihood):
    if isinstance(prior, PMF):
        p_times_l = prior * likelihood
        return p_times_l >> Normalised
    else:
        raise ValueError('Unhandled prior type %s' % str(type(prior)))

Update = CalcPosterior



def Chained(x, args, fn):
    for arg in args:
        x = fn(x, arg)
    return x



def PoissonProb(k, lam):
    return scipy.stats.poisson.pmf(k, lam)