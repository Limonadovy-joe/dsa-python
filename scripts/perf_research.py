"""Scaffold and refresh the performance research doc of one data structure.

Usage (from the repo root)::

    uv run python scripts/perf_research.py list
    uv run python scripts/perf_research.py init queue
    uv run python scripts/perf_research.py tables queue [--run-id ID]

Layout and contracts: ``docs/performance-research.md``::

    results/<structure>/data/     raw measurements (tidy CSV)
    results/<structure>/report/   <structure>.md (this doc) + figures

``init`` writes the doc once. ``tables`` is safe to re-run: it adds rows for new
backends/operations, copies the expected columns from table 1 into the measured
tables, refreshes the measured columns from ``data/`` and keeps every cell the
script does not own.
"""

from __future__ import annotations

import argparse
import csv
import importlib
import inspect
import math
import re
import statistics
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable

ROOT = Path(__file__).resolve().parent.parent
# `tests` is not installed like `dsa`; the root on sys.path makes the backend
# modules (tests/<topic>/<name>_backends.py) importable.
sys.path.insert(0, str(ROOT))

NO_BACKEND = "—"
# Dunders that are operations a user calls (len(x), x[i], `in`, for-loops), as
# opposed to plumbing (__init__, __repr__, __eq__).
OPERATION_DUNDERS = frozenset(
    {
        "__len__",
        "__getitem__",
        "__setitem__",
        "__delitem__",
        "__contains__",
        "__iter__",
    }
)
SECONDS = "seconds"
PEAK_BYTES = "peak_bytes"
REQUIRED_DATA_COLUMNS = frozenset({"backend", "operation", "n", "metric", "value"})
DEFAULT_GROWTH = "4"

_BLOCK = re.compile(
    r"<!-- perf:(?P<kind>table|exercises)(?::(?P<key>[a-z]+))? -->\n"
    r"(?P<body>.*?)"
    r"<!-- perf:end -->",
    re.DOTALL,
)
_CELL_SPLIT = re.compile(r"(?<!\\)\|")
_NUMBER = re.compile(r"\d+(?:\.\d+)?")

type Key = tuple[str, str]  # (backend, operation), normalised


# ---------------------------------------------------------------------------
# Discovery
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Structure:
    """What the doc is generated from: the class, its backends, its operations."""

    name: str
    class_name: str
    module: str
    backends: tuple[str, ...]
    backends_file: Path | None
    operations: tuple[str, ...]

    @property
    def results_dir(self) -> Path:
        return ROOT / "results" / self.name

    @property
    def doc_path(self) -> Path:
        return self.results_dir / "report" / f"{self.name}.md"


def _pascal(name: str) -> str:
    return "".join(part.capitalize() for part in name.split("_"))


def _dotted(path: Path) -> str:
    return ".".join(path.relative_to(ROOT).with_suffix("").parts)


def _rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def _python_files(top: str, pattern: str) -> list[Path]:
    return sorted(
        path
        for path in (ROOT / top).rglob(pattern)
        if "__pycache__" not in path.parts and path.name != "__init__.py"
    )


def _operations(cls: type) -> tuple[str, ...]:
    """Public methods and properties the class itself defines, in source order."""
    operations: list[str] = []
    for attr, value in vars(cls).items():
        if attr.startswith("_") and attr not in OPERATION_DUNDERS:
            continue
        if inspect.isfunction(value) or isinstance(
            value, property | staticmethod | classmethod
        ):
            operations.append(attr)
    return tuple(operations)


def _backends(name: str) -> tuple[tuple[str, ...], Path | None]:
    files = _python_files("tests", f"{name}_backends.py")
    if not files:
        return (NO_BACKEND,), None
    if len(files) > 1:
        sys.exit(f"ambiguous backends for {name!r}: {[_rel(f) for f in files]}")
    module = importlib.import_module(_dotted(files[0]))
    backends = getattr(module, "BACKENDS", None)
    if not isinstance(backends, dict) or not backends:
        sys.exit(f"{_rel(files[0])} has no non-empty BACKENDS dict")
    return tuple(str(key) for key in backends), files[0]


