"""Offline response evidence, including candidates whose decoding remains disabled.

Transport tests deliberately do not assert guessed physical values. Numeric
research cases exercise only independently corroborated, redundant definitions.
The normal response suite separately tests enabled, year-filtered commands.
"""

import json
from pathlib import Path
import sys

import pytest

TESTS = Path(__file__).parent.parent
sys.path.insert(0, str(TESTS / "schemas" / "python"))

from can.can_frame import CANFrameScanner
from can.command_registry import CommandRegistry
from can.signals import Command, Filter


AUDIT = json.loads((TESTS / "research" / "scanlog-audit.json").read_text())
CASES = json.loads((TESTS / "research" / "corroborated-decoding-cases.json").read_text())


def packets(capture):
    # Keep exact adapter bytes in evidence; normalize line endings only at the
    # parser boundary, just as YAML response fixtures use line-feed separators.
    response = bytes.fromhex(capture["response_hex"]).decode("ascii")
    return list(CANFrameScanner.from_ascii_string(
        response.replace("\r", "\n").strip(),
        extended_addressing_enabled=True,
    ))


@pytest.mark.parametrize("entry", AUDIT["entries"], ids=lambda e: e["key"])
def test_recorded_response_identity(entry):
    """Each requested PID has an actual routed positive or negative capture."""
    capture = entry["sample"]
    header, extension, request = entry["key"].split("|")
    setup = capture["adapter_setup"]
    assert setup["ATSH"] == header
    assert setup["ATCEA"] == extension
    assert setup["ATCRA"] == entry["receive_header"]
    assert capture["sent_command"][:6] == request

    received = packets(capture)
    assert len(received) == 1
    packet = received[0]
    assert packet.can_identifier == entry["receive_header"]
    assert packet.extended_receive_address == "F1"
    assert packet.data.hex().upper() == capture["expected_packet_hex"]
    if entry["response_status"] == "positive":
        assert packet.data[:3] == bytes.fromhex("62" + request[2:])
    else:
        # NRC 0x31 rejects this request on the observed ECU, not all BMWs.
        assert packet.data == bytes.fromhex("7F2231")


@pytest.fixture(scope="module")
def research_commands():
    data = json.loads((TESTS.parent / "signalsets" / "v3" / "default.json").read_text())
    return {
        "|".join((c["hdr"], c.get("eax", ""), "".join(k + v for k, v in c["cmd"].items()))): c
        for c in data["commands"]
    }


@pytest.mark.parametrize("capture", CASES, ids=lambda c: c["key"])
def test_corroborated_conversion(capture, research_commands):
    """Preserve the recorded conversion and its independent reference evidence."""
    definition = research_commands[capture["key"]]
    registry = CommandRegistry([Command.from_json(definition)])
    values = {}
    for packet in packets(capture):
        for response in registry.identify_commands(packet):
            values.update(response.values)
    assert values == pytest.approx(capture["expected_values"], abs=0.00001)


@pytest.mark.parametrize("year", [2014, 2018, 2019, 2020, 2026, 2035])
def test_rejected_commands_exclude_2019_and_allow_other_year_research(year, research_commands):
    """A failed 2019 probe must not suppress research on other model years."""
    for entry in AUDIT["entries"]:
        if entry["response_status"] != "negative_only":
            continue
        definition = research_commands[entry["key"]]
        command = Command.from_json(definition)
        assert command.filter.matches(year) == (year != 2019), entry["key"]
        assert Filter.from_json(definition["dbgfilter"]).matches(year) == (year != 2019), entry["key"]
        assert not command.debug, "Use year-specific debug metadata, not an unconditional override"
        assert command.id == entry["command_id"]


@pytest.mark.parametrize("key", AUDIT["graduation"]["command_keys"])
def test_graduated_commands_are_regular_only_for_verified_year(key, research_commands):
    """Graduation must preserve research status outside the verified year."""
    definition = research_commands[key]
    command = Command.from_json(definition)
    assert not command.debug
    assert "filter" not in definition or Filter.from_json(definition["filter"]).matches(2019)
    debug_filter = Filter.from_json(definition["dbgfilter"])
    assert not debug_filter.matches(2019)
    for year in [2014, 2018, 2020, 2026]:
        assert debug_filter.matches(year)


STAGING = json.loads((TESTS / 'research' / 'staging-groups.json').read_text())
STAGED = [m for g in STAGING['groups'] for m in g['commands']]


def test_staging_partition_and_activation(research_commands):
    keys = [m['key'] for m in STAGED]
    assert len(keys) == len(set(keys)) == 380
    assert set(keys) == {e['key'] for e in AUDIT['entries'] if e['decoding_status'] == 'unverified_decoding'}
    for group in STAGING['groups']:
        assert 1 <= len(group['commands']) <= 8
        assert sum(60 / m['interval_seconds'] for m in group['commands']) + STAGING['background_testing_requests_per_minute'] <= 400
        assert STAGING['testing_budget_requests_per_minute'] == 400
        for member in group['commands']:
            definition = research_commands[member['key']]
            command = Command.from_json(definition)
            assert command.debug == (group['id'] != STAGING['active_group'])
            assert 'dbgfilter' not in definition
            assert command.filter.matches(2019) == (group['id'] == STAGING['active_group'])
            assert not command.filter.matches(2018)
            assert not command.filter.matches(2020)
            assert definition['freq'] == member['interval_seconds']
            assert 0 < definition['freq'] <= 10


