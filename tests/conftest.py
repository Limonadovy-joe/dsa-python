"""Suite-wide pytest hooks."""

from __future__ import annotations

import pytest


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--allow-no-tests",
        action="store_true",
        help="exit 0 instead of 5 when the -m/-k selection matches no tests",
    )


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    # A stage selected by marker (`-m integration`) has nothing to run until its
    # first test lands. That stage is empty, not broken, so it shouldn't block a push.
    if exitstatus == pytest.ExitCode.NO_TESTS_COLLECTED and session.config.getoption(
        "--allow-no-tests"
    ):
        session.exitstatus = pytest.ExitCode.OK
