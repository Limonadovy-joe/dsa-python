"""CircularArray.

Complexity:
    TODO: document time/space for the main operations.
      [Writing | Arrays | Core | agent-ready]
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional, TypeVar

if TYPE_CHECKING:
    pass  # noqa: TC005

T = TypeVar("T")


class CircularArray[T]:
    _capacity: int
    _read_index: int
    _write_index: int
    _current_size: int
    _slots: list[Optional[T]]  # noqa: UP045

    def __init__(self, capacity: int = 16) -> None:
        self._capacity = capacity
        self._read_index = 0
        self._write_index = 0
        self._current_size = 0
        self._slots = [None] * self._capacity

    def _write(self, item: T) -> None:

        if self._current_size < self._capacity:
            self._current_size = self._current_size + 1

        self._slots[self._write_index] = item
        self._write_index = (self._write_index + 1) % self._capacity
        return None  # noqa: PLR1711

    def _read(self) -> Optional[T]:  # noqa: UP045
        if self._current_size > 0:
            self._current_size = self._current_size - 1

        return_value = self._slots[self._read_index]
        self._slots[self._read_index] = None
        self._read_index = (self._read_index + 1) % self._capacity
        return return_value

    def peek(self) -> Optional[T]:  # noqa: UP045
        return self._slots[self._read_index]

    def enqueue(self, item: T) -> None:
        self._write(item)

    def deque(self) -> Optional[T]:  # noqa: UP045
        return self._read()

    def size(self) -> int:
        return self._current_size

    def is_full(self) -> bool:
        return self._current_size == self._capacity

    def is_empty(self) -> bool:
        return self._current_size == 0