def discover(name: str) -> Structure:
    """Find ``dsa/**/<name>.py``, its ``<Name>`` class and its BACKENDS."""
    modules = _python_files("dsa", f"{name}.py")
    if not modules:
        sys.exit(f"no module dsa/**/{name}.py — run `list` for the known structures")
    if len(modules) > 1:
        sys.exit(f"ambiguous structure {name!r}: {[_rel(m) for m in modules]}")
    dotted = _dotted(modules[0])
    class_name = _pascal(name)
    cls = getattr(importlib.import_module(dotted), class_name, None)
    if not isinstance(cls, type):
        sys.exit(f"{dotted} defines no class {class_name}")
    backends, backends_file = _backends(name)
    return Structure(
        name=name,
        class_name=class_name,
        module=dotted,
        backends=backends,
        backends_file=backends_file,
        operations=_operations(cls),
    )


# ---------------------------------------------------------------------------
# Markdown tables between <!-- perf:table:<key> --> and <!-- perf:end -->
# ---------------------------------------------------------------------------


@dataclass
class Table:
    """A markdown table as header names plus one dict per row."""

    columns: list[str]
    rows: list[dict[str, str]] = field(default_factory=list)


def _norm(cell: str) -> str:
    text = cell.replace("`", "").strip()
    return NO_BACKEND if text in {"", "-", NO_BACKEND} else text


def _key(row: dict[str, str]) -> Key:
    return _norm(row.get("Backend", "")), _norm(row.get("Operation", ""))


def _cells(line: str) -> list[str]:
    inner = line.strip().removeprefix("|").removesuffix("|")
    return [cell.strip() for cell in _CELL_SPLIT.split(inner)]


def parse_table(body: str) -> Table | None:
    """Parse the first markdown table in ``body``; ``None`` if there is none."""
    lines = [line for line in body.splitlines() if line.lstrip().startswith("|")]
    if len(lines) < 2:  # noqa: PLR2004 - header + separator
        return None
    columns = _cells(lines[0])
    rows = []
    for line in lines[2:]:
        cells = _cells(line)
        cells += [""] * (len(columns) - len(cells))
        rows.append(dict(zip(columns, cells, strict=False)))
    return Table(columns, rows)


def render_table(table: Table) -> str:
    """Render ``table`` as GitHub markdown."""
    out = [
        "| " + " | ".join(table.columns) + " |",
        "|" + "---|" * len(table.columns),
    ]
    out += [
        "| " + " | ".join(row.get(col, "") for col in table.columns) + " |"
        for row in table.rows
    ]
    return "\n".join(out) + "\n"


def _blocks(text: str) -> dict[str, re.Match[str]]:
    return {match["key"] or match["kind"]: match for match in _BLOCK.finditer(text)}


# ---------------------------------------------------------------------------
# Table specs: which columns the script owns, which are the human's
# ---------------------------------------------------------------------------

IDENTITY = ("Structure", "Backend", "Operation")


@dataclass(frozen=True)
class TableSpec:
    """Columns of one table. ``generated`` columns are rewritten on every run."""

    key: str
    columns: tuple[str, ...]
    generated: frozenset[str]
    defaults: dict[str, str] = field(default_factory=dict)


OPERATIONS = TableSpec(
    "operations",
    (*IDENTITY, "Expected time", "Expected space", "Notes"),
    generated=frozenset(),  # identity is written once, for new rows only
)
TIME = TableSpec(
    "time",
    (
        *IDENTITY,
        "Expected time",
        "n",
        "Median time / call",
        "Log-log slope",
        "Measured class",
        "Verdict",
        "Notes",
    ),
    generated=frozenset(
        {*IDENTITY, "Expected time", "n", "Median time / call", "Log-log slope"}
    ),
)
SPACE = TableSpec(
    "space",
    (
        *IDENTITY,
        "Expected space",
        "n",
        "Peak memory",
        "Bytes / element",
        "Log-log slope",
        "Measured class",
        "Verdict",
        "Notes",
    ),
    generated=frozenset(
        {
            *IDENTITY,
            "Expected space",
            "n",
            "Peak memory",
            "Bytes / element",
            "Log-log slope",
        }
    ),
)
GROWTH = TableSpec(
    "growth",
    (
        *IDENTITY,
        "Expected time",
        "Growth factor",
        "Bound",
        "Measured ratio",
        "Status",
        "Test",
        "Notes",
    ),
    generated=frozenset({*IDENTITY, "Expected time", "Measured ratio", "Status"}),
    defaults={"Growth factor": DEFAULT_GROWTH},
)
MEASURED = (TIME, SPACE, GROWTH)


