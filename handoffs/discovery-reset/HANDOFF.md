# Project: BMW discovery-group reset

- Project ID: BMW-4-series/discovery-reset
- Owner/session: Codex /root; read-only discovery_advice and reset_review specialists
- Repository: M2ABRAMSTANK/BMW-4-series; publication target origin/main
- Branch: project/discovery-reset
- Worktree: /Users/rowdyer/Coding/OBDb/repos/BMW-4-series--discovery-reset
- Base: 26c737b86ea72c5a6abeb18f351b42edbfd9985a
- Updated: November 14, 2026 America/Denver
- Status: stage 1 published and verified as 47befec; stage 2 TG0–TG51 broad discovery approved by the owner for publication to fork main

## Scope and preservation

Clear the former testing-group pickers, their per-group reference aliases and TG folder labels. Keep command identities, decoding formats, model-year filters, polling settings, raw candidate views and all source/evidence records. The prior staging manifest is retained as tests/research/staging-groups-before-reset.json so historical TG labels and source hypotheses retain their meaning. Active staging-groups.json was empty in the published reset and now contains the approved discovery pass.

The separate pid-scaling worktree contains 96 locally accepted research identities and eight established corrections; those uncommitted decoders are not silently included in this immediate reset publication. Its evidence/decisions inform stage 2 planning. No primary checkout or other session worktree is edited.

## Next

The owner approved committing and pushing stage 2 to the fork. Publish after final checks and verify the remote commit; record its SHA in the root coordination handoff. Discovery only in this pass; targeted interpretation experiments are a later regrouping.

## Stage 1 validation

- All 1,102 command objects preserve addressing, filters, polling and non-UI fields. Every non-alias signal preserves its format and all fields except the intended old-TG name/path removal.
- Active pickers: 0; removed group reference aliases: 719. Original manifest/source hypotheses are retained byte-for-byte.
- Vehicle suite: 1,828 passed, two empty-group parametrizations skipped, one known padding xfail, and two pre-existing PID0144 fixture failures for2024/2026. Both failures reproduce against the unchanged research-integration baseline using the same schema dependency. No unrelated decoder/fixture fix is included in this reset.
- git diff --check passed. No raw scanlog exports, VINs or database files are included.

## Current result and next action

Stage 1 was pushed non-force to `M2ABRAMSTANK/BMW-4-series` main and verified at `47befec76239e3fb19b3e80414a3fb4875690544`. Stage 2 has explicit owner approval to commit and push. [REVIEW.md](REVIEW.md) records the approved scope and validation; Git history and the root coordination handoff identify the publication commit. No phone reload or focus-state change is claimed.

The owner's correction supersedes the earlier six-group/first-response-only proposal. Discovery means resolving PID meanings. The new pass has **52 groups TG0–TG51 covering all 318 ordinary unresolved candidates**: 295 captured plus 23 uncaptured. 96 accepted identities and 3 session-dependent EGS requests remain outside the candidate set. All 417research records and 583 prior exclusions are preserved. Family assignment is source-informed, not a new semantic acceptance. No targeted pairwise experiment groups are included.

Existing source hypotheses remain in the byte-identical historical manifest; external-research.json preserves 529 profiles / 1,355 fields. Discovery records point to those sources rather than silently making their formulas active. Current remaining questions are separate from archived old-group instructions.

New canonical collection: 11 closed sessions, 73,617 commands, 1 new session / 18,303 commands, 10 overlaps; complete through 2026-11-15T02:14:00Z. The full pages validate against an explicitly documented top-1000 summary-bin exporter limit (all reported counts and omitted-rank bounds checked), distinct from raw pagination. The importer now has 13 regression cases for that limitation. PID Detector overlap added 0 rows. Validated transport staging removed 302 files / 27,657,185 bytes; only small receipts remain. No backup database was created.

Fresh F150 witness: native 35C196DD-1648-43D6-84CD-A8FF787D1260, command 6296, matching 6F1/12→612 reply, 3 payload bytes. It remains active in broad semantic discovery (TG51); a new positive does not resolve its unknown meaning.

Stage 2 validation: 1895 passed, 1 existing xfail, 2 same 2024/2026 PID0144 baseline fixture failures. Independent review checks exact 318 coverage including 295 captured, no accepted/held inclusion, published-only reference formats, deterministic planner/builder and unchanged non-UI definition contract. New tests ensure a positive response cannot exclude an unresolved candidate or unhold a session-dependent request.

Shared/root dependencies: `handoffs/discovery-reset/build_catalog.py` reconciles prior pid-scaling decisions with the completed canonical increment; `handoffs/pelican-cli-access/unified_import.py` now verifies the exact histogram-cap diagnostic; `handoffs/discovery-reset/test_counter_cap.py` covers it. The prior pid-scaling worktree remains unchanged and contains unpublished decoder corrections. Do not blindly rerun its old group-aware apply_decisions.py over this rebuilt layout; adapt integration deliberately.

Publication: owner authorized the 52-group broad-discovery commit and non-force push. Fork main was verified at reset 47befec before publication. Preserve this worktree and the original primary/integration/scaling checkouts. Next operational step is loading the updated definitions in Pelican and selecting TG0; no phone reload is verified here.

Source mapping: tests/research/discovery-families.json records 15 reviewed broad families and reasons for all 318 assignments. plan_discovery_groups.py makes route-coherent chunks of at most 8 and build_discovery_groups.py generates display groups. Current source/response metadata remains separate from semantic resolution. The root helper build_catalog.py now explicitly prioritizes accepted/session-held state before support when writing eligibility and actions.
