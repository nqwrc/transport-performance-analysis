"""
Synthetic delivery data for a B2B/B2C furniture transport operation.

Modeled on real work: daily delivery rounds out of a Ravenna depot across
province zones, agreed time windows, transport documents (DDT), and the
discrepancies that actually happen (missing item, transport damage, wrong
address, refused goods).

The generator simulates ROUNDS, not isolated deliveries. A van leaves the
depot at the start of a time slot and the clock carries over from stop to
stop, so a slow stop pushes everything behind it. That is the real reason
a delivery misses its window: the round drifts, and the last stops pay for
it. Nothing here is a "lateness probability" pulled out of thin air —
drive time comes from distance and speed, handling time from how many
pieces come off the van and whether they go up three flights of stairs.

Run:  python data/generate_data.py  ->  data/deliveries.csv
"""

import csv
import random
from datetime import date, datetime, time, timedelta
from pathlib import Path

random.seed(7)

START = date(2026, 1, 7)
WEEKS = 26
VANS = 3

# --- Zones ---------------------------------------------------------------
# km    distance from the Ravenna depot to a delivery address in the zone
# hop   km between two consecutive stops inside the zone (dense in the city,
#       sparse in the far provinces)
# stops how many drops realistically fit in one half-day round there
ZONES = {
    "RA-city": {"km": (5, 20), "hop": (3, 8), "stops": (6, 8), "share": 0.30},
    "RA-province": {"km": (15, 45), "hop": (6, 14), "stops": (5, 7), "share": 0.25},
    "FC": {"km": (25, 60), "hop": (8, 18), "stops": (5, 6), "share": 0.15},
    "BO": {"km": (50, 90), "hop": (8, 20), "stops": (4, 5), "share": 0.15},
    "FE": {"km": (60, 110), "hop": (10, 22), "stops": (3, 5), "share": 0.08},
    "RN": {"km": (45, 80), "hop": (6, 16), "stops": (4, 6), "share": 0.07},
}
FAR = {"BO", "FE", "RN"}

# A far zone needs more rounds to place the same number of drops, because
# fewer stops fit in one. Dividing the target share by the average stops per
# round keeps the resulting DELIVERY mix close to the shares above.
ROUND_WEIGHTS = [
    z["share"] / ((z["stops"][0] + z["stops"][1]) / 2) for z in ZONES.values()
]

# --- Time slots ----------------------------------------------------------
# Shops receive early and have a narrow 2h window (someone has to be at the
# dock); private customers get the standard 4h window.
SLOTS = {
    "AM": {"depart": time(8, 0), "B2B": ("08:00", "10:00"), "B2C": ("08:00", "12:00")},
    "PM": {"depart": time(14, 0), "B2B": ("14:00", "16:00"), "B2C": ("14:00", "18:00")},
}

AVG_SPEED_KMH = 55  # a loaded van on provincial roads, not motorway cruising
TRAFFIC = (0.9, 1.4)  # multiplier on drive time: roadworks, town centres, ZTL

# Handling minutes at the stop: (fixed, per item). A shop takes the pallet at
# the dock and signs the DDT; a private address means stairs, unpacking and
# carrying the packaging back to the van.
HANDLING = {"B2B": (6, 2), "B2C": (10, 5)}
DISCREPANCY_HANDLING = 12  # phone call, note on the DDT, reload if refused

VAN_HALF_DAY_EUR = 128.0  # driver + van for one half-day round
COST_PER_KM = 0.65  # fuel, tyres, maintenance


def draw_items(customer: str, far: bool) -> int:
    """Load size. Nobody drives to Ferrara for one bedside table, so far
    rounds carry consolidated orders; shops restock in bigger batches."""
    if customer == "B2B":
        return random.randint(4, 10) if far else random.randint(3, 8)
    return random.randint(2, 6) if far else random.randint(1, 4)


def draw_discrepancy(customer: str, n_items: int, km: int) -> str:
    """At most one discrepancy per delivery — the one the driver writes on
    the DDT. Probabilities follow the mechanism, not a flat rate:
    more lines means more chance one is short, more km and more pieces mean
    more handling damage, private addresses are the ones you cannot find,
    and only a shop has a receiving procedure strict enough to refuse."""
    risks = {
        "missing_item": 0.008 + 0.0035 * n_items,
        "transport_damage": 0.004 + 0.00020 * km + 0.0015 * n_items,
        "wrong_address": 0.010 if customer == "B2C" else 0.002,
        "refused": 0.016 if customer == "B2B" else 0.003,
    }
    for kind, probability in risks.items():
        if random.random() < probability:
            return kind
    return ""


