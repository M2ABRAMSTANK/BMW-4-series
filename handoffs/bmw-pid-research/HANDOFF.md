# Project: BMW PID research

- Project ID: `BMW-4-series/bmw-pid-research`
- Status: Flat testing-picker follow-up complete and validated; delivery target is fork `main` after published baseline `25ee899`.
- Owner/session: Codex primary agent, resumed October 13, 2026 for the user-requested flat testing picker; prior implementation session complete. Clean dedicated project worktree reused.
- Repository: `M2ABRAMSTANK/BMW-4-series`; primary `/Users/rowdyer/Coding/OBDb/repos/BMW-4-series`.
- Branch: `project/bmw-430i-research-integration`.
- Worktree: `/Users/rowdyer/Coding/OBDb/repos/BMW-4-series--research-integration`.
- Updated: October 13, 2026.

## Current follow-up: flat testing picker

The user requested removing the nested complete-group folder and placing all
research and reference readings together at the TG level. All 67 native groups
now have parent path `Battery.Testing` and names such as `TG0_1`. Removed the
1,056 candidate signal paths that separately created candidate-only TG folders;
those signals remain members of the complete native group. The manifest's
`path` remains the full displayed destination, e.g. `Battery.Testing.TG0_1`.
Group regex membership, signal IDs, hidden flags, decoders, commands, reference
membership, and polling settings are unchanged. This layout supersedes the
candidate-folder description below. Primary checkout and other projects are
untouched. No other editor was recorded for this project at resume.

Validation: `bash scripts/test-repo.sh BMW-4-series--research-integration
--maxfail=5` passed **1,896 tests, 1 xfailed** (the existing CAN-padding expected
failure); log `/private/tmp/bmw-flat-groups-tests.log`. Semantic comparison to
`25ee899` verifies that only candidate paths and native group path/name changed.
The existing picker tests verify all 67 full destinations and visible candidate
memberships, reference inclusion, and request budgets. `git diff --check` passes.

Delivery uses the existing authorized fork workflow: `origin` was verified as
`https://github.com/M2ABRAMSTANK/BMW-4-series.git`; fetched `main` before committing.
Keep this worktree available. Next: reload the fork signal set and verify the
rendered picker; repository tests cannot establish the app's runtime presentation.

## Current resume: scanlogs and manual testing groups

This section is the current policy and supersedes all debug, parking, tiered
interval, and 400/minute instructions in the historical record below. User
instructions on October 13 explicitly remove debug, use approximately 700
requests/minute including all other reads, and make every group visible for
manual selection under Battery. The user confirmed “Show all groups for manual
selection.” This existing project worktree was clean at resume; no other editor
was recorded. Its dedicated branch was reused. Primary checkout changes and
other worktrees remain untouched.

### Evidence

- Read-only review of canonical `scanlogs/originals/sidecar.scanlogs`, sessions
  5421–5444; VIN equality to established session 5420 selected 18 sessions and
  excluded six empty VIN-less sessions. No VIN is exported in new artifacts.
- 59,264 service 01/22 reads reviewed with chronological adapter state. Routed
  positive/negative/no-data captures, exact raw hex, original session/record/
  command IDs, timestamps, setup state and setup record IDs are retained in
  [the report](../../tests/research/sessions-5421-5444-review.json).
- All eight TG0.1 commands have positive two-byte payloads, no negative replies,
  and multiple distinct payloads in the review. 4204/4310/4402/4409/4425 each
  have 132 positives; 4421/4422/4423 each have 161. Eight real raw-byte fixtures
  were added. Positive replies confirm response support, not meanings/scaling.
- None of the 26 latest external requests was observed on its configured route;
  their support remains untested. No new 7DF/7E8 0141 or 0183 capture was found.
  External acquisition provenance remains unobserved and source hypotheses are
  preserved. No 4402 promotion or other physical decoder change was made.
- Latest session-wide service 01/22 rates: 5441 about 812/min, 5442 about 303/min,
  5444 about 477/min. These include startup and do not establish a 700/min cap.

### Configuration and selection

- Removed every `dbg` and `dbgfilter` field. All 1,102 command identities/routes,
  1,855 signal IDs/scalings/hidden states, and diagnostic session parameters are
  unchanged. The 583 known rejected commands retain their 2019 exclusions.
