# Session 5399 review — October 7, 2026

Keep TG0.1 active and retain the 400 requests/minute allowance. Do not rotate yet. The user confirmed the latest configuration and debug collection were enabled for a full drive. The log contains the expected eight candidates, but their observed interval is approximately 30 seconds, not the configured 1–2 seconds. This does not test sustainability at the intended workload. A client debug scheduling floor or selection policy is a hypothesis; the database does not identify the cause.

## Direct verification

The bundle contains 5,399 sessions versus 5,397 at handoff. Sessions 5398 and 5399 have distinct session IDs and match the handoff vehicle VIN privately (year code K); VINs are excluded from this report. Their command record ranges are 52789354–52793837 and 52793838–52807229. Session 5399 has 13,392 records and timestamps 23:01:08–23:10:16 UTC. Session 5398 predates the configuration change and is not a post-change measurement. This establishes new database contents without relying on filesystem modification dates; no previous whole-file hash exists to compare. Scoped content hashes are saved for future comparisons.

## Cadence

Full-session, startup-excluded, and candidate operating-window tables for every observed route are in `session-5399-review.json`. Route keys are transmit header | extended address | receive filter | request. Successful routing commands and response headers are checked; adapter resets clear tracked state. Standard OBD requested intervals are not available in the local vehicle file, so those entries are null. Requested intervals for all sessions refer to current local definitions, not verified historical client configuration. Actual UI selections are unknown; recorded requests establish the polled subset.

The table below covers elapsed 60.000–478.031 seconds, ending at the last nonzero RPM record. This is an analysis window rather than a claim of identical conditions or uninterrupted running. No pause duration was subtracted. All staged responses in this window were positive.

| Request | Requested s | Samples | Median s | p95 s | Delivered/min |
| --- | ---: | ---: | ---: | ---: | ---: |
| 6F1|12|612|224204 | 2 | 14 | 30.212 | 31.892 | 2.009 |
| 6F1|12|612|224310 | 2 | 14 | 30.285 | 32.211 | 2.009 |
| 6F1|12|612|224402 | 2 | 14 | 30.254 | 31.606 | 2.009 |
| 6F1|12|612|224409 | 2 | 14 | 30.195 | 32.044 | 2.009 |
| 6F1|12|612|224421 | 1 | 14 | 30.33 | 31.756 | 2.009 |
| 6F1|12|612|224422 | 1 | 14 | 30.27 | 31.441 | 2.009 |
| 6F1|12|612|224423 | 1 | 14 | 30.302 | 32.026 | 2.009 |
| 6F1|12|612|224425 | 2 | 14 | 30.335 | 31.531 | 2.009 |
| 6F1|12|612|224AB1 | 0.25 | 555 | 0.705 | 1.14 | 79.659 |
| 7E1||7E9|010C | unknown | 553 | 0.705 | 1.125 | 79.372 |

The eight staged commands together delivered approximately 16.1 requests/minute in this window, versus 330/minute configured. Full-session capture yielded 18 positive two-byte responses per candidate. Speed had one NO DATA response in the operating window; RPM had none. Speed and RPM median intervals were both 0.705 seconds, versus approximately 0.72 seconds in the shorter handoff-session operating window. The earlier 5398 drive was slower (approximately 1.67 seconds), but its configuration differs. This comparison does not isolate a causal effect of the testing change. Speed still misses its local 0.25-second request interval. Same scanner name and interface ID are consistent with the same adapter, without independently verifying hardware.

## Decoding evidence

The drive reached 68.51 km/h and 3,986 RPM. Standard coolant rose from 74 to 111 C; initial oil reference was 84 C. This is a warm-engine drive, not a cold-soak recording. Shutdown/zero readings are retained in the reference series and are not declared invalid solely because they occur at session end. Every staged capture includes record PK, command ID, timestamp, routing state, raw response hex, and payload; reference series are timestamped relative to session start.

- 4204 remained `0BAF` while the ambient reference ranged only 26–27 C. This does not establish field width or conversion.
- 4310 changed between `2AF8` and `32C8` (11000 and 13000). Dividing by 100 would yield plausible target values of 110 and 130 C, but this is not proof of target identity or units.
- 4402 varied through `00AE`–`00CD` before ending at `0040`. The inherited 0.75*x−48 interpretation is not established by this drive; zero-like post-run results are not enough to assign sentinel handling.
- 4425 rose from `0258` to `02DA`; a rising raw quantity does not independently establish an oil-temperature location or scale.
- 4409 remained `48F4`; no independent oil-level reference was supplied.
- 4421/4422/4423 contain both low and high-bit-set values and finish at zero. Signed control terms and unsigned sensor values remain competing interpretations; no pressure units or sentinel bounds are assigned.

No candidate is graduated and no invalid-value filter is changed. The exact capture evidence supports follow-up without embedding the private database.

## Next collection

Keep TG0.1 and the 400/minute ceiling. First verify how the client schedules debug-only commands: use a short capture to check whether explicitly selecting the TG0.1 raw signals, where supported, changes their actual cadence to 1–2 seconds. Confirm cadence before another long drive; repeating the current selection may simply collect more 30-second samples. Then capture cold start/warm-up and a comparable warm drive, with standard coolant/oil/RPM/voltage references and an independent ambient/oil-level reference where available. Do not raise the budget based on aggregate traffic. If scheduling remains ambiguous, compare research-on and research-off under similar conditions.

Validation: every saved staged frame was parsed with the repository CAN parser and matched its route, positive DID response, and two-byte payload. Configuration and fixture files are unchanged, so the vehicle implementation suite was not rerun.
