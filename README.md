### Batteries


#### Pipeable

This decorator extends functions with the >> and << opertors with the effect of adding pipeline like behaviour (e.g. similar to |> in F#).

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
def each(xs, f):
    return [f(x) for x in xs]

@Pipeable
def chain(seed, xs, f):
    prior = seed
    for x in xs:
        prior = f(prior, x)
    return prior

@Pipeable
def squareIt(x):
    return x * x

@Pipeable
def add(x, y):
    return x + y


actual = [1,2,3] >> each >> squareIt >> chain(seed=0) >> add
expected = 14
assert actual == expected
```
