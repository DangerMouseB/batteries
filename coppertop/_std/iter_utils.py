# *******************************************************************************
#
#    Copyright (c) 2017-2020 David Briant
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
# *******************************************************************************



from ..pipeable import Pipeable


# iter iteration (rather than range iteration)

@Pipeable
def Each(xs, f):
    """each(xs, f)  e.g. xs >> Each >> f
    Answers [f(x) for x in xs]"""
    return [f(x) for x in xs]

@Pipeable
def EachIf(xs, f, ifF):
    """each(xs, f)  e.g. xs >> EachIf >> f >> ifF
    Answers [f(x) for x in xs]"""
    return [f(x) for x in xs if ifF(x)]

@Pipeable
def Chain(seed, xs, f):
    """chain(seed, xs, f)    e.g. xs >> Chain(seed) >> f
    Answers resultn where resulti=f(prior, xi) for each x in xs
    prior = resulti-1 or seed initially"""
    prior = seed
    for x in xs:
        prior = f(prior, x)
    return prior

@Pipeable
def EachArgs(listOfArgs, f):
    """eachArgs(f, listOfArgs)
    Answers [f(*args) for args in listOfArgs]"""
    return [f(*args) for args in listOfArgs]