def _with_spec_columns(spec: TableSpec, existing: Table | None) -> list[str]:
    """Keep the human's column order and extra columns; add any missing ones."""
    columns = list(existing.columns) if existing else list(spec.columns)
    columns += [col for col in spec.columns if col not in columns]
    return columns


def sync_operations(structure: Structure, existing: Table | None) -> Table:
    """Keep every existing row as written; append rows for new (backend, op)."""
    table = Table(_with_spec_columns(OPERATIONS, existing))
    table.rows = [dict(row) for row in existing.rows] if existing else []
    known = {_key(row) for row in table.rows}
    for backend in structure.backends:
        for operation in structure.operations:
            if (backend, operation) in known:
                continue
            table.rows.append(
                {
                    "Structure": structure.class_name,
                    "Backend": backend,
                    "Operation": f"`{operation}`",
                }
            )
    return table


def sync_measured(
    spec: TableSpec,
    operations: Table,
    existing: Table | None,
    fill: Callable[[dict[str, str], dict[str, str]], dict[str, str]],
) -> Table:
    """One row per row of table 1, in its order; human cells carried by key."""
    table = Table(_with_spec_columns(spec, existing))
    previous = {_key(row): row for row in existing.rows} if existing else {}
    for op_row in operations.rows:
        row = dict(spec.defaults) | previous.get(_key(op_row), {})
        row |= {col: op_row.get(col, "") for col in IDENTITY}
        row |= {k: v for k, v in fill(op_row, row).items() if k in spec.generated}
        table.rows.append(row)
    return table


# ---------------------------------------------------------------------------
# Measured data: results/<structure>/data/**/*.csv (contract in the docs)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Sample:
    """One measurement, normalised to a single call for ``seconds``."""

    backend: str
    operation: str
    metric: str
    n: int
    value: float
    run_id: str


def load_samples(data_dir: Path) -> tuple[list[Sample], list[Path]]:
    """Read every CSV under ``data_dir`` that has the required columns."""
    samples: list[Sample] = []
    used: list[Path] = []
    for path in sorted(data_dir.rglob("*.csv")):
        with path.open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            missing = REQUIRED_DATA_COLUMNS - set(reader.fieldnames or ())
            if missing:
                print(f"  skip  {_rel(path)}  (missing columns {sorted(missing)})")
                continue
            used.append(path)
            for line_no, row in enumerate(reader, start=2):
                try:
                    value = float(row["value"])
                    ops = float(row.get("ops") or 1)
                    if row["metric"] == SECONDS:
                        value /= ops
                    samples.append(
                        Sample(
                            backend=_norm(row["backend"]),
                            operation=_norm(row["operation"]),
                            metric=row["metric"].strip(),
                            n=int(row["n"]),
                            value=value,
                            run_id=(row.get("run_id") or "").strip(),
                        )
                    )
                except (ValueError, ZeroDivisionError) as error:
                    print(f"  skip  {_rel(path)}:{line_no}  ({error})")
    return samples, used


def select_run(samples: list[Sample], run_id: str | None) -> tuple[list[Sample], str]:
    """Never pool runs: keep ``run_id``, or the newest one if not given."""
    run_ids = {sample.run_id for sample in samples if sample.run_id}
    if not run_ids:
        return samples, ""
    chosen = run_id or max(run_ids)
    if chosen not in run_ids:
        sys.exit(f"run_id {chosen!r} not in data; known: {sorted(run_ids)}")
    return [sample for sample in samples if sample.run_id == chosen], chosen


@dataclass
class Measurements:
    """Median value per n, per (backend, operation, metric)."""

    medians: dict[tuple[str, str, str], dict[int, float]]

    @classmethod
    def from_samples(cls, samples: Iterable[Sample]) -> Measurements:
        grouped: dict[tuple[str, str, str], dict[int, list[float]]] = {}
        for sample in samples:
            key = (sample.backend, sample.operation, sample.metric)
            grouped.setdefault(key, {}).setdefault(sample.n, []).append(sample.value)
        return cls(
            {
                key: {n: statistics.median(vals) for n, vals in sorted(by_n.items())}
                for key, by_n in grouped.items()
            }
        )

    def get(self, key: Key, metric: str) -> dict[int, float]:
        return self.medians.get((*key, metric), {})


