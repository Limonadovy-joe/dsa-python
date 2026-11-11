"""CircularArray backends, shared by unit, integration and performance tests."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

from dsa.arrays.circular_array import CircularArray

if TYPE_CHECKING:
    from collections.abc import Iterable


class MakeCircularArray(Protocol):
    """Build a fresh circular_array, optionally pre-filled with ``values``."""

    def __call__[T](
        self, values: Iterable[T] = (), capacity: int = 16
    ) -> CircularArray[T]: ...


def _make_circular_array[T](
    values: Iterable[T] = (), capacity: int = 16
) -> CircularArray[T]:
    ca: CircularArray[T] = CircularArray(capacity)
    for value in values:
        ca.enqueue(value)
    return ca


# Adding a backend here runs every circular_array test against it.
BACKENDS: dict[str, MakeCircularArray] = {
    "circular_array": _make_circular_array,
}
