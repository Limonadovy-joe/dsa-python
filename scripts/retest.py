"""Run the whole suite, with the tests worth seeing first at the front.

Order: tests that failed on the last run, then tests pytest has not seen before
(added since the last run), then everything else. Nothing is skipped or
rewritten, only reordered, so a fix or a new test gives its answer early.

pytest's own `--failed-first --new-first` does not give this order:
`--new-first` re-sorts last, putting new tests ahead of failed ones and sorting
the rest by file modification time. This plugin reads the same `.pytest_cache`
and does the ordering explicitly. Delete `.pytest_cache` and every test is new.

Run it from the repo root; extra arguments go straight to pytest:

    uv run python scripts/retest.py
    uv run python scripts/retest.py tests/linked_lists -x
"""

from __future__ import annotations

import sys

import pytest


class _FailedThenNewThenRest:
    """pytest plugin: order collected tests as failed, new, then the rest."""

    def __init__(self) -> None:
        self._summary = ""

    # trylast: run after pytest's own deselection (-m, -k) so only selected tests
    # are ordered. Each group keeps collection order, so the run is deterministic.
    @pytest.hookimpl(trylast=True)
    def pytest_collection_modifyitems(
        self, config: pytest.Config, items: list[pytest.Item]
    ) -> None:
        cache = config.cache
        if cache is None:
            return

        failed_ids = set(cache.get("cache/lastfailed", {}))
        known_ids = set(cache.get("cache/nodeids", []))

        failed: list[pytest.Item] = []
        new: list[pytest.Item] = []
        rest: list[pytest.Item] = []
        for item in items:
            if item.nodeid in failed_ids:
                failed.append(item)
            elif item.nodeid not in known_ids:
                new.append(item)
            else:
                rest.append(item)

        items[:] = failed + new + rest
        self._summary = (
            f"retest order: {len(failed)} failed last time, "
            f"{len(new)} new, {len(rest)} other"
        )

    def pytest_report_collectionfinish(self) -> str:
        return self._summary


def main(argv: list[str]) -> int:
    """Run pytest with the ordering plugin and return pytest's exit code."""
    return int(pytest.main(argv, plugins=[_FailedThenNewThenRest()]))


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
