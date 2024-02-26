from __future__ import annotations

import math
import numbers
import operator
from abc import ABCMeta
from bisect import bisect_left, bisect_right
from dataclasses import dataclass
from enum import Enum
from itertools import chain, groupby
from typing import TypeVar, Sequence, List, Union, Tuple, Callable, Iterable, Any

from more_itertools import pairwise


__all__ = [
    'Component',
    'ComponentType',
    'Interval',
    'interval'
]


_T = TypeVar('_T', bound=numbers.Number)


def _group_by_len(iterable: Iterable[_T], chunk_size: int = 2) -> Iterable[_T]:
    """ _group_by_len(iterable: Iterable[_T], chunk_size: int = 2) -> Iterable[_T]

        group the items in iterable to groups of size chunk_size.
        For example,
            >>> list(_group_by_len(range(10), chunk_size=2))
            [(0, 1), (2, 3), (4, 5), (6, 7), (8, 9)]

        Notice that ``group_by_len`` returns an iterable object - not a list.
        please convert to list as needed.
    """
    return zip(*[iter(iterable)] * chunk_size)


class ComponentType(Enum):
    CLOSED = (0, '[', ']', operator.le, operator.le)  # [a, b] interval
    OPEN = (1, '(', ')', operator.lt, operator.lt)  # (a, b) interval
    HALF_CLOSED_LEFT = (2, '[', ')', operator.le, operator.lt)  # [a, b) interval
    HALF_CLOSED_RIGHT = (3, '(', ']', operator.lt, operator.le)  # (a, b] interval
    HALF_OPEN_LEFT = HALF_CLOSED_RIGHT
    HALF_OPEN_RIGHT = HALF_CLOSED_LEFT
    OPEN_CLOSED = HALF_CLOSED_RIGHT
    CLOSED_OPEN = HALF_CLOSED_LEFT

    @property
    def open_parens(self) -> str:
        return self.value[1]

    @property
    def closing_parens(self) -> str:
        return self.value[2]

    @property
    def parens(self) -> Tuple[str, str]:
        return self.open_parens, self.closing_parens

    @property
    def left_compare(self) -> Callable[..., bool]:
        return self.value[3]

    @property
    def right_compare(self) -> Callable[..., bool]:
        return self.value[4]

    def __invert__(self) -> ComponentType:
        cls = ComponentType
        if cls.CLOSED is self:
            return cls.OPEN
        elif cls.OPEN is self:
            return cls.CLOSED
        elif cls.HALF_CLOSED_LEFT is self:
            return cls.HALF_CLOSED_RIGHT
        elif cls.HALF_CLOSED_RIGHT is self:
            return cls.HALF_CLOSED_LEFT
        else:
            raise TypeError(f'{cls.__name__}: unknown component type {self}')

    @classmethod
    def get(cls, is_left_closed: bool, is_right_closed: bool) -> ComponentType:
        if is_left_closed and is_right_closed:
            return ComponentType.CLOSED
        elif not is_left_closed and not is_right_closed:
            return ComponentType.OPEN
        elif is_left_closed and not is_right_closed:
            return ComponentType.HALF_CLOSED_LEFT
        else:
            return ComponentType.HALF_CLOSED_RIGHT

    @classmethod
    def get_from_name(cls, name: str) -> ComponentType:
        try:
            return cls._COMPONENT_TYPE_ALIASES[name]
        except Exception as ex:
            raise ValueError(f'Unknown component type `{name}`.') from ex


ComponentType._COMPONENT_TYPE_ALIASES = {
    # closed interval [a, b]
    'closed': ComponentType.CLOSED,
    '[]': ComponentType.CLOSED,
    '[_]': ComponentType.CLOSED,

    # open interval (a, b)
    'open': ComponentType.OPEN,
    '()': ComponentType.OPEN,
    '(_)': ComponentType.OPEN,

    # left closed interval [a, b)
    'closedopen': ComponentType.HALF_CLOSED_LEFT,
    'closed_open': ComponentType.HALF_CLOSED_LEFT,
    'half_closed_left': ComponentType.HALF_CLOSED_LEFT,
    'half_open_right': ComponentType.HALF_CLOSED_LEFT,
    '[)': ComponentType.HALF_CLOSED_LEFT,

    # left open interval (a, b]
    'openclosed': ComponentType.HALF_CLOSED_RIGHT,
    'open_closed': ComponentType.HALF_CLOSED_RIGHT,
    'half_open_left': ComponentType.HALF_CLOSED_RIGHT,
    'half_closed_right': ComponentType.HALF_CLOSED_RIGHT,
    '(]': ComponentType.HALF_CLOSED_RIGHT,
}


