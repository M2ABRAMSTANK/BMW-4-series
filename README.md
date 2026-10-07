# BMW 4 Series

This repository contains signal set configurations for the BMW 4 Series, organized by model year and version. The files are structured to allow for easy differentiation between model generations and other vehicle parameters, ensuring accurate signal mapping for each version of the BMW 4 Series.

The [next-session handoff](HANDOFF.md) records the scanlog cutoff and the plan to
measure testing headroom. The testing allowance is **400 requests/minute**.

## Polling convention

Signal descriptions begin with `[Polling: <tier>]`. This is a local documentation
convention, not an OBDb schema extension. The supported command-level `freq`
field sets the requested interval in seconds; the prefix explains its purpose.

| Tier | Interval | Purpose | Example commands |
| --- | ---: | --- | --- |
| Operational | 0.25 s | Responsive driving measurements | RPM 4807, speed 4AB1, wheel speeds DBE4 |
| Engine control | 1 s | Engine response under changing load | Boost 4205/4AB0, fuel rail pressure 56D7, lambda 5889 |
| Short-term trends | 5 s | Electrical and intake trends | IBS voltage 5853, intake temperature 580F |
| Thermal condition | 15 s | Warm-up and sustained temperatures | Coolant 4300/5805, oil 4408/5822, transmission DA12 |
| Health and environment | 60 s | Periodic condition and environmental readings | TPMS DC98–DC9B, barometric pressure 4201 |
| Cumulative history | 300 s | Accumulated totals | Odometers D10D, Drive time DA37 |

All signals returned by one command share that command's interval and prefix,
including hidden fields. Classify by the measurement's use, not only its module.
These are ordinary-use defaults, not guarantees of achieved cadence or sensor
update rate. Existing duplicate sources retain the tier for their measurement;
selecting a preferred source can be a separate client/profile optimization.

Unverified commands and archived decoding hypotheses use
`[Polling: Unclassified; research override]`. This marks an exception, not a
seventh ordinary tier or an assertion that the candidate's identity is known.
Their existing research intervals, availability, and testing groups remain in
place. The **400 requests/minute testing budget** still includes the active wave
and other enabled experimental commands, and excludes regular polling. A regular
command's debug coverage on other years retains its ordinary tier interval;
this research budget is calculated for the observed 2019 vehicle.

When editing a polling tier, update both `freq` and every signal description in
that command. The tests check that tier labels match the configured interval.
No new signal-set fields are introduced.

## Scanlog validation

The October 2026 audit covers all 1,011 configured commands, including every
inactive TG0–TG8 testing wave, using 3,248 sessions identified as the same 2019
BMW. There are positive replies for 428 commands; the remaining 583 returned
UDS request-out-of-range responses on this vehicle. All 392 TG0–TG8 commands
answered, but many still have unverified meanings or scaling.

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
preserved; other allowed years remain in debug mode. Unknown TPMS raw fields
and the unconfirmed DA37 Sport/Manual fields remain hidden research signals.

This follows the live upstream [BMW 4 Series](https://github.com/OBDb/BMW-4-series/blob/main/signalsets/v3/default.json)
convention: omit unconditional `dbg`, and use `dbgfilter` for unverified years.
The [OBDb schema](https://github.com/OBDb/.schemas/blob/main/signals.json) supports
per-signal `hidden` fields. Upstream conventions were checked on October 7,
2026. The graduation gate is a project review judgment, not an OBDb certification
or independent calibration of every sensor. Source definitions, observed ranges,
paired measurements where available, and regression fixtures support this decision.
The audit's `graduation` section lists all commands and remaining limitations.

Five existing regular commands retain their prior year-specific status.
Nine available commands retain experimental decoding: 442C, 4683, 4A2E, 558E,
558F, 582F, 586F, DA25, and DA2E. Another 380 responding candidates are organized into staged research waves
pending decoding evidence. Oil-pressure 586F remains raw; DA25 has an
unexplained low-temperature outlier; DA2E has an unidentified state code.
Supported-year transmission filters follow existing response fixtures, whose
other-year conversions remain experimental.

### Staged research polling

The 380 unresolved positive-response commands are split into **57 waves of at
most eight commands**, preserving the old TG0–TG8 families; TG9 holds three
previously ungrouped candidates. **TG0.1 is active for 2019 in debug mode**.
All other waves use the existing disabled convention, `filter.years: [9999]`.
Graduated commands, nine existing experimental commands, and the 583 commands
rejected for 2019 keep their separate availability settings.

Requested polling intervals are 1 second for dynamic values, 2 seconds for
temperature/voltage/level candidates, and 10 seconds for slower counters and
adaptations. These are research scheduling choices, not evidence of a sensor's
update rate. Each wave fits a **400-request/minute testing-only budget**, excluding regular
polling and reserving approximately **24.02 requests/minute** for the nine
existing experimental commands. TG0.1 requests **330 polls/minute**, for
approximately **354.02 testing requests/minute** combined. The busiest wave
plus existing experimental polling totals approximately 396.02 requests/minute. Achieved cadence depends on
adapter throughput and other enabled commands and must be checked in the next
scanlog. Debug collection must be enabled in the client for the active wave.

TG0.1 contains 4204 (ambient temperature candidate), 4310 (coolant target),
4402 (oil temperature), 4409 (oil level), and 4425 (sump temperature) at
2-second intervals, plus 4421/4422/4423 (oil-pressure regulator components)
at 1-second intervals. These labels remain hypotheses. Remaining TG0 candidates continue in subsequent waves.
The visible research fields expose each returned byte without conversion or
clamping. Candidate formulas and labels are preserved in
[the staging manifest](tests/research/staging-groups.json), outside the live
signal definitions because the tooling rejects overlapping raw/decoded fields.
Raw-byte regression tests cover every wave, including parked waves.

From the workspace root, using the environment with OBDb schema tooling:

```sh
.venv/bin/python BMW-4-series/scripts/staging.py          # List waves; * marks active
.venv/bin/python BMW-4-series/scripts/staging.py TG0.2    # Park the old wave and enable the next
.venv/bin/python BMW-4-series/scripts/staging.py none     # Park every research wave
bash scripts/test-repo.sh BMW-4-series
```

The selector updates availability, audit command IDs, and the active-wave
manifest together and rejects any wave over the testing budget before writing.
It does not change regular or rejected commands. Wave
rotation is manual; collect useful paired recordings before selecting another.

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

The 583 rejected commands are excluded for model year 2019. Their `filter` and
`dbgfilter` both use `{"to": 2018, "from": 2020}`, admitting earlier and later
years for debug discovery. This follows the availability/debug-filter pattern
in [Porsche 911](https://github.com/OBDb/Porsche-911/blob/main/signalsets/v3/default.json)
and [Subaru Crosstrek](https://github.com/OBDb/Subaru-Crosstrek/blob/main/signalsets/v3/default.json).
There is no unconditional `dbg` override on these commands, so year-specific
debug metadata can evolve with collected evidence. This prepares the repository
for discovery; the external collection/update service is not tested locally.

Run the vehicle tests through `bash scripts/test-repo.sh BMW-4-series` from the
workspace root, or `python -m pytest tests` in a standalone checkout with the
OBDb schema tools installed. Tests do not require the private scanlog database.

## Contributing

Contributions are welcome! If you would like to add support for additional model years or other configurations, please open an issue or submit a pull request.

1. Fork the repository
2. Create a new branch for your changes
3. Commit your changes and open a pull request with a detailed description

## Issues

If you encounter any issues or would like to discuss improvements, please feel free to open an issue. We encourage collaboration and appreciate feedback to make the repository as accurate and useful as possible.
