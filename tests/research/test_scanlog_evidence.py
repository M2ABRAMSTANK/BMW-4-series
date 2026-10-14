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
        assert "dbgfilter" not in definition
        assert not command.debug
        assert command.id == entry["command_id"]


@pytest.mark.parametrize("key", AUDIT["graduation"]["command_keys"])
def test_graduated_commands_remain_available_for_verified_year(key, research_commands):
    """Removing debug must retain the known 2019 availability."""
    definition = research_commands[key]
    command = Command.from_json(definition)
    assert not command.debug
    assert "filter" not in definition or Filter.from_json(definition["filter"]).matches(2019)
    assert "dbgfilter" not in definition


STAGING = json.loads((TESTS / 'research' / 'staging-groups.json').read_text())
STAGED = [m for g in STAGING['groups'] for m in g['commands']]
EXTERNAL = json.loads((TESTS / 'research' / 'external-research.json').read_text())
DISCOVERY_KEYS = {e['key'] for e in EXTERNAL['acquisitions']}
RECORDED_STAGED = [m for m in STAGED if 'payload_bytes' in m and m['key'] not in DISCOVERY_KEYS]


def test_all_research_groups_are_visible_without_debug(research_commands):
    keys = [m['key'] for m in STAGED]
    assert len(RECORDED_STAGED) == 380
    assert len(keys) == len(set(keys)) == 417
    assert STAGING['selection_mode'] == 'manual_all_visible'
    assert STAGING['testing_budget_requests_per_minute'] == 700
    for definition in research_commands.values():
        assert 'dbg' not in definition and 'dbgfilter' not in definition
        assert definition['freq'] == 0.01
    for group in STAGING['groups']:
        assert 1 <= len(group['commands']) <= 8
        for member in group['commands']:
            definition = research_commands[member['key']]
            command = Command.from_json(definition)
            assert not command.debug
            assert command.filter is None or command.filter.matches(2019)
            assert all(s['path'] == group['path'] for s in definition['signals']
                       if not s['id'].startswith('BMW_TEST_REF_'))


@pytest.mark.parametrize('member', RECORDED_STAGED, ids=lambda m: m['key'])
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


def test_on_demand_prefixes(research_commands):
    for definition in research_commands.values():
        assert all(s['description'].startswith('[Polling: On demand] ')
                   for s in definition['signals'])


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
              if any(k in s.get('fmt', {}) for k in ('nullmin', 'nullmax'))
              and not s['id'].startswith('BMW_TEST_REF_')}
    assert documented == actual
