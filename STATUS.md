# status

state: paused
goal: G4
remote: github-public
updated: 2026-09-21
stale-after-days: 30

## kpi
None. The value of this project is whether the analysis holds up when someone reads it,
which is not a number. Declared deviation from the 1-3 KPI rule.

## now
Complete and public: round-based synthetic generator, 4,593 deliveries over 769 routes and
26 weeks, the analysis notebook, and a README carrying the findings. Description and eight
topics set, MIT licence, in sync with the remote. Tests and CI added 2026-08-21, local only
(3 commits ahead of the pushed HEAD) — see log.

## backlog
- push the 3 local commits (fix + test + ci) so the workflow actually runs on GitHub
  Actions; local pytest and a simulated fresh-clone run were verified green on Python
  3.11 and 3.13, but no real Actions run exists yet since nothing has been pushed

## log
- 2026-08-21 — tests+CI added, mirroring tool-warehouse-kpi-dashboard's pattern
  (c8ad338/54bab87/bda5802): `lineterminator="\n"` fix + `.gitattributes` so a
  regenerated data/deliveries.csv is byte-identical to the committed blob (verified:
  `git diff --cached` staged no change to the CSV); a 9-test pytest suite pinning
  generator reproducibility, the headline counts (4,593 deliveries / 769 routes / 26
  weeks, 2026-01-07 to 2026-07-05), the three README/notebook headline numbers (88.0%
  overall on-time, 97.1% -> 74.7% stop-sequence drift, 61.0% FE vs 98.7% RA-city B2B
  split) and the route_id slot-extraction bug boundary (`str[-5:-3]` breaks past
  VANS >= 10, latent while VANS = 3); a GitHub Actions workflow running pytest first
  against the pristine checkout, then the generator + `git diff --exit-code data/` —
  evidence: commits 6c11909, fcaf684, 66d0d16. Verified in a separate fresh clone
  (not the repo's own `.venv`) with Python 3.11 and 3.13 — both pytest and the
  pipeline diff check passed; Python 3.10 itself was not available on this machine
  to test directly, only 3.11+. Reviewed with `/code-review --level high` (single
  pass, Agent tool unavailable in this session): no findings. Commits are local only,
  not pushed — per this repo's CLAUDE.md, public/CV-adjacent code changes are not
  delegated outside a driving session, and the 2026-08-20 campaign session that lifted
  that boundary requires an adversarial-review gate before any public push, which has
  not run.
- 2026-08-10 — published. The five commits built on 2026-08-08 had never been pushed and
  the public repository was empty for two days; description and topics set at the same
  time — evidence: `gh api repos/nqwrc/transport-performance-analysis/contents` returned
  "This repository is empty"
- 2026-08-08 — built: the generator rewritten as a round simulation (`route_id`,
  `stop_seq`), notebook executed, README with the findings — evidence: commits 8a677c3
  to 51f2100
