# Next scanlog review: testing headroom

Recorded October 7, 2026, at approximately 22:43 UTC.

## Decision

The user approved doubling the testing allowance from 200 to **400 requests/minute**
before collecting the next recordings. This supersedes the initial decision to
hold at 200/minute. The next session should check whether the higher testing load
leaves adequate headroom and preserves operational polling cadence, rather than
assuming the theoretical baseline savings translate directly into capacity.
The allowance includes the active research wave and existing experimental
commands; regular polling is separate and unchanged by this budget increase.

The testing configuration is TG0.1 active for 2019, with **57 available waves**.
Its eight staged commands request **330 polls/minute**, plus approximately
24.02/minute for the existing experimental commands: **354.02/minute combined**.
Other waves remain parked; rotation is manual. The busiest configured wave plus
background testing requests approximately **396.02/minute**. The allowance is a
ceiling, not a target that every wave must fill. See
`tests/research/staging-groups.json` and `scripts/staging.py`.

## Baseline and cutoff

- Polling-tier implementation: commit `292afc5`, pushed to the fork's `main`.
  Commit time: October 7, 2026, 22:39:38 UTC. Confirm when the client actually
  loaded this signal set; commit time alone does not prove deployment.
- Latest BMW session in the current uploaded bundle: local session PK **5397**,
  October 7, 2026, **17:10:37.668926–17:14:33.389923 UTC**. This predates the tier
  change. Its PK is a local reference, not a stable identifier across exports.
- Compare later recordings, preferably sessions collected after this handoff
  with both the polling tiers and the **400/minute testing configuration** confirmed
  active. The tier commit alone still used the old 200/minute allowance. Do not mistake the currently
  uploaded session for a post-change measurement.
- Configured demand for all 39 regular commands fell from **2,946 to 2,209.4
  requests/minute** (736.6 fewer, about 25%). This sums `60 / freq` for regular
  commands available to model year 2019, before and after the tier change.
- For the 23 regular commands identified by routed requests in session 5397,
  the same calculation falls from **2,092 to 1,161 requests/minute** (about 44.5%).
  This is the observed command subset evaluated under two configurations, not
  two measured runs.
- Session 5397 contained 2,397 request records beginning with service 01, 09, or
  22 across 3.929 minutes: approximately **610 diagnostic requests/minute**.
  This rough session-wide figure includes startup/research requests and excludes
  adapter setup commands. It is not an estimate of maximum adapter capacity.

## Next-session procedure

1. Use the workspace `skills/pelican-scanlogs/SKILL.md` helper. Query the SQLite
   bundle read-only, keep sidecars intact, and identify BMW sessions independently
   of scan date. Do not publish VINs or the full private database.
2. Confirm the loaded signal-set revision, active testing wave, model year, and
   debug collection settings. Match commands using header, extended address,
   receive address, and request; identical DIDs alone are insufficient.
3. Compare several post-change sessions with comparable operating conditions and
   the same adapter. Separate connection/startup periods and pauses from steady
   scanning. Distinguish regular, experimental, and staged research requests.
4. Measure each command's achieved interval (median and upper percentiles),
   delivered requests per minute, negative/no-data replies, and setup traffic.
   Check whether operational signals approach their requested cadence while
   research polling remains within its allowance. Use response-time or idle-gap
   information only where the log semantics support that interpretation.
5. Assess whether an increased research workload could preserve operational
   cadence without increased delays, failures, or timeouts. Lower requested
   demand alone does not prove unused transport capacity: client scheduling,
   selected signals, and ECU response time also affect delivered rates.
6. Report whether the 400/minute allowance is sustainable. If operational
   cadence deteriorates or failures increase, recommend reducing the testing
   load; if there is measurable spare capacity, propose a further increase.
   Keep **400/minute** pending review and user approval of another change.
   Update wave packing, the background reservation, documentation, and budget
   regression tests together for any approved change.

The raw-byte fixtures and decoding hypotheses remain available for the separate
PID-decoding review. Better decoding evidence and polling headroom are related
research tasks, but a faster scan does not establish a candidate's physical scale.
