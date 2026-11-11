"""A growable array built on a fixed-capacity buffer.

This is the classic "how does ``list`` work" exercise: a fixed-size block of
slots plus a doubling policy, which makes ``append`` O(1) amortised.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from collections.abc import Iterable, Iterator

_INITIAL_CAPACITY = 4


class DynamicArray[T]:  # noqa: PLW1641 - mutable container, intentionally unhashable
    """A list-like sequence with amortised O(1) ``append``.

    Complexity: index/append amortised O(1), insert/pop-at-index O(n),
    space O(n).

    Slots at indices ``>= len(self)`` hold ``None`` as filler and are never
    read, which is why the reads below can cast the buffer element to ``T``.
    """

    def __init__(self, items: Iterable[T] = ()) -> None:
        self._capacity = _INITIAL_CAPACITY
        self._size = 0
        self._slots: list[T | None] = [None] * self._capacity
        for item in items:
            self.append(item)

    def __len__(self) -> int:
        """Return the number of items stored."""
        return self._size

    def __iter__(self) -> Iterator[T]:
        """Iterate over the stored items in order."""
        for i in range(self._size):
            yield cast("T", self._slots[i])

    def __getitem__(self, index: int) -> T:
        """Return the item at ``index``, which may be negative."""
        return cast("T", self._slots[self._normalize(index)])

    def __setitem__(self, index: int, value: T) -> None:
        """Replace the item at ``index``."""
        self._slots[self._normalize(index)] = value

    def __eq__(self, other: object) -> bool:
        """Return whether ``other`` is a ``DynamicArray`` with equal items."""
        if not isinstance(other, DynamicArray):
            return NotImplemented
        return len(self) == len(other) and all(
            a == b for a, b in zip(self, other, strict=True)
        )

    def __repr__(self) -> str:
        """Return a reconstructible representation."""
        return f"DynamicArray({list(self)!r})"

    @property
    def capacity(self) -> int:
        """Number of slots currently allocated (>= ``len(self)``)."""
        return self._capacity

    def append(self, value: T) -> None:
        """Add ``value`` to the end, doubling the buffer when it is full."""
        if self._size == self._capacity:
            self._resize(self._capacity * 2)
        self._slots[self._size] = value
        self._size += 1

    def insert(self, index: int, value: T) -> None:
        """Insert before ``index``; ``index == len(self)`` appends."""
        if index == self._size:
            self.append(value)
            return
        index = self._normalize(index)
        if self._size == self._capacity:
            self._resize(self._capacity * 2)
        for i in range(self._size, index, -1):
            self._slots[i] = self._slots[i - 1]
        self._slots[index] = value
        self._size += 1

    def pop(self, index: int = -1) -> T:
        """Remove and return the item at ``index`` (last by default)."""
        index = self._normalize(index)
        value = cast("T", self._slots[index])
        for i in range(index, self._size - 1):
            self._slots[i] = self._slots[i + 1]
        self._size -= 1
        self._slots[self._size] = None  # drop the reference so it can be GC'd
        return value

    def _normalize(self, index: int) -> int:
        if index < 0:
            index += self._size
        if not 0 <= index < self._size:
            msg = "DynamicArray index out of range"
            raise IndexError(msg)
        return index

    def _resize(self, capacity: int) -> None:
        slots: list[T | None] = [None] * capacity
        for i in range(self._size):
            slots[i] = self._slots[i]
        self._slots = slots
        self._capacity = capacity