- All 406 original staged requests are available for 2019. Preserved 64 group
  memberships; added TG17.1/17.2 for nine other experimental requests and
  TG18.1 for two uncaptured service 01 reads: 67 groups, 417 candidates total.
- Candidate folders are `Battery.Testing.TG0_1`, etc.; display names retain
  `[TG0.1]`. Native `signalGroups` regex membership includes candidate signals
  and reference reads without duplicating command definitions. Known rejected
  signals have an “Unavailable on 2019” folder and remain unavailable for 2019.
- Every group includes eight common reference reads (RPM, speed, load, fuel
  rate, fuel level, coolant, oil temperature, module voltage), with additional
  references where relevant. Unique requests count once across overlapping
  groups. Individual groups contain 9–19 total requests; TG0.1 is 18 requests,
  about 0.648 Hz each at the assumed 700/minute throughput.
- No tier schedule is used. Because the schema requires a positive `freq`,
  definitions use 0.01 seconds as a nonbinding ready-to-poll minimum, not a
  100-Hz target or runtime rate limiter. Client selection/throughput governs
  actual scans. Additional background reads must be counted too.
- `scripts/staging.py` is now read-only. It lists groups or estimates combined
  selections, deduplicating shared references. `--extra KEY` adds other named
  reads; `--background-count N` accounts for additional distinct unnamed reads.
  It no longer toggles availability, writes files, or parks groups.

### Validation and next actions

`bash scripts/test-repo.sh BMW-4-series--research-integration --maxfail=5`
passed **1,896 tests, 1 xfailed** in 1.99 seconds (log
`/private/tmp/bmw-manual-final.log`). The existing expected failure covers
single-frame CAN padding in external schema tooling. Native group regex matches,
reference inclusion, budget deduplication, additional background traffic,
2019 exclusions, capture fixtures, formatting and schema validation pass.
`git diff --check` passes. Source database was read only.

Next: load this local signal set in the app, manually select a group plus any
additional dashboard reads, and record target replies for TG10–TG16 and TG18.1.
Verify app picker behavior and actual throughput; offline tests cannot do this.
Do not treat all visible groups as simultaneously selected. Changes remain in
`/Users/rowdyer/Coding/OBDb/repos/BMW-4-series--research-integration` on
`project/bmw-430i-research-integration`. The October 13 full-permissions resume
authorized committing these changes and publishing to `M2ABRAMSTANK/BMW-4-series`
`main`. Fetch verified remote main at `f3349d8` before publication, matching the
local parent commit. Final publication verification is recorded in the workspace
`handoffs/github-write-approvals/HANDOFF.md`.

## Historical implementation record

The sections below preserve provenance through the service 01 integration.
Their old policy instructions are historical and superseded by the section above.

## Objective and scope

Maintain one comprehensive research project for the 2019 BMW 430i's PID opportunities. This consolidates the R42 external-export inventory and the scanlog/testing-headroom review. Preserve all source candidates and existing staged research, expose captured raw data for analysis, and promote decoded measurements only when their meaning and applicability are supported. The approved implementation covers the reviewed candidates and raw research views, alongside staged discovery. Do not fabricate firmware fitment or vehicle captures. No 4402 promotion is part of this task; retain its current repository decoder/raw status while preserving the corroboration evidence for a later decision.

The active implementation worktree is dedicated to this project. Keep all configuration and documentation changes scoped to this branch. Do not edit other projects' worktrees.

## Current state and evidence

The R42 evidence remains in the root workspace archive under [the earlier export-review project](../../../../handoffs/bmw-430i-research-integration/HANDOFF.md). Its [full-scope review](../../../../handoffs/bmw-430i-research-integration/FULL-SCOPE.md), [all-profile index](../../../../handoffs/bmw-430i-research-integration/snapshots/r42/external-profile-index.md), [all-staged-command index](../../../../handoffs/bmw-430i-research-integration/snapshots/r42/all-staged.md), and machine-readable snapshots remain the immutable supporting inventory. They record 529 working external BMW profiles / 1,355 field rows and all 380 already-staged positive-response commands. These are research inputs, not claims that every field works on the target car.

