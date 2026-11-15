# Broad PID discovery — approved grouping

The prior six-group draft was too narrow: it treated discovery as finding a first positive response. The owner clarified that this pass must cover **unresolved meanings**, using existing responses and imported knowledge. This draft replaces that proposal.

Stage 1 remains published as [47befec](https://github.com/M2ABRAMSTANK/BMW-4-series/commit/47befec76239e3fb19b3e80414a3fb4875690544). The owner approved committing and pushing stage 2 to the fork’s main branch. The publication commit is recorded in Git history and the workspace coordination handoff. No phone loading or focus change has occurred.

## Coverage

- **318 ordinary unresolved candidates**, exactly once across **52 groups, TG0–TG51**.
- These include **295 with captured replies and 23 without**. A positive response does not establish what its fields mean, their conversion, validity or operating-state behavior.
- **96 accepted research identities** remain outside the candidate set. Their prior local decoder improvements remain separate and unpublished.
- **Three session-dependent EGS requests** (224131,22413A,224140 on 6F1/18→618) remain explicit acquisition holds. They are not resolved or unsupported. Their sources call for diagnostic-session entry and tester-present; no new session behavior is introduced.
- All 417research identities remain accounted for. The 583 existing 2019 exclusions are preserved separately.

Existing captures are inputs to interpretation and reduce unnecessary repetition. They do not remove a still-unresolved candidate from this pass. New captures are useful when they add broad operating conditions or expose contradictions; there is no requirement to drive every group again before using the data already available.

## How the groups were rebuilt

A dedicated specialist classified every eligible candidate using preserved source names, formulas/context and external module/profile metadata. The map uses 15 broad families, not the retired TG numbers. Family names are **source-informed hypotheses**, not newly verified meanings. Vague labels remain in an explicit residual family rather than receiving invented units.

Each family is split into ECU-route-coherent batches of at most 8 candidates. Every group includes existing published RPM, vehicle speed and voltage context, plus at most one broad load or coolant channel. There are 188 same-request display aliases; these do not create 188 extra command identities. Groups contain 4–12 unique requests including context. Actual sampling rates remain unmeasured; polling metadata is unchanged.

These are broad discovery groups, not the later targeted pairwise experiments. The large D12F trip-history reply remains isolated in TG48 because its source expects at least 210 measurement bytes. This keeps its multi-frame traffic separate from batches of short replies.

| Groups | Broad source family | Candidates |
| --- | --- | ---: |
| TG0–TG2 | Air path, pressure and flow hypotheses | 24 |
| TG3–TG6 | Pedal and throttle sensor/control hypotheses | 26 |
| TG7–TG12 | Camshaft and variable-valve-system hypotheses | 44 |
| TG13–TG18 | Fuel, lambda, EVAP and exhaust-system hypotheses | 42 |
| TG19–TG23 | Ignition, knock, roughness and misfire hypotheses | 36 |
| TG24–TG27 | Temperature, cooling and thermal-history hypotheses | 25 |
| TG28 | Oil-level, oil-quality and oil-pressure hypotheses | 5 |
| TG29–TG31 | Engine torque, idle and engine-state hypotheses | 22 |
| TG32–TG35 | Battery, charging, electrical supply and energy hypotheses | 28 |
| TG36–TG38 | Transmission, clutch and gear-state hypotheses | 17 |
| TG39–TG43 | Vehicle motion, steering, cluster and trip hypotheses | 19 |
| TG44–TG47 | Body, closures and HVAC hypotheses | 12 |
| TG48 | Isolated large-response trip-history hypothesis | 1 |
| TG49 | Standard OBD advertised response/meaning discovery | 1 |
| TG50–TG51 | Unclear status, calibration and residual source hypotheses | 16 |

## What constitutes progress

For each candidate, combine retained source definitions with existing/new payloads and broad operating context to reach one of:

- A useful qualified interpretation/layout/conversion that can be implemented and tested.
- An evidence-supported applicability/unsupported decision, with routing and relevant conditions checked.
- A precise remaining question for the later targeted pass, stating why it changes the decision.

Capturing a positive packet alone does **not** complete semantic discovery. For example, 22F150 now has a matching three-byte reply but its meaning is unknown, so it remains an active candidate in TG51. The native witness is session 35C196DD-1648-43D6-84CD-A8FF787D1260, command 6296. Current support and payload lengths are separate from historical source assertions in the catalog and group manifest.

Use normal operating conditions; no special maneuvers or agent actuation. Source hypotheses may be wrong, copied from the same ancestor or variant-specific. Keep those qualifications when interpreting correlations or deciding whether a broader name is useful. Exact sensor naming is not a universal graduation gate.

## Preserved knowledge and reproducibility

- `staging-groups-before-reset.json`: all 417original candidate records and 380 decoding hypotheses, byte-identical to the pre-reset manifest.
- `external-research.json`: 529 source profiles / 1,355 field rows, including 26 complete acquisition records with routes, layouts, encodings, scale/offset/units, conditions/enumerations where available, source revisions and uncertainties.
- `discovery-catalog.json`: current acceptance, support, semantic question, inclusion, evidence references and historical questions kept separately.
- `discovery-families.json`: explicit per-candidate source labels, family assignments and reasons. Membership does not imply semantic acceptance.
- Existing audit, native captures and fixtures remain available. EV/HV-specific source opportunities are not automatically imported as applicable 430i PIDs.

From the vehicle worktree:

```sh
../../.venv/bin/python -B scripts/plan_discovery_groups.py --check
../../.venv/bin/python -B scripts/build_discovery_groups.py --check
```

Omit `--check` to regenerate after reviewing a mapping/plan change. The planner requires all eligible candidates to be mapped; the builder independently excludes accepted/session-dependent requests and rejects any omitted or duplicate unresolved request. Tests explicitly cover dropping a supported PID, accidentally adding accepted/held requests, and new positives not changing discovery eligibility.

The published-reset contract checks preservation of all 1,102 requests and retained signal fields except permitted display/group organization. No decoder, routing, year-filter, validity or frequency change is included.

Validation: **1,895 passed, one existing padding xfail, two pre-existing 0144 fixture failures (2024/2026)**. Those same failures reproduce in the published baseline. Planner/builder determinism, full 318 coverage, exact folder/regex matching, published reference formats and reset preservation pass. These results cover the owner-approved stage 2 grouping.

## Complete group index

Request keys are `transmit header|extended address|service+PID`; matching responders are retained in the manifest. Captured/uncaptured columns describe evidence availability, not resolved/unresolved meanings: **every listed candidate is unresolved**.

| Group | Candidates | Captured | Uncaptured | Requests incl. context | Candidate request identities |
| --- | ---: | ---: | ---: | ---: | --- |
| TG0 | 8 | 8 | 0 | 12 | `6F1|12|224202`, `6F1|12|224203`, `6F1|12|224610`, `6F1|12|224ACC`, `6F1|12|224ACD`, `6F1|12|224ACE`, `6F1|12|224ACF`, `6F1|12|224AD2` |
| TG1 | 8 | 8 | 0 | 12 | `6F1|12|224AD3`, `6F1|12|2257A1`, `6F1|12|2257AD`, `6F1|12|2257D2`, `6F1|12|225804`, `6F1|12|22580B`, `6F1|12|225810`, `6F1|12|225812` |
| TG2 | 8 | 8 | 0 | 12 | `6F1|12|225818`, `6F1|12|225899`, `6F1|12|2258D2`, `6F1|12|2258D3`, `6F1|12|2258F3`, `6F1|12|225956`, `6F1|12|225A0B`, `6F1|12|225A0C` |
| TG3 | 8 | 7 | 1 | 12 | `6F1|12|22DE9C`, `6F1|12|224206`, `6F1|12|224600`, `6F1|12|224601`, `6F1|12|22480B`, `6F1|12|22573C`, `6F1|12|225814`, `6F1|12|225826` |
| TG4 | 8 | 8 | 0 | 12 | `6F1|12|225839`, `6F1|12|22583F`, `6F1|12|225840`, `6F1|12|225843`, `6F1|12|225846`, `6F1|12|225847`, `6F1|12|225858`, `6F1|12|2258AD` |
| TG5 | 8 | 8 | 0 | 12 | `6F1|12|2258B0`, `6F1|12|2258B9`, `6F1|12|2258D8`, `6F1|12|2258D9`, `6F1|12|225A00`, `6F1|12|225A01`, `6F1|12|225A04`, `6F1|12|225A05` |
| TG6 | 2 | 2 | 0 | 6 | `6F1|12|225A06`, `6F1|12|225A07` |
| TG7 | 8 | 8 | 0 | 12 | `6F1|12|224500`, `6F1|12|224501`, `6F1|12|224502`, `6F1|12|224503`, `6F1|12|224506`, `6F1|12|224507`, `6F1|12|224508`, `6F1|12|224509` |
| TG8 | 8 | 8 | 0 | 12 | `6F1|12|22450E`, `6F1|12|224510`, `6F1|12|224511`, `6F1|12|224512`, `6F1|12|224513`, `6F1|12|224514`, `6F1|12|224515`, `6F1|12|224516` |
| TG9 | 8 | 8 | 0 | 12 | `6F1|12|224517`, `6F1|12|224518`, `6F1|12|224519`, `6F1|12|22451A`, `6F1|12|22451B`, `6F1|12|22451C`, `6F1|12|224526`, `6F1|12|224527` |
| TG10 | 8 | 8 | 0 | 12 | `6F1|12|224603`, `6F1|12|2257C3`, `6F1|12|225877`, `6F1|12|22587B`, `6F1|12|22589E`, `6F1|12|2258A2`, `6F1|12|2258A3`, `6F1|12|2258A6` |
| TG11 | 8 | 8 | 0 | 12 | `6F1|12|2258A8`, `6F1|12|2258AA`, `6F1|12|2258BB`, `6F1|12|2258BD`, `6F1|12|2258C0`, `6F1|12|2258CB`, `6F1|12|2258CC`, `6F1|12|2258F6` |
| TG12 | 4 | 4 | 0 | 8 | `6F1|12|2259BD`, `6F1|12|2259BE`, `6F1|12|225A02`, `6F1|12|225A03` |
| TG13 | 8 | 8 | 0 | 12 | `6F1|12|224700`, `6F1|12|224704`, `6F1|12|224705`, `6F1|12|224712`, `6F1|12|224804`, `6F1|12|2248D0`, `6F1|12|224A6C`, `6F1|12|224AD5` |
| TG14 | 8 | 8 | 0 | 12 | `6F1|12|225773`, `6F1|12|225784`, `6F1|12|22579B`, `6F1|12|2257A9`, `6F1|12|2257C9`, `6F1|12|225802`, `6F1|12|225803`, `6F1|12|225806` |
| TG15 | 8 | 8 | 0 | 12 | `6F1|12|225816`, `6F1|12|22582F`, `6F1|12|225830`, `6F1|12|225845`, `6F1|12|225849`, `6F1|12|22584D`, `6F1|12|225871`, `6F1|12|225878` |
| TG16 | 8 | 8 | 0 | 12 | `6F1|12|22588C`, `6F1|12|225894`, `6F1|12|225895`, `6F1|12|225896`, `6F1|12|22589B`, `6F1|12|22589C`, `6F1|12|2258C5`, `6F1|12|2258FA` |
| TG17 | 8 | 8 | 0 | 12 | `6F1|12|2258FB`, `6F1|12|225949`, `6F1|12|22594A`, `6F1|12|22594C`, `6F1|12|225A0D`, `6F1|12|225A11`, `6F1|12|225A12`, `6F1|12|225A13` |
| TG18 | 2 | 2 | 0 | 6 | `6F1|12|225A14`, `6F1|12|225A17` |
| TG19 | 8 | 8 | 0 | 12 | `6F1|12|224880`, `6F1|12|224881`, `6F1|12|224A00`, `6F1|12|224A01`, `6F1|12|224A30`, `6F1|12|224A31`, `6F1|12|224A32`, `6F1|12|224A33` |
| TG20 | 8 | 8 | 0 | 12 | `6F1|12|224A37`, `6F1|12|224A38`, `6F1|12|224A39`, `6F1|12|224A3A`, `6F1|12|2257A0`, `6F1|12|22580E`, `6F1|12|225838`, `6F1|12|225883` |
| TG21 | 8 | 8 | 0 | 12 | `6F1|12|225884`, `6F1|12|225885`, `6F1|12|225886`, `6F1|12|225888`, `6F1|12|2258B1`, `6F1|12|2258B2`, `6F1|12|2258B3`, `6F1|12|2258B4` |
| TG22 | 8 | 8 | 0 | 12 | `6F1|12|2258B5`, `6F1|12|2258B6`, `6F1|12|2258DC`, `6F1|12|2258E5`, `6F1|12|2258E6`, `6F1|12|2258E7`, `6F1|12|2258E8`, `6F1|12|2258F8` |
| TG23 | 4 | 4 | 0 | 8 | `6F1|12|2258F9`, `6F1|12|22590F`, `6F1|12|22592D`, `6F1|12|2259FD` |
| TG24 | 8 | 8 | 0 | 12 | `6F1|12|224AEC`, `6F1|12|224AED`, `6F1|12|224AEE`, `6F1|12|224AF6`, `6F1|12|224AF7`, `6F1|12|224AF8`, `6F1|12|22580A`, `6F1|12|22581F` |
| TG25 | 8 | 8 | 0 | 12 | `6F1|12|225824`, `6F1|12|225833`, `6F1|12|225850`, `6F1|12|225851`, `6F1|12|22587E`, `6F1|12|22587F`, `6F1|12|225882`, `6F1|12|225890` |
| TG26 | 8 | 8 | 0 | 12 | `6F1|12|2258D1`, `6F1|12|2258D5`, `6F1|12|2258EE`, `6F1|12|2259D4`, `6F1|12|225A08`, `6F1|12|225A09`, `6F1|12|225A0A`, `6F1|12|225A0E` |
| TG27 | 1 | 1 | 0 | 5 | `6F1|18|22DA25` |
| TG28 | 5 | 5 | 0 | 9 | `6F1|12|224409`, `6F1|12|22440A`, `6F1|12|22442C`, `6F1|12|225811`, `6F1|12|22586F` |
| TG29 | 8 | 8 | 0 | 12 | `6F1|12|224520`, `6F1|12|224808`, `6F1|12|224809`, `6F1|12|225800`, `6F1|12|22580C`, `6F1|12|225819`, `6F1|12|225823`, `6F1|12|225832` |
| TG30 | 8 | 8 | 0 | 12 | `6F1|12|225836`, `6F1|12|22583D`, `6F1|12|22583E`, `6F1|12|225875`, `6F1|12|22588B`, `6F1|12|2258A7`, `6F1|12|2258BF`, `6F1|12|2258C1` |
| TG31 | 6 | 6 | 0 | 10 | `6F1|12|2258C7`, `6F1|12|2258C8`, `6F1|12|2258C9`, `6F1|12|2258CA`, `6F1|12|2258DA`, `6F1|12|22592E` |
| TG32 | 8 | 7 | 1 | 11 | `6F1|12|22402B`, `6F1|12|224602`, `6F1|12|224606`, `6F1|12|224607`, `6F1|12|22460C`, `6F1|12|22460E`, `6F1|12|224612`, `6F1|12|224617` |
| TG33 | 8 | 8 | 0 | 11 | `6F1|12|22575F`, `6F1|12|2257B5`, `6F1|12|225835`, `6F1|12|22583C`, `6F1|12|22584A`, `6F1|12|225852`, `6F1|12|225857`, `6F1|12|225868` |
| TG34 | 8 | 8 | 0 | 11 | `6F1|12|225869`, `6F1|12|22586B`, `6F1|12|22586C`, `6F1|12|22586E`, `6F1|12|2258A0`, `6F1|12|225916`, `6F1|12|225917`, `6F1|12|225918` |
| TG35 | 4 | 4 | 0 | 7 | `6F1|12|22597F`, `6F1|12|225981`, `6F1|12|225A0F`, `6F1|12|225A10` |
| TG36 | 8 | 8 | 0 | 11 | `6F1|12|224683`, `6F1|12|224800`, `6F1|12|224801`, `6F1|12|225717`, `6F1|12|22582B`, `6F1|12|22587D`, `6F1|12|225881`, `6F1|12|225891` |
| TG37 | 8 | 8 | 0 | 11 | `6F1|12|22589A`, `6F1|12|2258D4`, `6F1|12|2258D6`, `6F1|12|22593B`, `6F1|12|225940`, `6F1|12|225941`, `6F1|12|225942`, `6F1|12|2259D1` |
| TG38 | 1 | 1 | 0 | 4 | `6F1|18|22DA2E` |
| TG39 | 1 | 0 | 1 | 4 | `6F1|30|22DB99` |
| TG40 | 6 | 0 | 6 | 9 | `6F1|60|22420C`, `6F1|60|22D111`, `6F1|60|22D112`, `6F1|60|22D114`, `6F1|60|22D129`, `6F1|60|22D12A` |
| TG41 | 2 | 0 | 2 | 5 | `6F1|63|22D030`, `6F1|63|22D031` |
| TG42 | 8 | 8 | 0 | 11 | `6F1|12|22480A`, `6F1|12|22480D`, `6F1|12|224810`, `6F1|12|224811`, `6F1|12|224812`, `6F1|12|224A1D`, `6F1|12|22580D`, `6F1|12|225892` |
| TG43 | 2 | 2 | 0 | 5 | `6F1|12|2258B7`, `6F1|12|2259EB` |
| TG44 | 2 | 0 | 2 | 5 | `6F1|40|22D130`, `6F1|40|22DAD6` |
| TG45 | 1 | 0 | 1 | 4 | `6F1|56|22DCDD` |
| TG46 | 7 | 0 | 7 | 10 | `6F1|78|22D85C`, `6F1|78|22D8C5`, `6F1|78|22D91A`, `6F1|78|22D92C`, `6F1|78|22D930`, `6F1|78|22D931`, `6F1|78|22D96B` |
| TG47 | 2 | 2 | 0 | 5 | `6F1|12|224802`, `6F1|12|224803` |
| TG48 | 1 | 0 | 1 | 4 | `6F1|60|22D12F` |
| TG49 | 1 | 0 | 1 | 4 | `7DF||0183` |
| TG50 | 8 | 8 | 0 | 11 | `6F1|12|224002`, `6F1|12|22440B`, `6F1|12|22440C`, `6F1|12|22460D`, `6F1|12|22584F`, `6F1|12|225855`, `6F1|12|225887`, `6F1|12|2258A9` |
| TG51 | 8 | 8 | 0 | 11 | `6F1|12|2258AB`, `6F1|12|2258CD`, `6F1|12|2258CE`, `6F1|12|2258DB`, `6F1|12|2258DF`, `6F1|12|2258E4`, `6F1|12|2258F5`, `6F1|12|22F150` |
