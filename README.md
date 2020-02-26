### coppertop

The coppertop package has two key features, a piping opertor and D 
language style ranges. I have found these useful for writing code in a piping style (i.e. 
in a smalltalk / kdb / functional manner).

The quickest and most effective way of gaining an understanding of the 
codebase is to start up your favourite debugger (e.g. PyCharm) and dive straight into
 the following:

**pipeable** \
follow the _overview_ test in coppertop/tests/test_pipeable.py

**ranges**
1. coppertop/examples/count_lines_jsp.py and coppertop/examples/tests/test_count_lines_jsp.py 
solve the jsp problem described in https://en.wikipedia.org/wiki/Jackson_structured_programming

2. coppertop/examples/format_calendar.py and coppertop/examples/tests/test_format_calendar.py
solve the calendar printing problem described in https://wiki.dlang.org/Component_programming_with_ranges


#### pipeable

The *Pipeable* decorator extends functions with the >> and << operators with the effect 
of adding pipeline like behaviour (e.g. similar to |> in F#).

x >> f   and   f >> x   both answer f(x)\
x << f   calls f(x) and answers x\
f << x   calls f(x) and answers f

or equivalently,\
lhs >> rhs   answers f(x)\
lhs << rhs   calls f(x) and answers the lhs

Example:

```
from coppertop import Pipeable

@Pipeable
def Each(xs, f):
    return [f(x) for x in xs]

@Pipeable
def Chain(seed, xs, f):
    prior = seed
    for x in xs:
        prior = f(prior, x)
    return prior

@Pipeable
def SquareIt(x):
    return x * x

@Pipeable
def Add(x, y):
    return x + y


actual = [1,2,3] >> Each >> SquareIt >> Chain(seed=0) >> Add
expected = 14
assert actual == expected
```

Addtionally functions that are decorated with Pipeable can easily be 
made partial by providing some of the arguments, for example 
`Chain(seed=0)` in the code above.


#### ranges

Using D style ranges is similar to programming with a non-reactive 
pull style DAG.  Debugging an apparently simple sequence such as 

```
def test_checkNumberOfDaysInEachMonth():
    2020 >> DatesInYear \
        >> MonthChunks \
        >> Materialise >> Each >> Len \
        >> AssertEqual >> [31,29,31,30,31,30,31,31,30,31,30,31]
```

is similar to DAG debugging in that you need to have breakpoints in many places 
and code can be hard to step through. 

However the the range implementation in D has a key redeeming feature.

The input and output types are not fixed as in typical DAG implementations 
so each range is easier to test and reason about in isolation. Thus they can
be composed more easily in longer pipelines and with a higher degree of confidence.

