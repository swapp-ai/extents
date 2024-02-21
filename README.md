# Extents - An Intervals Library in Pure Python

`extents` is an intervals library implemented in pure python. 
It draws its inspiration from the [`PyInterval`](https://pyinterval.readthedocs.io/en/latest/) 
library ([github](https://github.com/taschini/pyinterval)).

This library is capable of representing open, closed and semi-open/closed intervals.
It also supports set operations on intervals (i.e., union, intersection and complement).


## Examples:

### Basic use cases:

Basic use of this library includes creating simple intervals, and manipulating them 
through set operations


```python
from extents import interval        # the interval class represents a collection of intervals

ival1 = interval([0, 1])            # the singleton interval set containing the closed interval [0, 1]
print(ival1)                        # Interval([0, 1])
print(~ival1)                       # Interval((-inf, 0), (1, inf)) -- the interval set of (-inf, 0) and (1, inf) -- 
                                    # which compose the complement of [0, 1]

ival2 = interval((4, 5))            # the singleton interval set containing the open interval (4, 5)
print(ival2)                        # Interval((4, 5))
print(~ival2)                       # Interval((-inf, 4], [5, inf)) -- the interval set of (-inf, 4] and [5, inf) --
                                    # which are the complement of (4, 5)]

ival3 = interval([0, 1], [5, 6])    # the interval set [0, 1] and [5, 6]
ival4 = interval([0, 3], [4, 5.5])  # the interval set [0, 3] and [4, 5.5]
print(ival3 | ival4)                # the interval set [0, 3] and [4, 6], which is the union of ival3 and ival4
print(ival3 & ival4)                # the interval set [0, 1] and [5, 5.5], which is the intersection of ival3 and ival4

ival5 = interval([0, 1], [0.5, 3])  # intervals are automatically union-ed during construction.
print(ival5)                        # resulting in the interval [0, 3]
```

The output of the commands above would be:

```
Interval([0, 1])
Interval((-inf, 0), (1, inf))
Interval((4, 5))
Interval((-inf, 4], [5, inf))
Interval([0, 3], [4, 6])
Interval([0, 1], [5, 5.5])
Interval([0, 3])
```

### Advanced use cases:

In order to construct a semi-open interval, you can import the `Component` and `ComponentType`,
and construct the internal interval components.

For example,
```python
from extents import interval, Component, ComponentType

ival = interval(Component(0, 1, ComponentType.HALF_CLOSED_LEFT),
                Component(5, 6, ComponentType.HALF_CLOSED_RIGHT)
                )
print(ival)  # construct the interval set: [0, 1), (5, 6]
```

### Additional Examples:

See the `tests/extents_test.py` file. 

## Installation:

From `github`:
```shell
$ pip install git+https://github.com/swapp-ai/extents
```

From source:
```shell
$ git clone https://github.com/swapp-ai/extents
$ cd extents
$ pip install .
```
