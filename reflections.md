### Introduction

The ideas and way they are implemented in pipeable.py and ranges.py have the 
potential to (profoundly) change the way a piece of code is thought about - which is part 
of the reason for writing them in the first place.

Here I will, somewhat narcissistically, reflect on those changes.

<br>

### Pipeable multi-dispatch - dog-typing vapourware - understanding type inheritance differently

To paraphrase Steve Cook - an object's class defines it's structure, a type an 
object can belong too defines the object's role the system.

In Java we have two sort of inheritance - implementation inheritance and 
interface inheritance. It's an attempt to separate type from structure.

e.g. IC is inherited by IA and IB, and CC is inherited by CA and CB, the C's 
can implement the I's.

---
#### An aside on implementation inheritance

As an aside, I find frameworks that share code via inheritance really hard to 
follow - indeed I wrote the Pipeable decorator because I was learning Bayesian 
stats and couldn't reuse Allen Downey's class based code from Think Bayes and 
wanted a clearer way of working in the domain.

Another current case in point is the implementation Jupyter kernels in Python - in 
order to implement my own kernel I must subclass ipykernel.kernelbase.Kernel 
and the overall inheritance hierarchy looks thus:

```
class MyKernel(Kernel)
  ipykernel.kernelbase >> class Kernel(SingletonConfigurable)
    traitlets.config.configurable >> class SingletonConfigurable(LoggingConfigurable)
      traitlets.config.configurable >> class LoggingConfigurable(Configurable)
        traitlets.config.configurable >> class Configurable(HasTraits)
          traitlets.traitlets >> class HasTraits(six.with_metaclass(MetaHasTraits, HasDescriptors))
            traitlets.traitlets >> class MetaHasTraits(MetaHasDescriptors)
              traitlets.traitlets >> class MetaHasDescriptors(type)
            traitlets.traitlets >> class HasDescriptors(six.with_metaclass(MetaHasDescriptors, object))
              traitlets.traitlets >> class MetaHasDescriptors(type)
```

(It's so complicated I made several mistakes just trying to browser the code and write it down).

That's a lot to follow for an object that implements a very basic request response 
interface. The ipython message protocol documentation reflects a similar bias towards 
complication, yet thank goodness the authors did a good enough job to get 
IPython and Jupyter so widely used.

Lessons Learned - [The Zen of Python](https://www.python.org/dev/peps/pep-0020/) 
has a good point *"Flat is better than nested"* and the rest.

---

So let's consider two completely different implementations for a date type - TA an integer 
offset from an epoch, and TB three integers representing year, month and date.

Let's also consider a comparison operator for sorting LessThan()

We're familiar with the deign decision in our object oriented world, e.g. we can have 
CA and CB implementing ILessThan, and we know how much those decisions bind us in 
knots, so let's try something different.

In python we can suggest there is a conceptual union of TA and TB with the following 
function signatures for example:

```
def LessThan(a, b):
    assert type(a) == type(b)
    if isinstance(a, TA):
        return _TALessThan(a, b)
    elif isinstance(a, TA):
        return _TALessThan(a, b)
    
def _TALessThan(a, b)
    assert isinstance(a, TA)
    assert isinstance(b, TA)
    return a.offset < b.offset

def _TBLessThan(a, b)
    assert isinstance(a, TA)
    assert isinstance(b, TA)
    if a.year < b.year: return True
    if a.year > b.year: return False
    if a.month < b.month: return True
    if a.month > b.month: return False
    if a.day < b.day: return True
    if a.day > b.day: return False
    return False
```

I'm going to make up the term dog-typing since dogs, in the real world, have exogenously  
(human) given roles (aka types). We still have the duck-type and specialisation of breed 
but we also can usefully define pet-dogs, police-dogs, sheep-dogs, etc, (and if we 
believe Hollywood's film Babe there are also sheep-pigs and presumably sheep-ducks, etc).

So in a similar vein, let's consider TA to be like dog, TB to be like a pig and 
LessThan to be a sheep based activity, but applied to comparing dates.

With the Pipeable we can do this:

```
@Pipeable(a=TA, b=TA)
def LessThan(a, b):
    # assert isinstance(a, TA) - done by the decorator machinery in order to dispatch
    # assert isinstance(b, TA)
    return a.offset < b.offset

@Pipeable(a=TB, b=TB)
def LessThan(a, b):
    # assert isinstance(a, TB)
    # assert isinstance(b, TB)
    if a.year < b.year: return True
    if a.year > b.year: return False
    if a.month < b.month: return True
    if a.month > b.month: return False
    if a.day < b.day: return True
    if a.day > b.day: return False
    return False
```

if we define TC as the union of TA & TB then we can also have:

```
@Pipeable(dates=Union(Tuple(TC), List(TC)))
def sortDates(dates):
    ...
    if a >> LessThan >> b:
    ...
```

sortDates will accept only arrays type TC or subtypes of TC.

To me I find these concept central in the code of ParcPlace's VisualWorks (i.e. 
Smalltalk-80).

Is this possible (and easy in Java or C++)? 

I suspect this is a more "functional" way of seeing types, but I'm not sure. Bones 
should be able to statically and dynamically type in this manner. 

Notice we didn't have to make any changes to the implementation of TA and TB in order 
to do this. The typing hierarchy is a property of functions not objects and independent 
of the structural hierarchy of PoD structs (acka objects).

Also we can define cross operations, e.g. LessThan(TA, TB) where one or both of the 
types is converted, which is harder to implement with traditional OO.

I don't know where the idea came from of lumping some behaviour with data got 
conflated with the rule that ALL behaviour that relates to some type of data must be 
lumped with that data, but it has proved mischievous. Smalltalk had first-class 
behaviour and things that served as control structures (higher order functiona) as 
do functional languages. Why this wasn't part of Java to start
with I can only guess but it's taken 20 years to correct the mistake.


Pipeable either needs a rule, such as left to right concrete to abstract bind, or the 
ability to detect ambiguity at module compilation time, for cases such as:

```
@Pipeable(a=TC, b=TA)
def LessThan(a, b):
    ...

@Pipeable(a=TA, b=TC)
def LessThan(a, b):
    ...
```

Finally I wonder how this works in Julia and using templates in D and C++ or 
generics in Java.

#### Conclusion

Behaviour and properties that are dog like (similarly offset, year, month and day) can 
stay with the dog, and behaviours that are exogenously defined such as shepherding 
(similarly LessThan) should be exogenous to the dog. 

The ways of thinking and knowing to handle this do need to be fostered. 