The separate [testing-headroom review](../../../../repos/BMW-4-series--testing-headroom-review/handoffs/testing-headroom/REVIEW.md) covers sessions 5400–5420 and preserves its detailed route evidence. Its [handoff](../../../../repos/BMW-4-series--testing-headroom-review/handoffs/testing-headroom/HANDOFF.md) and the older migrated [primary handoff](../../../../repos/BMW-4-series--project-handoffs/handoffs/testing-headroom/HANDOFF.md) are historical evidence. They document earlier policy states; the uniform policy below supersedes their conflicting statements about removing debug gating from the active wave. Do not edit or relocate those artifacts.

The implementation inventory is **26 new read requests**: 21 shared-function reads, three EGS adaptation reads, FEM DAD6 terminal voltage, and the lower-confidence DME F150 lead. The 26 acquisition records are kept separately from the original 529-profile/1,355-field source inventory in [external-research.json](../../tests/research/external-research.json); its target capture claim is false and no captures are fabricated. These add **339 raw research signals**, bringing the repository to **1,037 command objects and 1,676 signal objects**. The 339 byte views are not 339 physical sensors: D12F alone contributes 210 byte views for a long-response trip-history hypothesis. The 380 existing staged commands expose 684 raw channels across 57 waves. Seven new discovery waves bring the total to **406 staged commands, 1,023 raw research signals, and 64 waves**. Counts describe configuration/research objects, not independently verified vehicle capabilities.

Source route details remain bounded: D114 and D96B receiver routes should be treated as source-derived hypotheses and cross-validated against available evidence, not null routes. DAD6 uses a CAN route informed by BMW addressing (`40`/`640`); its source profile describes HSFZ, and there is no target CAN capture. EGS DIN `03` / DOUT `01` metadata supports the request hypothesis, while exact target support and session behavior remain unverified. EGS research reads are read-only and must not invoke control or reset operations.

## Known schema-tooling limitation

The installed OBDb schema tooling at `442b82a` leaves padding on single ISO-TP frames instead of trimming to the declared PDU length; its multi-frame scanner does trim. Synthetic tests exercise missing-byte behavior with adapter-trimmed single frames and use a strict expected failure for the padded-single-frame regression. This describes the test tooling only and does not establish client runtime behavior. Preserve complete raw responses and honor declared lengths when assessing captures; do not promote fields backed only by missing or unconfirmed bytes. The schema is an external ignored dependency, and this project does not include a parser fix.

## Current polling and raw-data policy

- Keep all 380 existing staged commands configured with `dbg: true`, including selected wave TG0.1. Preserve the current command membership, filters, and requested intervals: 1 second for dynamic candidates, 2 seconds for temperature/voltage/level candidates, and 10 seconds for slower counters/adaptations. The selector must preserve debug status when rotating active waves. Existing cadence results show that configured intervals do not establish achieved cadence; collect further evidence before changing the budget or schedule.
- The 26 new reviewed candidates use ordinary intervals by intended use: temperature 15 s, ambient 60 s, HVAC/body states 5 s, trip/history 300 s, range 60 s, steering/GPS/wheel/pedal 0.25 s, IBS/FEM 5 s, EGS adaptations 300 s, and F150 60 s. They expose 339 unconverted byte views in `OBD.Testing.<category>` and enter seven staged debug discovery waves for full-response collection. D12F contributes 210 views for a long-response trip-history hypothesis; these are raw bytes, not 210 separate physical measurements.
- New discovery wave plan: TG10.1 cluster (7), TG11.1 climate (7), TG12.1 body including FEM (3), TG13.1 steering (1), TG14.1 NBT (2), TG15.1 pedal/IBS/F150 (3), and TG16.1 EGS (3). Keep TG0.1 selected; park the seven new waves with the existing `filter.years: [9999]` convention until deliberately selected. All 406 staged commands retain `dbg: true`.
- Preserve the 400 requests/minute testing ceiling and the existing staged group structure while implementing. Record negative replies and full response evidence; a positive reply establishes response support only, not field identity or scaling.
- Keep source route/session assumptions labeled as hypotheses until target evidence resolves them. Do not claim exact ECU firmware compatibility, completed vehicle polling, or new captures without evidence.
- No 4402 decoder promotion is included in this implementation. It remains at its existing repository status despite the corroboration documented by the headroom review.

## Validation

The pre-implementation baseline in this fresh worktree passed **1,645 tests** in 0.99 seconds (`/private/tmp/bmw-r42-baseline.log`). The final command, `bash scripts/test-repo.sh BMW-4-series--research-integration --maxfail=0 --junitxml=/private/tmp/bmw-r42-final.xml`, passed **1,751 tests with 1 xfailed test** in 1.93 seconds. The strict xfail covers the known external schema-tooling behavior for padded single ISO-TP frames; formatter/schema validation is included in the suite. `git diff --check` passed. These checks validate repository configuration and tests, not client runtime behavior or vehicle support. No vehicle polling was performed.

