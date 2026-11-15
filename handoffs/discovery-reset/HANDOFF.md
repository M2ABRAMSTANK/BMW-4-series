# Project: BMW discovery-group reset

- Project ID: BMW-4-series/discovery-reset
- Owner/session: Codex /root; read-only discovery_advice and reset_review specialists
- Repository: M2ABRAMSTANK/BMW-4-series; publication target origin/main
- Branch: project/discovery-reset
- Worktree: /Users/rowdyer/Coding/OBDb/repos/BMW-4-series--discovery-reset
- Base: 26c737b86ea72c5a6abeb18f351b42edbfd9985a
- Updated: November 14, 2026 America/Denver
- Status: stage 1 clearing groups for immediate authorized publication; stage 2 discovery-only TG0 onward remains local until owner review

## Scope and preservation

Clear the former testing-group pickers, their per-group reference aliases and TG folder labels. Keep command identities, decoding formats, model-year filters, polling settings, raw candidate views and all source/evidence records. The prior staging manifest is retained as tests/research/staging-groups-before-reset.json so historical TG labels and source hypotheses retain their meaning. Active staging-groups.json is empty for the published reset.

The separate pid-scaling worktree contains 96 locally accepted research identities and eight established corrections; those uncommitted decoders are not silently included in this immediate reset publication. Its evidence/decisions inform stage 2 planning. No primary checkout or other session worktree is edited.

## Next

Validate and push the stage 1 reset to the verified fork main. Build fresh discovery groups from TG0 using existing support, source hypotheses, accepted/excluded decisions and incremental evidence. Do not publish stage 2 until the owner agrees. Discovery only in this pass; targeted interpretation experiments are a later regrouping.

## Stage 1 validation

- All 1,102 command objects preserve addressing, filters, polling and non-UI fields. Every non-alias signal preserves its format and all fields except the intended old-TG name/path removal.
- Active pickers: 0; removed group reference aliases: 719. Original manifest/source hypotheses are retained byte-for-byte.
- Vehicle suite: 1,828 passed, two empty-group parametrizations skipped, one known padding xfail, and two pre-existing PID0144 fixture failures for2024/2026. Both failures reproduce against the unchanged research-integration baseline using the same schema dependency. No unrelated decoder/fixture fix is included in this reset.
- git diff --check passed. No raw scanlog exports, VINs or database files are included.