def stops_in_round(day: date, zone_cfg: dict, far: bool) -> int:
    """Base capacity of the zone, plus the two peaks anyone who has driven
    these rounds knows: Monday clears the weekend orders, and April-June is
    when people refurbish. Neither peak helps a far zone — the drive time is
    the binding constraint there, so no extra stop fits."""
    n = random.randint(*zone_cfg["stops"])
    if not far:
        n += 1 if day.weekday() == 0 else 0
        n += 1 if day.month in (4, 5, 6) else 0
    return n


rows = []
delivery_id = 20000

for week in range(WEEKS):
    for weekday in range(5):  # Monday-Friday rounds
        day = START + timedelta(weeks=week, days=weekday)
        for van in range(1, VANS + 1):
            van_back_at = None
            for slot_name, slot in SLOTS.items():
                start = datetime.combine(day, slot["depart"])
                # The afternoon round cannot leave before the morning one is
                # back and reloaded. This is how a bad morning turns into a
                # bad afternoon.
                if van_back_at is not None:
                    start = max(start, van_back_at + timedelta(minutes=20))
                    # Past a point you do not leave at all: the dispatcher
                    # moves those drops to another day rather than start a
                    # round that cannot possibly hit its window.
                    if start > datetime.combine(day, time(15, 0)):
                        continue

                zone = random.choices(list(ZONES), ROUND_WEIGHTS)[0]
                cfg = ZONES[zone]
                far = zone in FAR
                n_stops = stops_in_round(day, cfg, far)

                # B2B first: their window is half as wide, so the shops get
                # the early slots and the homes follow.
                customers = [
                    random.choices(["B2C", "B2B"], [0.7, 0.3])[0]
                    for _ in range(n_stops)
                ]
                customers.sort(key=lambda c: c != "B2B")

                clock = start
                route_km = 0
                stops = []
                for seq, customer in enumerate(customers, start=1):
                    km = random.randint(*cfg["km"])  # depot -> this address
                    leg = km if seq == 1 else random.randint(*cfg["hop"])
                    route_km += leg
                    clock += timedelta(
                        minutes=leg / AVG_SPEED_KMH * 60 * random.uniform(*TRAFFIC)
                    )
                    arrival = clock

                    n_items = draw_items(customer, far)
                    discrepancy = draw_discrepancy(customer, n_items, km)
                    fixed, per_item = HANDLING[customer]
                    handling = fixed + per_item * n_items
                    handling += DISCREPANCY_HANDLING if discrepancy else 0
                    clock += timedelta(minutes=handling)

                    stops.append((seq, customer, km, n_items, discrepancy, arrival))

                route_km += stops[-1][2]  # drive home from the last address
                van_back_at = clock + timedelta(
                    minutes=stops[-1][2] / AVG_SPEED_KMH * 60
                )

                # A round is a joint cost: the van and the driver are paid for
                # the half-day whatever happens, so the only honest way to get
                # a per-delivery figure is to split the round evenly.
                cost = (VAN_HALF_DAY_EUR + route_km * COST_PER_KM) / n_stops
                route_id = f"{day.isoformat()}-{slot_name}-V{van}"

                for seq, customer, km, n_items, discrepancy, arrival in stops:
                    delivery_id += 1
                    window_start, window_end = slot[customer]
                    rows.append(
                        {
                            "delivery_id": delivery_id,
                            "delivery_date": day.isoformat(),
                            "route_id": route_id,
                            "stop_seq": seq,
                            "zone": zone,
                            "customer_type": customer,
                            "n_items": n_items,
                            "distance_km": km,
                            "window_start": window_start,
                            "window_end": window_end,
                            "arrival_time": arrival.strftime("%H:%M"),
                            "discrepancy_type": discrepancy,
                            "transport_cost_eur": round(cost, 2),
                        }
                    )

out = Path(__file__).with_name("deliveries.csv")
with out.open("w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)

routes = {r["route_id"] for r in rows}
print(f"{out.name}: {len(rows):,} deliveries · {len(routes):,} routes · {WEEKS} weeks")