def _loglog_slope(medians: dict[int, float]) -> float | None:
    points = [(n, v) for n, v in medians.items() if n > 0 and v > 0]
    if len(points) < 2:  # noqa: PLR2004 - a slope needs two points
        return None
    xs = [math.log(n) for n, _ in points]
    ys = [math.log(v) for _, v in points]
    return statistics.linear_regression(xs, ys).slope


def _linear_slope(medians: dict[int, float]) -> float | None:
    if len(medians) < 2:  # noqa: PLR2004 - a slope needs two points
        return None
    return statistics.linear_regression(list(medians), list(medians.values())).slope


def _growth_ratio(medians: dict[int, float], growth: float) -> float | None:
    """Median at the largest n over the median at n / growth."""
    pairs = [
        (big, small)
        for small in medians
        for big in medians
        if small > 0 and math.isclose(big / small, growth, rel_tol=0.01)
    ]
    if not pairs:
        return None
    big, small = max(pairs)
    return medians[big] / medians[small] if medians[small] > 0 else None


def _fmt_seconds(seconds: float) -> str:
    for unit, scale in (("s", 1.0), ("ms", 1e-3), ("µs", 1e-6)):
        if seconds >= scale:
            return f"{seconds / scale:.3g} {unit}"
    return f"{seconds / 1e-9:.3g} ns"


def _fmt_bytes(size: float) -> str:
    for unit, scale in (("GiB", 2**30), ("MiB", 2**20), ("KiB", 2**10)):
        if abs(size) >= scale:
            return f"{size / scale:.3g} {unit}"
    return f"{size:.3g} B"


def _fmt_sizes(medians: dict[int, float]) -> str:
    sizes = sorted(medians)
    if len(sizes) == 1:
        return f"{sizes[0]:,}"
    return f"{sizes[0]:,} → {sizes[-1]:,} ({len(sizes)} sizes)"


def _fmt_span(medians: dict[int, float], fmt: Callable[[float], str]) -> str:
    sizes = sorted(medians)
    if len(sizes) == 1:
        return fmt(medians[sizes[0]])
    return f"{fmt(medians[sizes[0]])} → {fmt(medians[sizes[-1]])}"


def _fmt_optional(value: float | None, fmt: str) -> str:
    # round(...) + 0.0 turns -0.0 into 0.0, so a flat O(1) slope never shows "-0.00"
    return "" if value is None else format(round(value, 2) + 0.0, fmt)


def _first_number(cell: str) -> float | None:
    match = _NUMBER.search(cell.replace(",", ""))
    return float(match[0]) if match else None


def time_fill(data: Measurements) -> Callable[..., dict[str, str]]:
    """Generated cells of the time table for one row."""

    def fill(op_row: dict[str, str], _row: dict[str, str]) -> dict[str, str]:
        medians = data.get(_key(op_row), SECONDS)
        return {
            "Expected time": op_row.get("Expected time", ""),
            "n": _fmt_sizes(medians) if medians else "",
            "Median time / call": _fmt_span(medians, _fmt_seconds) if medians else "",
            "Log-log slope": _fmt_optional(_loglog_slope(medians), ".2f"),
        }

    return fill


def space_fill(data: Measurements) -> Callable[..., dict[str, str]]:
    """Generated cells of the space table for one row."""

    def fill(op_row: dict[str, str], _row: dict[str, str]) -> dict[str, str]:
        medians = data.get(_key(op_row), PEAK_BYTES)
        per_element = _linear_slope(medians)
        return {
            "Expected space": op_row.get("Expected space", ""),
            "n": _fmt_sizes(medians) if medians else "",
            "Peak memory": _fmt_span(medians, _fmt_bytes) if medians else "",
            "Bytes / element": "" if per_element is None else _fmt_bytes(per_element),
            "Log-log slope": _fmt_optional(_loglog_slope(medians), ".2f"),
        }

    return fill


