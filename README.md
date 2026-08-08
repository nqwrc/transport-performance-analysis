# Transport Performance Analysis 🚚

On-time delivery, cost-per-route and discrepancy analysis for a **B2B/B2C
furniture transport operation** — synthetic data modeled on real delivery
rounds I worked (province zones, agreed time windows, transport documents,
and the discrepancies that actually happen on the road).

## What the analysis found

- **Punctuality is a scheduling problem, not a driving problem.** Overall
  on-time is 88.0% against a 90% target, and it falls with the position in
  the round — 97% at the first stop, 75% by the seventh. The afternoon slot
  runs ~5 points below the morning because it starts with the morning's
  delay.
- **The failure cluster is B2B in the far zones.** B2B looks healthy on
  average (87.0% against 88.5% for B2C), but split by zone it is the *best*
  served customer near the depot (98.7% in Ravenna city) and the *worst*
  far from it (61.0% in Ferrara). A 2h goods-in window does not survive a
  60+ km outbound leg followed by a second stop.
- **Distance sets the cost of a round; load size sets the cost of a piece.**
  RN costs 25% more per delivery than FC (€47.41 against €37.88) and 29%
  *less* per item (€11.68 against €16.43), because far rounds go out
  consolidated. Normalised per item the most expensive zone is FC — the
  same small orders as the city, three times the drive.
- **Discrepancies are a per-line risk**, 4.42% of deliveries. The rate
  tracks order size, not distance: the cleanest zone is BO at 3.9%, from
  69 km out.

## Questions it answers

- **On-time rate**: how many deliveries arrive inside the agreed window, by zone and customer type?
- **Cost per route**: which zones cost most per delivery and per item?
- **Discrepancies**: missing items vs transport damage vs wrong address — where and for whom?
- **B2B vs B2C**: different customers, different failure modes?

## Stack

Python · pandas · matplotlib · Jupyter

## Run it

```bash
pip install -r requirements.txt
python data/generate_data.py        # rebuilds data/deliveries.csv (4,593 deliveries, 769 routes, 26 weeks)
jupyter notebook notebooks/01_transport_analysis.ipynb
```

The generator is seeded, so it rebuilds the same CSV byte for byte.

## Data

One row = one stop on a delivery round.

| column | meaning |
|---|---|
| `delivery_id` | one per delivery |
| `delivery_date` | Monday–Friday, 26 weeks from 2026-01-07 |
| `route_id` | the round the stop belongs to: `date-AM/PM-Vn` |
| `stop_seq` | position of the stop within its round |
| `zone` | RA-city, RA-province, FC, BO, FE, RN |
| `customer_type` | B2B (shop, 2h window) or B2C (private address, 4h window) |
| `n_items` | pieces delivered |
| `distance_km` | depot to this address |
| `window_start`, `window_end` | the window agreed with the customer |
| `arrival_time` | when the van actually arrived |
| `discrepancy_type` | `missing_item`, `transport_damage`, `wrong_address`, `refused`, or empty |
| `transport_cost_eur` | the round's cost, split evenly across its stops |

### How it is generated

`data/generate_data.py` simulates **rounds**, not isolated deliveries. A van
leaves the depot at 08:00 or 14:00 and the clock carries over from stop to
stop: drive time comes from distance and speed, handling time from how many
pieces come off the van and whether they go up three flights of stairs.
Lateness is never drawn as a per-delivery probability — it is what is left
when the round has drifted past the window. Cost works the same way: the van
and the driver are paid for the half-day whatever happens, so a route is a
joint cost split evenly across its stops.

100% synthetic — no employer data. The patterns it encodes (zone mix, 2h B2B
windows against 4h B2C ones, consolidated far-zone loads, the Monday backlog
and the April–June peak) reflect first-hand experience.

## KPI definitions

- **On-time** = arrival within [`window_start`, `window_end`]
- **Cost per item** = `transport_cost_eur` / `n_items`, where
  `transport_cost_eur` = (van half-day cost + route km × €/km) / stops on the route
- **Discrepancy rate** = deliveries with any discrepancy / total deliveries
