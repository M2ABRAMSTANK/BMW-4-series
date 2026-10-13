# Project: BMW PID research

- Project ID: `BMW-4-series/bmw-pid-research`
- Status: Implementation complete; awaiting user review.
- Owner/session: Codex, consolidated project session, October 12, 2026.
- Repository: `M2ABRAMSTANK/BMW-4-series`; primary `/Users/rowdyer/Coding/OBDb/repos/BMW-4-series`.
- Branch: `project/bmw-430i-research-integration`.
- Worktree: `/Users/rowdyer/Coding/OBDb/repos/BMW-4-series--research-integration`.
- Updated: October 12, 2026.

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

1. Review the implementation and its limits in this project worktree before any commit or integration.
2. Continue controlled collection and interpretation as separate evidence updates. Preserve route hypotheses, the existing 400/minute ceiling, and the full raw-response evidence.
3. Revisit candidate meaning, target applicability, and polling cadence only when new captures or trusted references add evidence. Preserve the R42 and scanlog review records as supporting history.

## Preservation and integration

The dedicated project branch/worktree remains uncommitted for review; no commit, push, or primary-checkout integration was performed. The primary checkout had pre-existing changes (`.gitignore`, `HANDOFF.md`, and untracked `tests/research/session-5400-review.json`); its tracked diff still matches the captured pre-work patch byte-for-byte and the untracked artifact hash is unchanged. Baseline comparison confirmed the 1,011 old command objects are unchanged except for the eight intended `dbg: true` settings, and all 57 old staging groups and top-level metadata are unchanged. The testing-headroom review worktree and migrated historical handoff remain untouched. Root archive artifacts are retained in place and linked rather than copied into a second editable project.