def growth_fill(data: Measurements) -> Callable[..., dict[str, str]]:
    """Generated cells of the growth-ratio table for one row."""

    def fill(op_row: dict[str, str], row: dict[str, str]) -> dict[str, str]:
        growth = _first_number(row.get("Growth factor", ""))
        medians = data.get(_key(op_row), SECONDS)
        ratio = _growth_ratio(medians, growth) if growth and growth > 1 else None
        bound = _first_number(row.get("Bound", ""))
        status = ""
        if ratio is not None and bound is not None:
            status = "pass" if ratio < bound else "fail"
        return {
            "Expected time": op_row.get("Expected time", ""),
            "Measured ratio": _fmt_optional(ratio, ".2f"),
            "Status": status,
        }

    return fill


# ---------------------------------------------------------------------------
# The document
# ---------------------------------------------------------------------------


def _block(kind: str, body: str) -> str:
    return f"<!-- perf:{kind} -->\n{body}<!-- perf:end -->"


def render_doc(structure: Structure) -> str:
    """The research doc for a structure that has none yet."""
    name, cls = structure.name, structure.class_name
    if structure.backends_file is None:
        backends = (
            f"{NO_BACKEND} (no `tests/**/{name}_backends.py` yet; one "
            "single-entry `BACKENDS` dict keeps the benchmarks uniform)"
        )
    else:
        listed = ", ".join(f"`{b}`" for b in structure.backends)
        backends = f"{listed} from `{_rel(structure.backends_file)}`"
    operations = sync_operations(structure, None)
    empty = Measurements({})
    tables = {
        spec.key: render_table(sync_measured(spec, operations, None, fill(empty)))
        for spec, fill in (
            (TIME, time_fill),
            (SPACE, space_fill),
            (GROWTH, growth_fill),
        )
    }
    return f"""\
# {cls}: performance research

| | |
|---|---|
| Class | `{structure.module}.{cls}` |
| Backends | {backends} |
| Data | `results/{name}/data/`: tidy CSV, contract in `docs/performance-research.md` |
| Report | this file; save figures next to it in `results/{name}/report/` |

Generated by `scripts/perf_research.py`. After adding a backend or collecting
data, run `uv run python scripts/perf_research.py tables {name}`: it adds the
missing rows and refreshes the measured columns. It never touches a cell you
own.

## 1. Operations

Your prediction, made **before** measuring. You fill **Expected time**,
**Expected space** and **Notes**. The script fills only Structure, Backend and
Operation. Add a row for any workload the method names don't show (for example
`insert(0, x)` next to `insert(n, x)`, or `build` for the structure's own
footprint). Its Operation cell is the name your data uses.

{_block("table:operations", render_table(operations))}

## 2. Exercises

{_block("exercises", f"_Not written yet. Run `/perf-research exercises {name}`._\n")}

## 3. Time complexity: measured

**Expected time** is copied from table 1. **n**, **Median time / call** (at the
smallest → largest n) and **Log-log slope** come from `data/`. A slope near 0
means O(1), near 1 means O(n), near 2 means O(n²). O(log n) shows up as a small
positive slope. **Measured class**, **Verdict** ("matches expected" or "does not
match, because …") and **Notes** are yours.

{_block("table:time", tables["time"])}

## 4. Space complexity: measured

**Expected space** is copied from table 1. **Peak memory** is the `tracemalloc`
peak at the smallest → largest n. **Bytes / element** is the slope of peak bytes
against n. **Log-log slope** reads like the one in table 3. **Measured class**,
**Verdict** and **Notes** are yours.

{_block("table:space", tables["space"])}

## 5. Growth-ratio assertions

One row per ratio check. **Growth factor** is the factor between the two sizes
you compare (default {DEFAULT_GROWTH}). **Measured ratio** is the median time
per call at the largest n divided by the median at n / growth: about 1 for O(1),
about growth for O(n), about growth² for O(n²). A pytest ratio test that times
*all n calls* sees one more factor of growth. **Bound** (put its derivation in
Notes) and **Test** (the pytest node id) are yours. **Status** compares the
measured ratio with your bound.

{_block("table:growth", tables["growth"])}
"""


