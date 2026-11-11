from __future__ import annotations

import time
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from tests.queues.queue.queue_backends import MakeQueue

pytestmark = pytest.mark.performance

# Wall-clock limits are machine-dependent, so compare growth instead: draining 4x
# the items costs ~4x for O(1) dequeue and ~16x for O(n) dequeue.
_SIZE = 5_000
_GROWTH = 4
_LINEAR_BOUND = 8


def _drain_seconds(make_queue: MakeQueue, size: int) -> float:
    best = float("inf")
    for _ in range(3):  # best of 3 filters out scheduler noise
        queue = make_queue(range(size))
        start = time.perf_counter()
        for _ in range(size):
            queue.dequeue()
        best = min(best, time.perf_counter() - start)
    return best


@pytest.mark.known_bug("list", reason="QueueList dequeues with list.pop(0), O(n)")
def test_draining_queue_scales_linearly(make_queue: MakeQueue) -> None:
    small = _drain_seconds(make_queue, _SIZE)
    large = _drain_seconds(make_queue, _SIZE * _GROWTH)
    assert large / small < _LINEAR_BOUND
