# Project: BMW service 01 coverage

- Project ID: `BMW-4-series/bmw-service01`
- Status: Implemented and committed for integration.
- Owner/session: Sol agent, October 13, 2026.
- Repository: `M2ABRAMSTANK/BMW-4-series`; primary `/Users/rowdyer/Coding/OBDb/repos/BMW-4-series`.
- Branch: `project/bmw-service01`.
- Worktree: `/Users/rowdyer/Coding/OBDb/repos/BMW-4-series--service01`.
- Base: research integration commit `6408ab5`.
- Updated: October 13, 2026.

## Objective and scope

Implement the target 2019 BMW 430i's supported SAE service 01 PIDs with route-specific requests, canonical decoding, repo polling tiers, exact real response fixtures, and traceable source records. The prior research implementation and staged groups remain unchanged.

## Current state and evidence

The original Sidecar SQLite bundle was queried read-only. Session 5399 and 3,266 other sessions share the target VIN, whose model-year code is `K`; the VIN itself is withheld. The source query examined 13,492,121 service 01 request records for that VIN. Source session 1 and the later representative sessions use `ATSP6`, `ATH1`, functional `7DF`/reply `7E8`, and physical `7E1`/reply `7E9` routes. Each example's source session PK, record PK, command sequence, UTC timestamp, raw full response hex, reply excerpt, and preceding adapter setup are recorded in `tests/research/service01-2019-provenance.json`. The source bundle is not committed.

The `7E8` bitmaps advertise 47 data PIDs, 45 of which have positive payloads in the matched sessions. The `7E9` bitmaps advertise nine data PIDs, all nine with positive payloads. `7E8` PIDs `0141` and `0183` are advertised but have no captured positive payload; they are retained as parked debug discovery (`filter.years: [9999]`). `0141` uses the canonical readiness decoder if later confirmed; `0183` has only a tentative raw-byte view because the installed SAE definition has no decoder. All other data definitions reuse the installed SAEJ1979 decoder; `7E9` signal IDs have a route suffix to preserve uniqueness. PID `0168` has a canonical decoder and a captured multi-frame payload. Six `7E8` and three `7E9` support-page reads expose raw bitmap values.

The 65 new route-specific definitions are `7DF`/`7E8` for the engine-side replies (53 including support pages) and `7E1`/`7E9` for the second ECU (12 including support pages). Polling intervals follow the existing repository tiers: 0.25 s dynamic, 1 s short, 2 s thermal, 10 s medium/status, 60 s slow, and 3,600 s support-page discovery. There are 63 real positive-response fixtures, one for every captured route/PID combination, including the multi-frame `0168` case. The invalid-value catalog records null bounds copied unchanged from SAE definitions; these are not new BMW calibrations.

Configured intervals describe requested polling. Vehicle cadence and the combined runtime scheduler load were not measured. These service 01 additions do not alter the separate staged debug groups or their 400 requests/minute testing ceiling.

## Validation

`bash scripts/test-repo.sh BMW-4-series--service01 --maxfail=5` passed 1,818 tests with one existing expected failure for padded single-frame ISO-TP behavior in the ignored schema tooling. The suite covers schema/formatting, route-specific command selection, support bitmap coverage, numeric samples, and multi-frame reassembly. Ignored schema tooling and the generated response runner were copied from the research-integration worktree after online setup could not reach GitHub; they are not committed.

## Blockers and next actions

Coordinator should integrate this branch and review the route-specific service 01 cadence against the intended client schedule. No live vehicle polling was performed. If a future `7E8` `0141` or `0183` positive reply is captured, promote only after validating payload and decoder.

## Preservation and integration

The primary checkout's pre-existing `.gitignore`, `HANDOFF.md`, and untracked session review are untouched. This project uses its own branch/worktree and adds no VIN or raw scanlog bundle. Branch commit is recorded in the agent handoff message after commit.
