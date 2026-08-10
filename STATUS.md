# status

state: active
remote: github-public
updated: 2026-08-10
stale-after-days: 30

## kpi
None. The value of this project is whether the analysis holds up when someone reads it,
which is not a number. Declared deviation from the 1-3 KPI rule.

## now
Complete and public: round-based synthetic generator, 4,593 deliveries over 769 routes and
26 weeks, the analysis notebook, and a README carrying the findings. Description and eight
topics set, MIT licence, in sync with the remote.

## backlog
- nothing open

## log
- 2026-08-10 — published. The five commits built on 2026-08-08 had never been pushed and
  the public repository was empty for two days; description and topics set at the same
  time — evidence: `gh api repos/nqwrc/transport-performance-analysis/contents` returned
  "This repository is empty"
- 2026-08-08 — built: the generator rewritten as a round simulation (`route_id`,
  `stop_seq`), notebook executed, README with the findings — evidence: commits 8a677c3
  to 51f2100
