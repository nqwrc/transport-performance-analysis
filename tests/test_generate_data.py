"""Tests for the synthetic data generator: it must be fully reproducible
(fixed seed = 7) and it must produce the shapes the README and the analysis
notebook are pinned against.

Run:  pytest
"""

import shutil
from pathlib import Path

from tests.conftest import REPO_ROOT, run_python


def generate_in(tmp_path: Path, name: str) -> Path:
    """Run the real generate_data.py in its own isolated `data/` folder."""
    run_dir = tmp_path / name
    (run_dir / "data").mkdir(parents=True)
    shutil.copy(REPO_ROOT / "data" / "generate_data.py", run_dir / "data" / "generate_data.py")
    run_python("data/generate_data.py", cwd=run_dir)
    return run_dir / "data"


def test_generator_output_is_byte_identical_across_runs(tmp_path):
    """random.seed(7) makes the whole generator deterministic: two runs must
    produce byte-identical CSVs, not just the same row counts."""
    content_a = (generate_in(tmp_path, "run_a") / "deliveries.csv").read_bytes()
    content_b = (generate_in(tmp_path, "run_b") / "deliveries.csv").read_bytes()

    assert content_a == content_b, "deliveries.csv differs between two seeded runs"


def test_generator_matches_the_committed_dataset(tmp_path):
    """The CSV committed under data/ is exactly what the generator produces
    today -- if this drifts, the committed dataset is stale."""
    generated = (generate_in(tmp_path, "run") / "deliveries.csv").read_bytes()
    committed = (REPO_ROOT / "data" / "deliveries.csv").read_bytes()

    assert generated == committed, "committed data/deliveries.csv is out of date"


def test_generator_produces_the_headline_counts(tmp_path):
    """Pinned against the numbers the README's Mermaid diagram and Key
    Operational Findings quote: 4,593 deliveries over 769 routes."""
    data_dir = generate_in(tmp_path, "run")
    lines = (data_dir / "deliveries.csv").read_text().splitlines()
    header, rows = lines[0], lines[1:]

    assert len(rows) == 4593
    route_id_col = header.split(",").index("route_id")
    routes = {row.split(",")[route_id_col] for row in rows}
    assert len(routes) == 769


def test_generator_covers_26_weeks_of_weekday_rounds_from_2026_01_07(tmp_path):
    """WEEKS = 26, Monday-Friday rounds only, starting the first Monday of 2026."""
    data_dir = generate_in(tmp_path, "run")
    lines = (data_dir / "deliveries.csv").read_text().splitlines()[1:]
    dates = {line.split(",")[1] for line in lines}

    assert min(dates) == "2026-01-07"
    assert max(dates) == "2026-07-05"  # 26 weeks * Mon-Fri, last week's Friday
    assert len(dates) == 130  # 26 weeks * 5 weekdays, no weekend rounds
