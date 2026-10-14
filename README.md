# BMW 4 Series

This repository contains signal set configurations for the BMW 4 Series, organized by model year and version. The files are structured to allow for easy differentiation between model generations and other vehicle parameters, ensuring accurate signal mapping for each version of the BMW 4 Series.

The [BMW PID research handoff](handoffs/bmw-pid-research/HANDOFF.md) records the
current evidence and local worktree. The shared scanning budget is approximately
**700 requests/minute**, including candidate, reference, and other app reads.

## Manual testing groups

All **67 testing groups / 417 candidate requests** are available together for
manual selection on the 2019 car. In the signal picker, look under
**Battery → TG0_1**, TG0_2, etc. Signal names retain the
original `[TG0.1]` notation on individual research signals. Each TG entry is one
complete native group directly under Battery, containing its research
signals and relevant reference readings together. Each research signal also has
an explicit `Battery.TG…` path so the app files it in its TG folder on the
parameters page. The Testing level is omitted to work around the app bug.
Select the TG entry once to include RPM, speed, engine load, fuel rate, fuel
level, coolant/oil temperature, control-module voltage, and any group-specific
references alongside the candidates. References can belong to multiple groups
without creating duplicate signal or command definitions.

The 64 existing TG0–TG16 groups retain their candidate membership. TG17.1/17.2
add the nine existing experimental readings; TG18.1 adds the two bitmap-advertised
but uncaptured service 01 reads, 0141 and 0183. All `dbg` and `dbgfilter` fields
are removed. Existing raw-byte views stay raw: availability does not certify a
proposed interpretation. The 583 commands previously rejected by the car remain
excluded for 2019 and are filed under Battery → Testing → Unavailable on 2019
for research on other years. Known ordinary signals retain their normal paths;
reference membership makes them available when adding testing groups.

Count **unique requests**, not signals or raw bytes. One request returning 210
byte views still consumes one request in this model. At the assumed shared
throughput, each selected request receives `700 / N / 60` updates/second, where
`N` includes all selected groups, reference reads, and any additional app reads.
An overlapping request counts once. Individual groups including references
contain 9–19 requests (approximately 1.30–0.61 Hz each). TG0.1 contains 18 requests:
8 candidates and 10 references, approximately **0.648 Hz / 1.543 seconds each**.
Extra dashboard or background reads increase N and lower every request's share.
Long replies, route changes, setup, retries, and diagnostic-session keepalives
can reduce actual throughput; these figures are estimates, not measured cadence.

There is no planned tier schedule. The schema requires a positive `freq`, so
all definitions use `0.01` seconds as a ready-to-poll minimum. It is not a
100-Hz target and does not enforce the 700/minute budget. The app must poll only
the manually selected reads and share its available throughput. Making a group
visible does not itself select it. App picker behavior and actual throughput
still need an on-car check.

Use the read-only helper from the workspace root:

```sh
python3 repos/BMW-4-series--research-integration/scripts/staging.py
python3 repos/BMW-4-series--research-integration/scripts/staging.py TG0.1 TG16.1
python3 repos/BMW-4-series--research-integration/scripts/staging.py TG0.1 --extra '7DF||010B' --background-count 3
bash scripts/test-repo.sh BMW-4-series--research-integration
```

`--extra` names additional requests and deduplicates them against the selected
groups. `--background-count` accounts for further distinct reads not already
named. The helper cannot inspect the app's selection. It no longer rewrites year
filters or rotates one active group. The [manifest](tests/research/staging-groups.json)
records full group membership, references, and estimates. Historical candidate
intervals and source tier labels remain there as provenance only.

### New scanlog results: sessions 5421–5444

The [bounded review](tests/research/sessions-5421-5444-review.json) covers all
18 sessions in that range with the established car's VIN, containing 59,264
service 01/22 requests. Six VIN-less empty sessions are excluded. Adapter route
changes were reconstructed chronologically, and single-frame padding was
trimmed to the declared PDU length before interpreting payloads.

