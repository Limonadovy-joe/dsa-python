"""Three-way comparison of values, with a pluggable compare function."""

from __future__ import annotations

import math
from typing import TYPE_CHECKING, Protocol, cast

if TYPE_CHECKING:
    from collections.abc import Callable

type Primitive = int | float | bool | str | bytes | None
type ComparatorFunc[T] = Callable[[T, T], int]

# Module-level tuples: ``isinstance(v, int | float)`` would build a new
# ``types.UnionType`` on every call, and this runs once per node in every search.
_NUMBER = (int, float)
_PRIMITIVE = (int, float, str, bytes)


class _Ordered(Protocol):
    """Anything with ``<`` and ``>``; used only to type the ``==`` fallback."""

    def __lt__(self, other: object, /) -> bool: ...
    def __gt__(self, other: object, /) -> bool: ...


def _incomparable(x: object, y: object) -> TypeError:
    """Build the ``TypeError`` for two values that have no order between them."""
    return TypeError(f"cannot compare {type(x).__name__} with {type(y).__name__}")


def _is_primitive(value: object) -> bool:
    """Return whether ``value`` belongs to one of the ``Primitive`` families."""
    return value is None or isinstance(value, _PRIMITIVE)


def _compare_numbers(x: int | float, y: int | float) -> int:
    """Compare two numbers, ordering NaN equal to NaN and above everything else.

    NaN is only looked for once ``<``, ``>`` and ``==`` all failed, so the
    ordinary case costs no NaN test. ``isinstance`` guards ``math.isnan``,
    which raises ``OverflowError`` on an int too large for a float.
    """
    if x < y:
        return -1
    if x > y:
        return 1
    if x == y:
        return 0
    x_is_nan = isinstance(x, float) and math.isnan(x)
    y_is_nan = isinstance(y, float) and math.isnan(y)
    return x_is_nan - y_is_nan


def _compare_fallback(x: object, y: object) -> int:
    """Compare values outside the primitive families with ``==``, ``<`` and ``>``.

    Two values that are unequal yet neither ``<`` nor ``>`` (a partial order,
    e.g. two disjoint ``frozenset``, or lists holding distinct NaN objects) get
    a nonzero tie-break by ``id``. That order is arbitrary but antisymmetric and
    consistent for as long as both objects are alive in this process.

    Raises:
        TypeError: Python refuses to order ``x`` and ``y`` (e.g. two
            ``object()``, or a list and a tuple). The message names both types.
    """
    if x == y:
        return 0
    # The operand types are unknown here: the cast only lets the checker accept
    # ``<``/``>``; an unorderable pair raises TypeError, caught and re-raised.
    ordered = cast("_Ordered", x)
    try:
        if ordered < y:
            return -1
        if ordered > y:
            return 1
    except TypeError as exc:
        raise _incomparable(x, y) from exc
    x_id, y_id = id(x), id(y)
    return (x_id > y_id) - (x_id < y_id)


class Comparator[T]:
    """Three-way comparison of two values, ``-1`` / ``0`` / ``1``.

    Holds a compare function, the default being :meth:`default_compare`, and
    answers equality through it.

    Complexity:
        ``equal``: the cost of the compare function; O(1) extra space.
    """

    compare: ComparatorFunc[T]

    @staticmethod
    def default_compare(x: Primitive, y: Primitive) -> int:
        """Compare two values: ``-1`` if ``x < y``, ``0`` if equal, else ``1``.

        Numbers (``int``, ``float``, ``bool``) compare by value with each other,
        exactly even for huge ints against floats. NaN gets a total order: equal
        to NaN, greater than every other number (``inf`` included). ``str``,
        ``bytes`` and ``None`` each compare only within their own type; two
        primitives of different families raise.

        Values outside those families (lists, tuples, sets, custom objects) fall
        back to ``==`` for equality and ``<`` / ``>`` for the order. Unequal
        values that are neither ``<`` nor ``>`` (partial orders such as sets)
        get an arbitrary but antisymmetric nonzero order by ``id``, consistent
        for as long as both objects are alive.

        Complexity:
            Time O(1) for numbers and ``None``; O(min(len x, len y)) for ``str``
            and ``bytes``; for the fallback, the cost of the operands' own
            ``==``, ``<`` and ``>`` (O(n) for lists and tuples of n
            primitives). Space O(1).

        Raises:
            TypeError: two primitives of different families (e.g. ``"a"`` and
                ``1``, ``None`` and ``0``), or two unequal values that Python
                cannot order (e.g. two ``object()``). The message names both
                types.
        """
        # Fast path for the most common case: two exact ints (NaN impossible).
        if type(x) is int and type(y) is int:
            return (x > y) - (x < y)
        if isinstance(x, _NUMBER) and isinstance(y, _NUMBER):
            return _compare_numbers(x, y)
        if isinstance(x, str) and isinstance(y, str):
            return (x > y) - (x < y)
        if isinstance(x, bytes) and isinstance(y, bytes):
            return (x > y) - (x < y)
        if x is None and y is None:
            return 0
        if _is_primitive(x) and _is_primitive(y):
            raise _incomparable(x, y)
        return _compare_fallback(x, y)

    def __init__(self, compare_fun: ComparatorFunc[T] | None = None) -> None:
        if compare_fun is not None:
            self.compare = compare_fun
        else:
            # default_compare is typed for Primitive but accepts any value at
            # runtime: non-primitives take the ==/</> fallback, so it is a
            # valid compare function for every T.
            self.compare = cast("ComparatorFunc[T]", Comparator.default_compare)

    def equal(self, x: T, y: T) -> bool:
        """Return whether ``compare(x, y) == 0``.

        Complexity:
            Time: the cost of ``compare``. Space O(1).
        """
        return self.compare(x, y) == 0