def refresh_doc(
    structure: Structure, text: str, data: Measurements, source: str
) -> str:
    """Sync every table block in ``text``; leave everything else as written."""
    blocks = _blocks(text)
    if "operations" not in blocks:
        sys.exit(f"{_rel(structure.doc_path)}: no <!-- perf:table:operations --> block")
    operations = sync_operations(structure, parse_table(blocks["operations"]["body"]))
    bodies = {"operations": render_table(operations)}
    fills = {"time": time_fill, "space": space_fill, "growth": growth_fill}
    for spec in MEASURED:
        if spec.key not in blocks:
            print(f"  warn  no <!-- perf:table:{spec.key} --> block; skipped")
            continue
        existing = parse_table(blocks[spec.key]["body"])
        table = sync_measured(spec, operations, existing, fills[spec.key](data))
        bodies[spec.key] = (source + "\n\n" if source else "") + render_table(table)

    # Replace from the end so earlier offsets stay valid.
    for key in sorted(bodies, key=lambda k: blocks[k].start(), reverse=True):
        match = blocks[key]
        text = text[: match.start("body")] + bodies[key] + text[match.end("body") :]
    return text


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def cmd_list(_args: argparse.Namespace) -> int:
    """Print every structure the script can scaffold."""
    for path in _python_files("dsa", "*.py"):
        name = path.stem
        module = importlib.import_module(_dotted(path))
        if not isinstance(getattr(module, _pascal(name), None), type):
            continue
        backends, _ = _backends(name)
        doc = ROOT / "results" / name / "report" / f"{name}.md"
        state = "doc" if doc.exists() else "-"
        print(f"{name:<22} {_pascal(name):<22} {state:<4} {', '.join(backends)}")
    return 0


def cmd_init(args: argparse.Namespace) -> int:
    """Create results/<name>/{data,report}/ and the research doc."""
    structure = discover(args.structure)
    data_dir = structure.results_dir / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    (data_dir / ".gitkeep").touch(exist_ok=True)
    structure.doc_path.parent.mkdir(parents=True, exist_ok=True)
    if structure.doc_path.exists():
        print(f"  skip  {_rel(structure.doc_path)}  (exists; use `tables`)")
        return 0
    structure.doc_path.write_text(render_doc(structure), encoding="utf-8")
    print(f"  create  {_rel(structure.doc_path)}")
    print(
        f"  rows    {len(structure.backends)} backend(s) x "
        f"{len(structure.operations)} operation(s): {', '.join(structure.operations)}"
    )
    return 0


def cmd_tables(args: argparse.Namespace) -> int:
    """Sync rows and refresh the measured columns from data/."""
    structure = discover(args.structure)
    if not structure.doc_path.exists():
        sys.exit(f"{_rel(structure.doc_path)} missing; run `init {structure.name}`")
    samples, used = load_samples(structure.results_dir / "data")
    samples, run_id = select_run(samples, args.run_id)
    source = ""
    if used:
        files = ", ".join(f"`{_rel(p)}`" for p in used)
        run = f", run `{run_id}`" if run_id else ""
        source = f"_Source: {files}{run}; {len(samples)} samples._"
    text = structure.doc_path.read_text(encoding="utf-8")
    updated = refresh_doc(structure, text, Measurements.from_samples(samples), source)
    if updated == text:
        print(f"  same  {_rel(structure.doc_path)}")
    else:
        structure.doc_path.write_text(updated, encoding="utf-8")
        print(f"  update  {_rel(structure.doc_path)}")
    print(f"  data    {len(samples)} samples from {len(used)} file(s)")
    if run_id:
        print(f"  run     {run_id}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("list", help="list structures, their class and backends")
    init = sub.add_parser("init", help="create results/<name>/ and the research doc")
    init.add_argument("structure", help="module name, e.g. queue, dynamic_array")
    tables = sub.add_parser("tables", help="sync rows, refresh measured columns")
    tables.add_argument("structure")
    tables.add_argument("--run-id", help="data run to use (default: newest)")
    args = parser.parse_args(argv)
    commands = {"list": cmd_list, "init": cmd_init, "tables": cmd_tables}
    return commands[args.command](args)


if __name__ == "__main__":
    raise SystemExit(main())
