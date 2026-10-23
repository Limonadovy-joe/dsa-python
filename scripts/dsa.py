from __future__ import annotations

import argparse
import re
from pathlib import Path


def _snake_to_pascal(name: str) -> str:
    """linked_list -> LinkedList, deque -> Deque."""
    return "".join(part.capitalize() for part in name.split("_"))


def _write_if_missing(path: Path, content: str) -> None:
    if path.exists():
        print(f"  skip  {path}  (already exists)")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"  create  {path}")


# ---------------------------------------------------------------------------
# Templates
# ---------------------------------------------------------------------------


def _module_init(import_path: str, name: str, class_name: str) -> str:
    # import_path is the full dotted path to the package, e.g. "dsa.binary_tree"
    return (
        f'"""{class_name} data structure."""\n'
        "\n"
        f"from {import_path}.{name} import {class_name}\n"
        "\n"
        f'__all__ = ["{class_name}"]\n'
    )


def _module_file(class_name: str) -> str:
    return (
        f'"""{class_name}.\n'
        "\n"
        "Complexity:\n"
        "    TODO — document time/space for the main operations.\n"
        '"""\n'
        "\n"
        "from __future__ import annotations\n"
        "\n"
        "from typing import TYPE_CHECKING, Generic, Optional, Protocol, TypeVar\n"
        "\n"
        "if TYPE_CHECKING:\n"
        "    from collections.abc import Callable\n"
        "\n"
        'T = TypeVar("T")\n'
        "\n"
        "\n"
        f"class {class_name}Storage(Protocol[T]):\n"
        f'    """Storage backend contract for {class_name}."""\n'
        "\n"
        "    ...\n"
        "\n"
        "\n"
        f"class {class_name}[T]:\n"
        f'    """TODO: implement {class_name}."""\n'
        "\n"
        f"    _storage: {class_name}Storage[T]\n"
        "\n"
        f"    def __init__(self, storage: {class_name}Storage[T]) -> None:\n"
        "        self._storage = storage\n"
    )


def _backends(tests_dotted: str, import_path: str, name: str, class_name: str) -> str:
    return (
        f'"""{class_name} backends under test, shared by unit, integration and performance tests."""\n'
        "\n"
        "from __future__ import annotations\n"
        "\n"
        "from typing import TYPE_CHECKING, Protocol\n"
        "\n"
        f"from {import_path} import {class_name}\n"
        "\n"
        "if TYPE_CHECKING:\n"
        "    from collections.abc import Iterable\n"
        "\n"
        "\n"
        f"class Make{class_name}(Protocol):\n"
        f'    """Build a fresh {name}, optionally pre-filled with ``values``."""\n'
        "\n"
        f"    def __call__[T](self, values: Iterable[T] = ()) -> {class_name}[T]: ...\n"
        "\n"
        "\n"
        f"# def _fill[T]({name}: {class_name}[T], values: Iterable[T]) -> {class_name}[T]:\n"
        f"#     for value in values:\n"
        f"#         {name}.<method>(value)\n"
        f"#     return {name}\n"
        "\n"
        "\n"
        f"# Adding a backend here runs every {name} test against it.\n"
        f"BACKENDS: dict[str, Make{class_name}] = {{\n"
        "}\n"
    )


def _conftest(tests_dotted: str, name: str, class_name: str) -> str:
    return (
        "from __future__ import annotations\n"
        "\n"
        "import pytest\n"
        "\n"
        f"from {tests_dotted}.{name}_backends import BACKENDS, Make{class_name}\n"
        "\n"
        "\n"
        "@pytest.fixture(params=list(BACKENDS))\n"
        f"def {name}_backend(request: pytest.FixtureRequest) -> str:\n"
        "    return request.param  # type: ignore[no-any-return]\n"
        "\n"
        "\n"
        "@pytest.fixture\n"
        f"def make_{name}({name}_backend: str) -> Make{class_name}:\n"
        f"    return BACKENDS[{name}_backend]\n"
    )


