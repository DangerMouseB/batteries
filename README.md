### coppertop


#### pipeable

This Pipeable decorator extends functions with the >> and << opertors with the effect of adding pipeline like behaviour (e.g. similar to |> in F#).

x >> f   and   f >> x   both answer f(x)\
x << f   calls f(x) and answers x\
f << x   calls f(x) and answers f

or equivalently,\
lhs >> rhs   answers f(x)\
lhs << rhs   calls f(x) and answers the lhs

Example:

```
from batteries import Pipeable

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

See batteries/tests/test_pipeable.py for a fuller description and example code.

#### ranges

D style ranges in python - see batteries/examples/format_calendar.py and batteries/examples/tests/test_format_calendar.py