@pytest.mark.parametrize('member', STAGED, ids=lambda m: m['key'])
def test_staged_raw_bytes_match_recorded_payload(member, research_commands):
    entry = next(e for e in AUDIT['entries'] if e['key'] == member['key'])
    packet = packets(entry['sample'])[0]
    payload = packet.data[3:]
    assert len(payload) == member['payload_bytes']
    definition = research_commands[member['key']]
    registry = CommandRegistry([Command.from_json(definition)])
    values = {}
    for response in registry.identify_commands(packet):
        values.update(response.values)
    assert values == dict(zip(member['raw_signal_ids'], payload))
    assert all(s['fmt']['unit'] == 'scalar' for s in definition['signals'])


def test_switching_wave_preserves_other_commands_and_can_park_all(tmp_path):
    import importlib.util
    import shutil
    spec = importlib.util.spec_from_file_location('bmw_staging', TESTS.parent / 'scripts/staging.py')
    staging = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(staging)
    for relative in ['signalsets/v3/default.json', 'tests/research/staging-groups.json',
                     'tests/research/scanlog-audit.json']:
        target = tmp_path / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(TESTS.parent / relative, target)
    path = tmp_path / 'signalsets/v3/default.json'
    original = json.loads(path.read_text())
    managed = {m['key'] for m in STAGED}
    for selected in ['TG0.2', 'none', 'TG0.1']:
        staging.select_group(tmp_path, selected)
        current = json.loads(path.read_text())
        for before, after in zip(original['commands'], current['commands']):
            if staging.command_key(before) not in managed:
                assert before == after
        enabled = {staging.command_key(c) for c in current['commands']
                   if staging.command_key(c) in managed and Command.from_json(c).filter.matches(2019)}
        expected = {m['key'] for g in STAGING['groups'] if g['id'] == selected for m in g['commands']}
        assert enabled == expected
        for definition in current['commands']:
            key = staging.command_key(definition)
            if key in managed:
                assert Command.from_json(definition).debug == (key not in expected)
                assert 'dbgfilter' not in definition
    before = path.read_bytes()
    with pytest.raises(ValueError):
        staging.select_group(tmp_path, 'TG-does-not-exist')
    assert path.read_bytes() == before


def test_over_budget_wave_is_rejected_before_writing(tmp_path):
    import importlib.util
    spec = importlib.util.spec_from_file_location('bmw_staging_budget', TESTS.parent / 'scripts/staging.py')
    staging = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(staging)
    manifest = json.loads(json.dumps(STAGING))
    manifest['groups'][0]['commands'][0]['interval_seconds'] = 0.1
    path = tmp_path / 'tests/research/staging-groups.json'
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps(manifest))
    before = path.read_bytes()
    with pytest.raises(ValueError, match='exceeds the request budget'):
        staging.select_group(tmp_path, manifest['groups'][0]['id'])
    assert path.read_bytes() == before
    assert not (tmp_path / 'signalsets').exists()


def test_background_testing_reservation_matches_current_definitions(research_commands):
    managed = {m['key'] for m in STAGED}
    background = 0
    for key, definition in research_commands.items():
        command = Command.from_json(definition)
        if key in managed or (command.filter and not command.filter.matches(2019)):
            continue
        debug = definition.get('dbg') or ('dbgfilter' in definition and Filter.from_json(definition['dbgfilter']).matches(2019))
        if debug:
            background += 60 / definition['freq']
    assert background == pytest.approx(STAGING['background_testing_requests_per_minute'])


def test_polling_tier_labels_match_command_intervals(research_commands):
    tiers = {
        'Operational': 0.25,
        'Engine control': 1,
        'Short-term trends': 5,
        'Thermal condition': 15,
        'Health and environment': 60,
        'Cumulative history': 300,
    }
    for entry in AUDIT['entries']:
        definition = research_commands[entry['key']]
        if entry['decoding_status'] in ('regular_2019', 'existing_regular_2019'):
            descriptions = [s['description'] for s in definition['signals']]
            prefixes = [f'[Polling: {tier}] ' for tier, interval in tiers.items()
                        if interval == definition['freq']]
            assert len(prefixes) == 1
            assert all(d.startswith(prefixes[0]) for d in descriptions)
        else:
            assert all(s['description'].startswith('[Polling: Unclassified; research override] ')
                       for s in definition['signals'])
    for member in STAGED:
        assert all(s['description'].startswith('[Polling: Unclassified; research override] ')
                   for s in member['decoding_hypotheses'])


TPMS_INVALID = json.loads((TESTS / 'research/invalid-values/tpms.json').read_text())


