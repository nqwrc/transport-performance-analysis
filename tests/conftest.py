"""Shared fixtures.

data/generate_data.py is a top-level script that writes to a relative path
(data/deliveries.csv), not an importable function. Reproducibility tests
therefore run it as a subprocess inside an isolated tmp_path directory, so a
test run never touches the real data/deliveries.csv in the repo working tree.

deliveries_df reimplements the derived columns notebooks/01_transport_analysis.ipynb
computes in its first code cell (arrival/window datetimes, on_time, slot) against
the committed, seeded CSV. That means the headline-number tests pin the notebook's
published results, not the notebook's code -- if the notebook's derivation logic
changes, these tests will not catch the drift on their own.
"""

import subprocess
import sys
from pathlib import Path

import pandas as pd
import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]


def run_python(script: str, cwd: Path, check: bool = True) -> subprocess.CompletedProcess:
    """Run `python <script>` with cwd set, raising on a non-zero exit.

    Pass check=False when the non-zero exit is the thing under test; the
    caller then asserts on returncode and stderr itself.
    """
    result = subprocess.run(
        [sys.executable, script],
        cwd=cwd,
        capture_output=True,
        text=True,
    )
    if check:
        assert result.returncode == 0, (
            f"{script} failed (exit {result.returncode})\n"
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )
    return result


def load_deliveries(csv_path: Path) -> pd.DataFrame:
    """Load a deliveries.csv and add the columns the notebook derives from it.

    Mirrors notebooks/01_transport_analysis.ipynb cell 1 exactly: keep_default_na=False
    (an empty discrepancy_type means "nothing went wrong", not NaN), arrival/window
    datetimes rebuilt from the text time columns, on_time, late_minutes, and the
    slot extracted from route_id ("2026-01-07-AM-V1" -> "AM").
    """
    df = pd.read_csv(csv_path, parse_dates=["delivery_date"], keep_default_na=False)

    day = df["delivery_date"].dt.date.astype(str)
    df["arrival"] = pd.to_datetime(day + " " + df["arrival_time"])
    df["w_start"] = pd.to_datetime(day + " " + df["window_start"])
    df["w_end"] = pd.to_datetime(day + " " + df["window_end"])

    df["on_time"] = (df["arrival"] >= df["w_start"]) & (df["arrival"] <= df["w_end"])
    df["late_minutes"] = (df["arrival"] - df["w_end"]).dt.total_seconds() / 60
    df["slot"] = df["route_id"].str[-5:-3]  # "AM" or "PM", from 2026-01-07-AM-V1

    return df


@pytest.fixture(scope="session")
def deliveries_df() -> pd.DataFrame:
    """The committed, seeded data/deliveries.csv with the notebook's derived columns."""
    return load_deliveries(REPO_ROOT / "data" / "deliveries.csv")