| TG0.1 DID | Proposed interpretation (unverified) | Positive replies | Distinct payloads |
| --- | --- | ---: | ---: |
| 4204 | Ambient temperature | 132 | 13 |
| 4310 | Coolant target | 132 | 3 |
| 4402 | Oil temperature after filter | 132 | 32 |
| 4409 | Oil level | 132 | 3 |
| 4421 | Oil-pressure control P component | 161 | 134 |
| 4422 | Oil-pressure control I component | 161 | 157 |
| 4423 | Oil-pressure control D component | 161 | 94 |
| 4425 | Sump oil temperature | 132 | 60 |

These eight requests all returned two-byte payloads and no negative replies on
the configured route in this review. Eight new real-response fixtures preserve
the raw byte extraction. This confirms response support on this car and provides
changing values for research; it does not validate the proposed physical scales.
No decoder promotion is made, including 4402.

**None of the 26 newest external discovery requests was sent on its configured
route in these sessions.** Their model support remains untested, not rejected.
Likewise, there are no newly captured 7DF/7E8 0141 or 0183 reads in this range.
TG10–TG16 and TG18.1 are now visible for collecting that missing evidence.

Session-wide service 01/22 throughput varies substantially: approximately
812/minute in 5441, 303/minute in 5442, and 477/minute in 5444, including startup.
The 700/minute assumption is the user's planning budget, not a guaranteed rate
established by these recordings.

### 2019 service 01 coverage

The target car's 7E8 support bitmaps advertise 47 data PIDs; 45 have captured
positive replies. The 7E9 bitmaps advertise nine data PIDs, all with positive
replies. The signal set defines these through observed functional 7DF/7E8 and
physical 7E1/7E9 routes, plus nine support-page reads. The 63 earlier fixtures and
[source provenance](tests/research/service01-2019-provenance.json) retain the
support distinction. TG18.1 exposes bitmap-advertised 7E8 0141 and 0183 for
manual discovery; no positive payload has been claimed.

## Scanlog validation

The October 2026 audit covers all 1,011 configured commands, including every
inactive TG0–TG8 testing wave, using 3,248 sessions identified as the same 2019
BMW. There are positive replies for 428 commands; the remaining 583 returned
UDS request-out-of-range responses on this vehicle. All 392 TG0–TG8 commands
answered, but many still have unverified meanings or scaling.

That audit is the pre-integration baseline. The research integration had 1,037
command objects and 1,676 signal objects; the service 01 coverage brings the
configuration to 1,102 commands and 1,855 signals. The research integration
added 26 read requests and 339 raw research signals; these byte views are not
339 physical sensors. D12F alone
accounts for 210 byte views for a long-response trip-history hypothesis, whose
target framing and layout remain unverified.

[The complete audit](tests/research/scanlog-audit.json) records every command's
status, original definition concerns, response counts, and a lossless capture
with session, record, timestamp, and adapter routing. The offline transport
tests preserve this evidence without treating a positive reply as proof of a
physical conversion. [Decoding evidence](tests/research/decoding-evidence.json)
contains paired measurements and provenance for newly added numeric fixtures.

Thirty-four commands are now regular for **2019**: 18 reviewed DME commands,
ten corroborated engine/temperature/voltage candidates, four TPMS commands,
transmission temperature DA12, and the DA37 Drive counter. This includes the
five previously disabled duplicate measurements. Availability filters are
preserved. Debug gating has since been removed by the manual testing policy above. Unknown TPMS raw fields
and the unconfirmed DA37 Sport/Manual fields remain hidden research signals.

The earlier graduation review was a project judgment, not independent
calibration of every sensor. Source definitions, observed ranges, paired
measurements where available, and regression fixtures support that review.
The audit's `graduation` section lists all commands and remaining limitations.

Five existing regular commands retain their prior availability filters.
Nine available commands retain experimental decoding: 442C, 4683, 4A2E, 558E,
558F, 582F, 586F, DA25, and DA2E. The original 380 responding candidates are organized into staged research waves
pending decoding evidence. Oil-pressure 586F remains raw; DA25 has an
unexplained low-temperature outlier; DA2E has an unidentified state code.
Supported-year transmission filters follow existing response fixtures, whose
other-year conversions remain experimental.

### Unavailable and invalid readings

[The invalid-value catalog](tests/research/invalid-values/index.json) records every
configured null bound, its confidence, and links to lossless scanlog evidence.
OBDb's `fmt.nullmin` and `fmt.nullmax` are **inclusive bounds on decoded values**,
not exact raw-code lists. Preserve the raw response and return a missing value;
do not replace an unavailable reading with numeric zero.