@dataclass
class Component(Sequence[_T]):
    inf: _T
    sup: _T
    type: ComponentType | str = ComponentType.CLOSED

    def __post_init__(self) -> None:
        if isinstance(self.type, str):
            self.type = ComponentType.get_from_name(self.type)

    @property
    def length(self) -> float:
        return self.sup - self.inf

    # @property
    # def inf(self) -> _T:
    #     return self._inf

    @property
    def inf_inv(self) -> _T:
        return 1/self.inf

    # @property
    # def sup(self) -> _T:
    #     return self._sup

    @property
    def sup_inv(self) -> _T:
        return 1/self.sup

    @property
    def is_open(self) -> bool:
        return ComponentType.OPEN is self.type

    @property
    def is_closed(self) -> bool:
        return ComponentType.CLOSED is self.type

    @property
    def is_left_closed(self) -> bool:
        return self.is_closed or ComponentType.HALF_CLOSED_LEFT is self.type

    @property
    def is_left_open(self) -> bool:
        return self.is_open or ComponentType.HALF_OPEN_LEFT is self.type

    @property
    def is_right_closed(self) -> bool:
        return self.is_closed or ComponentType.HALF_CLOSED_RIGHT is self.type

    @property
    def is_right_open(self) -> bool:
        return self.is_open or ComponentType.HALF_OPEN_RIGHT is self.type

    @property
    def _compare_key(self) -> Tuple[float, float]:
        return self.inf, self.sup

    def __contains__(self, value: _T) -> bool:
        return self.type.left_compare(self.inf, value) and self.type.right_compare(value, self.sup)

    def __len__(self) -> int:
        return 2

    def __getitem__(self, index: int) -> _T:
        if index == 0:
            return self.inf
        elif index == 1:
            return self.sup
        else:
            raise IndexError(index)

    def __repr__(self) -> str:
        return f'{type(self).__name__}({self.inf}, {self.sup}, {self.type})'

    def __str__(self) -> str:
        if self.inf == self.sup:
            return f'{self.type.open_parens}{self.inf}{self.type.closing_parens}'
        else:
            return f'{self.type.open_parens}{self.inf}, {self.sup}{self.type.closing_parens}'

    @classmethod
    def are_continuous(cls, comp1: Component[_T], comp2: Component[_T]) -> bool:
        return comp1.type.right_compare(comp2.inf, comp1.sup) or comp2.type.left_compare(comp2.inf, comp1.sup)
        # return comp2.inf in comp1

    @classmethod
    def create(cls, from_value, copy: bool = False) -> Component[_T]:
        if isinstance(from_value, Component):
            return from_value if not copy else Component(from_value.inf, from_value.sup, from_value.type)
        elif isinstance(from_value, Sequence):
            n = len(from_value)
            assert 1 <= n <= 3, from_value
            if n == 1:
                from_value = (from_value, from_value) if isinstance(from_value, tuple) else list(from_value)*2

            if n == 2:
                if isinstance(from_value, tuple):
                    return Component(*from_value, type=ComponentType.OPEN)
                else:
                    return Component(*from_value)
            else:
                return Component(*from_value)
        elif isinstance(from_value, numbers.Number):
            return Component(from_value, from_value)
        elif isinstance(from_value, Iterable) and not isinstance(from_value, str):
            return Component(*list(from_value))
        else:
            raise TypeError(f'Cannot create {cls.__name__} from value `{from_value}`')

    @classmethod
    def from_extrema(cls, comp1: Component[_T], comp2: Component[_T]) -> Component[_T]:
        inf = comp1.inf
        sup = comp2.sup
        left = comp1.is_left_closed
        right = comp2.is_right_closed
        return cls(inf, sup, ComponentType.get(left, right))


class MetaInterval(ABCMeta, type):
    def __getitem__(cls, item) -> Interval[_T]:
        return cls(list(item) if isinstance(item, tuple) else item)