@pytest.mark.parametrize('capture', TPMS_INVALID['samples'], ids=lambda c: str(c['record_pk']))
def test_tpms_unavailable_values_preserve_other_fields(capture, research_commands):
    key = '|'.join((capture['route']['hdr'], capture['route']['eax'], capture['command']))
    definition = research_commands[key]
    packet = packets({'response_hex': capture['raw_response_hex']})[0]
    assert packet.data.hex().upper() == capture['packet_hex']
    assert packet.can_identifier == capture['route']['rax']
    registry = CommandRegistry([Command.from_json(definition)])
    values = {}
    for response in registry.identify_commands(packet):
        values.update(response.values)
    wheel = capture['wheel']
    if capture['classification'] == 'unavailable_pair':
        assert values[f'4SERIES_TP_{wheel}'] is None
        assert values[f'4SERIES_TT_{wheel}'] is None
    else:
        assert values[f'4SERIES_TP_{wheel}'] == pytest.approx(capture['pressure_bar'])
        assert values[f'4SERIES_TT_{wheel}'] == capture['temperature_celsius']
    assert values[f'4SERIES_TP_SET_{wheel}'] == pytest.approx(capture['setpoint_bar'])
    assert values[f'4SERIES_TPMS_POS_{wheel}'] == capture['position_raw']


@pytest.mark.parametrize('did', ['DC98', 'DC99', 'DC9A', 'DC9B'])
def test_tpms_null_bounds_are_inclusive_and_do_not_mask_neighbors(did, research_commands):
    from can.signals import Scaling
    definition = research_commands[f'6F1|29|22{did}']
    pressure = Scaling.from_json(next(s['fmt'] for s in definition['signals'] if s['id'].startswith('4SERIES_TP_') and not s['id'].startswith('4SERIES_TP_SET_')))
    temperature = Scaling.from_json(next(s['fmt'] for s in definition['signals'] if s['id'].startswith('4SERIES_TT_')))
    # Synthetic boundary cases verify the configured inclusive range; they are
    # not claims that these adjacent values were observed on the vehicle.
    for raw, expected in [(0, 0), (6299, 6.299), (6300, None), (6301, None)]:
        payload = bytearray(8)
        payload[5:7] = raw.to_bytes(2, 'little')
        value = pressure.decode_value(payload)
        assert value is None if expected is None else value == pytest.approx(expected)
    for raw, expected in [(0, 0), (126, 126), (127, None)]:
        payload = bytearray(8)
        payload[7] = raw
        value = temperature.decode_value(payload)
        assert value is None if expected is None else value == expected


DME_INVALID = json.loads((TESTS / 'research/invalid-values/dme.json').read_text())
LAMBDA_STARTUP = DME_INVALID['solid_proposals'][0]['evidence']
DME_STARTUP_CASES = [
    (capture, expected)
    for category, expected in [('zero_records', None), ('paired_catalyst', None),
                               ('later_plausible', 'numeric'), ('paired_lambda1_first', 'numeric')]
    for capture in LAMBDA_STARTUP[category]
]


@pytest.mark.parametrize('capture,expected', DME_STARTUP_CASES, ids=[str(c['record']) for c, _ in DME_STARTUP_CASES])
def test_recorded_dme_startup_values(capture, expected, research_commands):
    route = capture['route']
    key = '|'.join((route['ATSH'], route['ATCEA'], capture['command']))
    definition = research_commands[key]
    packet = packets({'response_hex': capture['raw_hex']})[0]
    assert packet.can_identifier == route['ATCRA']
    assert packet.data[3:].hex().upper() == capture['payload']
    registry = CommandRegistry([Command.from_json(definition)])
    values = {}
    for response in registry.identify_commands(packet):
        values.update(response.values)
    value = values[definition['signals'][0]['id']]
    if expected is None:
        assert value is None
    else:
        assert value == pytest.approx(int(capture['payload'], 16) / 4096)


def test_lambda_zero_filter_preserves_small_positive_and_lean_values(research_commands):
    from can.signals import Scaling
    scaling = Scaling.from_json(research_commands['6F1|12|22582C']['signals'][0]['fmt'])
    assert scaling.decode_value(bytes.fromhex('0000')) is None
    assert scaling.decode_value(bytes.fromhex('0001')) == pytest.approx(1 / 4096)
    assert scaling.decode_value(bytes.fromhex('1000')) == 1
    assert scaling.decode_value(bytes.fromhex('FF00')) == 15.9375


def test_invalid_value_catalog_tracks_all_configured_null_bounds(research_commands):
    catalog = json.loads((TESTS / 'research/invalid-values/index.json').read_text())
    documented = {}
    for rule in catalog['rules']:
        documented.setdefault(rule['signal_id'], {}).update(rule['configured_bounds'])
    actual = {s['id']: {k: v for k, v in s['fmt'].items() if k in ('nullmin', 'nullmax')}
              for c in research_commands.values() for s in c['signals']
              if any(k in s.get('fmt', {}) for k in ('nullmin', 'nullmax'))}
    assert documented == actual