| Signal | Observed marker | Handling and evidence |
| --- | --- | --- |
| TPMS pressure / temperature, DC98–DC9B | LE pressure bytes `9C18` = 6.300 bar (about 91.37 psi), paired with `7F` = 127 C | Existing upper null bounds retained. 37 unavailable pairs among 127 positive responses in 11 recent sessions. Target pressures remain numeric. |
| Lambda 2, 582C | `0000` | Added `nullmin: 0`; unsigned scaling makes this exactly raw zero. Five readings in four sessions, initially paired with catalyst marker `08B7`; two sessions subsequently recover near lambda 1. |
| Candidate catalyst temperature, 582F | `08B7` = -50.05 C | Already covered by `nullmin: -50`. Startup correlation supports an unavailable marker; physical identity and calibration remain provisional. |
| Lambda upper range, 582C / 5889 | Existing threshold 15.99, raw `FFD8`–`FFFF` | Inherited rule retained but not independently confirmed by this review. Do not broaden it: high lambda may be lean/saturated rather than unavailable. Observed `FF00` remains numeric. |

The TPMS review includes both unavailable-to-ordinary and ordinary-to-unavailable
transitions. The logs support missing readings, not a specific warming, RF, or
ECU-initialization cause. The DME review covers 90 bounded VIN-matched sessions;
transmission evidence includes older startup sequences. These are scoped reviews,
not proof that every unavailable code in the export has been identified.

UDS negative responses, `NO DATA`, malformed replies, and ISO-TP padding are
separate from numeric sentinels. Zero speed is valid; DA25 raw `30` and DA2E state
`0A` remain unresolved and are not nulled. Unknown research bytes retain their
full range. Add a new null bound only with supported interpretation and captured
regression cases, including valid neighboring or recovered readings.

### Raw research views

The 406 original staged requests expose 1,023 raw research signals, including
339 byte views from 26 external discovery reads. D12F alone contributes 210 raw
views for a long-response trip-history hypothesis. These are byte views, not
independently identified sensors. Candidate formulas and labels remain in the
[manifest](tests/research/staging-groups.json), outside live signal definitions
because the tooling rejects overlapping raw/decoded fields. Raw-byte regression
tests continue to cover the original 380 recorded candidates.

### Building stronger decoding evidence

More sessions are useful when they add **different conditions and independent
references**. A positive reply proves that a request is supported, not that its
label, byte offset, signedness, scale, or unavailable-value handling is correct.
Repeated constant values cannot distinguish competing conversions.

- Record candidate and trusted reference PIDs close together through cold start,
  warm-up, idle, and normal driving. Compare several temperatures, engine speeds,
  and voltages, not just one plausible value. For example, 4807 raw 1417 / 2
  gives 708.5 rpm alongside a recorded SAE reference of 705 rpm.
- For pressure or oil level, obtain a documented conversion for the matching ECU
  or paired readings from a trusted diagnostic tool. Raw data alone may never
  identify physical units uniquely.
- For DA37, record known durations in Drive, Sport, and Manual to establish which
  counters advance. For DA2E, record known selector states to identify code 0A.
- For DA25 and 582F, capture the suspicious values alongside a trusted temperature
  and operating state to distinguish real readings from unavailable sentinels.
- Retain model year, engine/ECU version, timestamps, routing, raw responses, and
  reference provenance. Evidence from this 2019 vehicle does not verify another
  ECU or year. Add numeric and sentinel fixtures once the interpretation is known.

Tests establish reproducible decoding; they cannot establish a physical meaning
when expected values were derived only from the same unverified formula.

The 583 rejected commands retain `filter: {"to": 2018, "from": 2020}`.
Removing debug metadata does not enable them on 2019. The external collection
service and live app loading are not exercised by the offline tests.

Tests do not require access to the private scanlog database.

## Contributing

Contributions are welcome! If you would like to add support for additional model years or other configurations, please open an issue or submit a pull request.

1. Fork the repository
2. Create a new branch for your changes
3. Commit your changes and open a pull request with a detailed description

## Issues

If you encounter any issues or would like to discuss improvements, please feel free to open an issue. We encourage collaboration and appreciate feedback to make the repository as accurate and useful as possible.