class Interval(Sequence[Component[_T]], metaclass=MetaInterval):
    _comps: List[Component[_T]]
    _endpoints: List[_T]

    def __init__(self, *components) -> None:
        components = [Component.create(comp) for comp in components]
        components = sorted(components, key=operator.attrgetter('_compare_key'))

        if len(components) <= 1:
            self._endpoints = sum([[comp.inf, comp.sup] for comp in components], [])
            self._comps = components
            return

        partition = [[]]
        for comp1, comp2 in pairwise(chain(components, [components[-1]])):
            partition[-1].append(comp1)
            if not Component.are_continuous(comp1, comp2):
                partition.append([])

        components = []
        for part in partition:
            inf = part[0]
            sup = max(part, key=operator.attrgetter('sup'))
            components.append(Component.from_extrema(inf, sup))

        self._comps = components
        self._endpoints = sum([[comp.inf, comp.sup] for comp in components], [])

    @classmethod
    def _from_valid_values(cls, values: Iterable, from_endpoints: bool = True) -> Interval[_T]:
        result = cls()
        if values:
            if from_endpoints:
                result._endpoints = list(values)
                result._comps = [Component(inf, sup) for inf, sup in _group_by_len(values, 2)]
            else:
                result._comps = [Component.create(comp) for comp in values]
                result._endpoints = sum([[comp.inf, comp.sup] for comp in result._comps], [])
        return result

    @property
    def components(self) -> Sequence[Interval[_T]]:
        cls = type(self)
        return [cls(comp) for comp in self._comps]

    @property
    def extrema(self) -> Interval[_T]:
        endpoints = [k for k, _ in groupby(self._endpoints)]
        return type(self)._from_valid_values(endpoints, from_endpoints=False)

    @property
    def midpoint(self) -> Interval[_T]:
        midpoints = [(comp.inf + comp.sup) / 2 for comp in self._comps]
        return type(self)._from_valid_values(zip(midpoints, midpoints), from_endpoints=False)

    def __contains__(self, item: Union[_T, Component[_T], Interval[_T]]) -> bool:

        if isinstance(item, Interval):
            return all(comp in self for comp in item)

        elif isinstance(item, Component):
            inf, sup = item.inf, item.sup
            inf_idx, sup_idx = bisect_left(self._endpoints, inf), bisect_right(self._endpoints, sup)
            n = len(self._endpoints)
            if inf_idx >= n or sup_idx >= n or sup_idx - inf_idx > 1:
                return False

            comp = self._comps[inf_idx // 2]
            return inf in comp and sup in comp

        elif isinstance(item, numbers.Number):
            idx = bisect_left(self._endpoints, item)
            n = len(self._endpoints)
            if idx >= n:
                return False

            return item in self._comps[idx // 2]

        else:
            raise TypeError(f'{type(self).__name__} items must be numbers, components or intervals, '
                            f'got `{type(item).__name__}` with value: `{item}`')

    def __len__(self) -> int:
        return len(self._comps)

    def __getitem__(self, index: Union[int, slice, tuple]) -> Union[Component[_T], Interval[_T]]:
        if isinstance(index, int):
            return self._comps[index]
        elif isinstance(index, slice):
            return type(self)._from_valid_values(self._comps[index], from_endpoints=False)
        elif isinstance(index, tuple) and all(isinstance(i, (int, slice)) for i in index):
            comps = [self[i] for i in index]
            comps = sum([[comp] if isinstance(comp, Component) else list(comp) for comp in comps], [])
            comps = sorted(comps, key=operator.attrgetter('_compare_key'))
            return type(self)._from_valid_values(comps, from_endpoints=False)
        else:
            raise TypeError(f'{type(self).__name__} indices must be ints or slices, got {type(index).__name__}')

    def __invert__(self) -> Interval[_T]:
        cls = type(self)
        if not self._endpoints:
            return cls._from_valid_values([-math.inf, math.inf], from_endpoints=True)

        first, last = self._endpoints[0], self._endpoints[-1]
        types = sum([[not comp.is_left_closed, not comp.is_right_closed] for comp in self._comps], [])
        if -math.inf != first and math.inf != last:
            compl = [-math.inf, *self._endpoints, math.inf]
            types = [False, *types, False]
        elif -math.inf == first and math.inf == last:
            compl = self._endpoints[1:-1]
            types = types[1:-1]
        elif -math.inf == first and math.inf != last:
            compl = [*self._endpoints[1:], math.inf]
            types = [*types[1:], False]
        else:
            compl = [-math.inf, *self._endpoints[:-1]]
            types = [False, *types[:-1]]

        return cls._from_valid_values([Component(inf, sup, ComponentType.get(left, right))
                                       for (inf, sup), (left, right) in
                                       zip(_group_by_len(compl, 2), _group_by_len(types, 2))
                                       ],
                                      from_endpoints=False
                                      )

    def __or__(self, other: Union[Component[_T], Interval[_T]]) -> Interval[_T]:
        cls = type(self)
        if isinstance(other, Component):
            other = cls(other)

        assert isinstance(other, Interval)
        return cls(*self, *other)

    def __and__(self, other: Union[Component[_T], Interval[_T]]) -> Interval[_T]:
        if isinstance(other, Component):
            other = type(self)(other)
        return ~(~self | ~other)

    def __xor__(self, other: Union[Component[_T], Interval[_T]]) -> Interval[_T]:
        if isinstance(other, Component):
            other = type(self)(other)
        return (self & ~other) | (~self & other)

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Interval) and self._endpoints == other._endpoints

    def __repr__(self) -> str:
        # # for debugging purposes, uncommet the following:
        # return f'{type(self).__name__}({self._endpoints})'
        return str(self)

    def __str__(self) -> str:
        comps = ', '.join(str(comp) for comp in self._comps)
        return f'{type(self).__name__}({comps})'

    @classmethod
    def hull(cls, intervals: Iterable[Interval[_T]]) -> Interval[_T]:
        values = [(value._endpoints[0], value._endpoints[-1], value) for value in intervals]
        inf = min(values, key=operator.itemgetter(0))
        sup = max(values, key=operator.itemgetter(1))
        left = inf[2]._comps[0].is_left_closed
        right = sup[2]._comps[-1].is_right_closed
        return cls(Component(inf[0], sup[1], ComponentType.get(left, right)))

    @classmethod
    def union(cls, intervals: Iterable[Interval[_T]]) -> Interval[_T]:
        components = [value._comps for value in intervals]
        return cls(*chain(*components))

    @classmethod
    def cast(cls, scalar: _T) -> Interval[_T]:
        return cls([scalar])


interval = Interval