## Blockers and next actions

1. Finish service 01 integration, validate the combined implementation, and publish to the authorized fork when network access permits.
2. Continue controlled collection and interpretation as separate evidence updates. Preserve route hypotheses, the existing 400/minute ceiling, and the full raw-response evidence.
3. Revisit candidate meaning, target applicability, and polling cadence only when new captures or trusted references add evidence. Preserve the R42 and scanlog review records as supporting history.

## Preservation and integration

At the October 12 handoff the dedicated project branch/worktree was uncommitted for review. The October 13 resume preserved that implementation in commit `6408ab5`; publication and service 01 integration are tracked below. No primary-checkout integration was performed. The primary checkout had pre-existing changes (`.gitignore`, `HANDOFF.md`, and untracked `tests/research/session-5400-review.json`); its tracked diff still matches the captured pre-work patch byte-for-byte and the untracked artifact hash is unchanged. Baseline comparison confirmed the 1,011 old command objects are unchanged except for the eight intended `dbg: true` settings, and all 57 old staging groups and top-level metadata are unchanged. The testing-headroom review worktree and migrated historical handoff remain untouched. Root archive artifacts are retained in place and linked rather than copied into a second editable project.

## October 13 resume

The user authorized preserving all research requests as debug PIDs, retaining the
testing group structure, adding supported service 01 PIDs with explicit polling
intervals, and pushing the completed changes to their fork. Luna verified all
406 staged commands retain `dbg: true` across 64 groups and the selector preserves
that policy. Existing operational signals retain their ordinary status.

The prior implementation was preserved as commit `6408ab5`; its baseline passes
1,751 tests with one documented expected failure. Sol owns the dependent service
01 project in `/Users/rowdyer/Coding/OBDb/repos/BMW-4-series--service01`, branch
`project/bmw-service01`. Its changes will be reviewed and integrated here.

A remote fetch currently fails because this execution environment cannot resolve
`github.com`; an escalation request was rejected by the configured approval policy.
Local implementation and validation continue. Publication remains pending.

Luna independently compared `bb2381d` to `6408ab5`: all 1,011 prior command
identities are retained, the only eight prior-command changes set `dbg`, and
all 57 original group objects/memberships are unchanged. There are exactly 26
new commands and seven added groups.

## Integrated service 01 result

Sol's commits `64f9c4c` and `b76a754` are integrated on this project branch.
The [service 01 project handoff](../bmw-service01/HANDOFF.md) and
[provenance](../../tests/research/service01-2019-provenance.json) record a
read-only review of 3,267 same-vehicle sessions and 13,492,121 service 01 requests.
The 7E8 bitmaps advertise 47 data PIDs (45 captured); 7E9 advertises nine data
PIDs (all captured). All are represented in 65 route-specific definitions
including nine support-page reads. The 7E8 `0141` and `0183` candidates remain
parked debug discovery because no positive payload was captured. There are
63 real response fixtures. All new commands follow the six existing polling
tiers and matching description prefixes. Requested cadence is not measured
client cadence.

The full integrated suite passed **1,819 tests with one existing expected
failure**, via `bash scripts/test-repo.sh BMW-4-series--research-integration
--maxfail=0` (log `/private/tmp/bmw-service01-integrated.log`). `git diff
--check` passed. All 1,037 command objects from the research snapshot are
unchanged by service 01 integration; the total is 1,102 commands and 1,855
signals. Primary checkout changes and historical worktrees remain untouched.

Publication target is `origin` (`M2ABRAMSTANK/BMW-4-series`) branch `main`,
using this integration worktree's HEAD. No force push is authorized or needed.
The environment cannot resolve GitHub and disallows network permission
escalation. After connectivity is restored, fetch/review any new remote
commits and push with:

```sh
git -C /Users/rowdyer/Coding/OBDb/repos/BMW-4-series--research-integration push origin HEAD:main
```

Leave both project worktrees available for review. Future evidence collection
should verify client loading, service 01 override scheduling and achieved
cadence; preserve the 400/min testing ceiling and current debug group structure.
