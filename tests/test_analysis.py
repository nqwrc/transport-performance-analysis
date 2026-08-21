"""Pins for the headline numbers in the README and in
notebooks/01_transport_analysis.ipynb's Conclusions section, computed
against the committed, seeded data/deliveries.csv (random.seed(7) in
data/generate_data.py). If the generator changes, these will need
re-measuring and updating alongside it -- see tests/conftest.py's
load_deliveries for exactly how each column is derived.

Also documents a known latent bug: the notebook extracts AM/PM from
route_id with a fixed slice, df['route_id'].str[-5:-3], which assumes a
single-digit van id. It works today because VANS = 3 in data/generate_data.py;
it silently breaks once a 10th van is introduced. See
test_slot_extraction_breaks_past_9_vans below.

Run:  pytest
"""

VANS = 3  # data/generate_data.py -- the slot-extraction slice below is only
# correct while every van id is a single digit ("V1".."V9").


def test_overall_on_time_rate(deliveries_df):
    """README 'Key Operational Findings' and the notebook's Conclusions
    both open with this number."""
    total = len(deliveries_df)
    on_time = int(deliveries_df["on_time"].sum())

    assert total == 4593
    assert on_time == 4043
    assert round(on_time / total * 100, 1) == 88.0


def test_punctuality_drift_across_stop_sequence(deliveries_df):
    """README: 'On-time rate drops from 97% at Stop 1 to 75% by Stop 7'.
    Notebook cell 7 filters to stop_seq groups with >= 50 rows before
    reading the trend off the chart; stop 7 is the last one the README's
    wording anchors on, so both ends are pinned by exact fraction here."""
    by_seq = deliveries_df.groupby("stop_seq")["on_time"].agg(["sum", "size"])
    by_seq = by_seq[by_seq["size"] >= 50]

    stop1_on_time, stop1_total = by_seq.loc[1, "sum"], by_seq.loc[1, "size"]
    stop7_on_time, stop7_total = by_seq.loc[7, "sum"], by_seq.loc[7, "size"]

    assert (stop1_on_time, stop1_total) == (747, 769)
    assert (stop7_on_time, stop7_total) == (213, 285)
    assert round(stop1_on_time / stop1_total * 100, 1) == 97.1
    assert round(stop7_on_time / stop7_total * 100, 1) == 74.7


def test_b2b_far_zone_vs_depot_city_split(deliveries_df):
    """README: 'B2B delivery windows (2h) experience severe lateness in far
    zones (61.0% in Ferrara vs 98.7% in depot city)'."""
    b2b = deliveries_df[deliveries_df["customer_type"] == "B2B"]

    fe = b2b[b2b["zone"] == "FE"]
    ra_city = b2b[b2b["zone"] == "RA-city"]

    assert (int(fe["on_time"].sum()), len(fe)) == (50, 82)
    assert (int(ra_city["on_time"].sum()), len(ra_city)) == (469, 475)
    assert round(fe["on_time"].mean() * 100, 1) == 61.0
    assert round(ra_city["on_time"].mean() * 100, 1) == 98.7


def test_slot_extraction_matches_the_actual_slot_field(deliveries_df):
    """The route_id slice the notebook uses agrees with a robust split, for
    every row in the committed dataset -- today's positive case for the
    boundary documented below."""
    from_slice = deliveries_df["route_id"].str[-5:-3]
    from_split = deliveries_df["route_id"].str.split("-").str[3]

    assert set(from_slice.unique()) == {"AM", "PM"}
    assert (from_slice == from_split).all()


def test_slot_extraction_breaks_past_9_vans():
    """Documents the boundary rather than fixing it (fixing it means editing
    the notebook, out of scope here): route_id.str[-5:-3] counts from the end
    of the string, so it only lands on "AM"/"PM" while every van id is one
    digit. VANS = 3 in data/generate_data.py today keeps every id in "V1".."V9",
    so the bug is latent, not triggered -- but it is a ticking one: reached the
    day someone raises VANS to 10 without revisiting this slice."""
    single_digit_van = "2026-01-07-AM-V9"
    assert single_digit_van[-5:-3] == "AM"

    double_digit_van = "2026-01-07-AM-V10"
    assert double_digit_van[-5:-3] == "M-"  # silently wrong, not an error
    assert VANS < 10, "VANS grew past single digits: revisit the route_id slot slice"