def _test_file(import_path: str, name: str, class_name: str) -> str:
    return (
        "from __future__ import annotations\n"
        "\n"
        "from typing import TYPE_CHECKING\n"
        "\n"
        "if TYPE_CHECKING:\n"
        f"    from {import_path} import {class_name}\n"
        "\n"
        "\n"
        f"def test_{name}_placeholder() -> None:\n"
        f'    """Remove once real tests are added."""\n'
    )


# ---------------------------------------------------------------------------
# Scaffold actions
# ---------------------------------------------------------------------------


def _import_path(src: str, name: str) -> str:
    """Build the dotted import path for the package, e.g. 'dsa.binary_tree'."""
    if src == ".":
        return name
    return f"{Path(src).as_posix().replace('/', '.')}.{name}"


def create_module(root: Path, src: str, name: str) -> None:
    class_name = _snake_to_pascal(name)
    src_dir = root / src / name
    pkg_path = _import_path(src, name)

    _write_if_missing(src_dir / "__init__.py", _module_init(pkg_path, name, class_name))
    _write_if_missing(src_dir / f"{name}.py", _module_file(class_name))


def create_tests(
    root: Path,
    src: str,
    name: str,
    *,
    unit: bool = True,
    integration: bool = True,
    perf: bool = True,
) -> None:
    class_name = _snake_to_pascal(name)
    pkg_path = _import_path(src, name)
    test_dir = root / "tests" / name
    tests_dotted = f"tests.{name}"

    _write_if_missing(root / "tests" / "__init__.py", "")
    _write_if_missing(test_dir / "__init__.py", "")
    _write_if_missing(
        test_dir / f"{name}_backends.py",
        _backends(tests_dotted, pkg_path, name, class_name),
    )
    _write_if_missing(
        test_dir / "conftest.py",
        _conftest(tests_dotted, name, class_name),
    )
    if unit:
        _write_if_missing(test_dir / "unit" / "__init__.py", "")
        _write_if_missing(
            test_dir / "unit" / f"test_{name}.py",
            _test_file(pkg_path, name, class_name),
        )
    if integration:
        _write_if_missing(test_dir / "integration" / "__init__.py", "")
    if perf:
        _write_if_missing(test_dir / "perf" / "__init__.py", "")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

_COMMAND_RE = re.compile(r"^create-([a-z][a-z0-9_]*)(?:-(module|tests))?$")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Scaffold a new DSA module and/or its tests.",
    )
    parser.add_argument("command", help="create-<type>[-(module|tests)]")
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parent.parent,
        help="Project root (default: two levels up from this script)",
    )
    parser.add_argument(
        "--src",
        default="dsa",
        help='Source package folder relative to root (default: "dsa")',
    )
    parser.add_argument(
        "-u",
        action="store_true",
        help="Create unit test folder with test file",
    )
    parser.add_argument(
        "-i",
        action="store_true",
        help="Create integration test folder",
    )
    parser.add_argument(
        "-p",
        action="store_true",
        help="Create performance test folder",
    )
    args = parser.parse_args(argv)

    m = _COMMAND_RE.match(args.command)
    if not m:
        parser.error(
            f"Unknown command {args.command!r}. "
            "Expected create-<type>, create-<type>-module, or create-<type>-tests."
        )

    name: str = m.group(1)
    scope: str | None = m.group(2)  # None | "module" | "tests"

    # If none of -u/-i/-p given, default to all three.
    any_flag = args.u or args.i or args.p
    unit = args.u or not any_flag
    integration = args.i or not any_flag
    perf = args.p or not any_flag

    if scope is None or scope == "module":
        print(f"[module] {name}")
        create_module(args.root, args.src, name)
    if scope is None or scope == "tests":
        print(f"[tests]  {name}")
        create_tests(
            args.root, args.src, name, unit=unit, integration=integration, perf=perf
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
