"""Discovery configuration and synthetic transport checks, NOT vehicle fixtures.

The external candidates have no confirmed target captures. Synthetic responses
exercise byte extraction, ISO-TP reassembly and routing only, never physical
calibration or vehicle support.
"""
import json
from pathlib import Path
import sys

import jsonschema
import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tests/schemas/python'))

from can.can_frame import CANFrameScanner
from can.command_registry import CommandRegistry
from can.signals import Command, Filter


EXTERNAL = json.loads((ROOT / 'tests/research/external-research.json').read_text())
ACQUISITIONS = EXTERNAL['acquisitions']
DEFINITION = json.loads((ROOT / 'signalsets/v3/default.json').read_text())
STAGING = json.loads((ROOT / 'tests/research/staging-groups.json').read_text())
TIERS = {'Operational': 0.25, 'Engine control': 1, 'Short-term trends': 5,
         'Thermal condition': 15, 'Health and environment': 60,
         'Cumulative history': 300}


def command_key(c):
    return '|'.join((c['hdr'], c.get('eax', ''),
                     ''.join(k + v for k, v in c['cmd'].items())))


COMMANDS = {command_key(c): c for c in DEFINITION['commands']}


def synthetic_frames(receive, pdu, *, pad_single=False):
    """Independently construct 11-bit ISO-TP frames with F1 receive extension.

    Extended-address single frames hold up to six application bytes; first
    frames hold five, and continuation frames six. Single frames normally model
    adapter-trimmed input; the external scanner's padded-single-frame limitation
    is tracked separately below. Multi-frame padding exercises declared length.
    """
    if len(pdu) <= 6:
        frames = [bytes([0xF1, len(pdu)]) + pdu]
    else:
        frames = [bytes([0xF1, 0x10 | (len(pdu) >> 8), len(pdu) & 255]) + pdu[:5]]
        for index, offset in enumerate(range(5, len(pdu), 6), start=1):
            frames.append(bytes([0xF1, 0x20 | (index % 16)]) + pdu[offset:offset+6])
    if len(pdu) > 6 or pad_single:
        frames = [f.ljust(8, b'\xAA') for f in frames]
    return '\n'.join(receive + f.hex().upper() for f in frames)


def parse_one(receive, pdu):
    packets = list(CANFrameScanner.from_ascii_string(
        synthetic_frames(receive, pdu), extended_addressing_enabled=True))
    assert len(packets) == 1
    packet = packets[0]
    assert packet.data == pdu, 'Reassembly must preserve all bytes without padding'
    assert packet.extended_receive_address == 'F1'
    return packet


@pytest.mark.xfail(strict=True, reason=(
    'External schema CANFrameScanner retains single-frame CAN padding '
    '(442b82a); this does not establish client runtime behavior'))
def test_external_scanner_padded_single_frame_honors_declared_length():
    pdu = bytes.fromhex('62D111FE80')
    packets = list(CANFrameScanner.from_ascii_string(
        synthetic_frames('660', pdu, pad_single=True),
        extended_addressing_enabled=True))
    assert len(packets) == 1
    assert packets[0].data == pdu


def test_full_signalset_schema_and_acquisition_identity():
    schema = json.loads((ROOT / 'tests/schemas/signals.json').read_text())
    jsonschema.validate(DEFINITION, schema)
    keys = [command_key(c) for c in DEFINITION['commands']]
    assert len(keys) == len(set(keys)), 'Alternative source decoders must not duplicate requests'
    ids = [s['id'] for c in DEFINITION['commands'] for s in c['signals']]
    assert len(ids) == len(set(ids))
    inventory = EXTERNAL['profile_inventory']
    assert len(inventory) == EXTERNAL['source_working_profile_count'] == 529
    assert len({p['profile_key'] for p in inventory}) == len(inventory)
    assert sum(p['field_count'] for p in inventory) == EXTERNAL['source_working_field_count'] == 1355
    added = {p['command_key'] for p in inventory if p['disposition'] == 'added_debug_discovery'}
    assert added == {a['key'] for a in ACQUISITIONS}
    assert not EXTERNAL['target_vehicle_capture_claim']


@pytest.mark.parametrize('entry', ACQUISITIONS, ids=lambda e: e['key'])
def test_discovery_is_raw_categorized_and_explicitly_unobserved(entry):
    definition = COMMANDS[entry['key']]
    member = next(m for g in STAGING['groups'] for m in g['commands'] if m['key'] == entry['key'])
    assert definition['dbg'] is True
    assert 'dbgfilter' not in definition
    active = entry['staging_group'] == STAGING['active_group']
    assert definition['filter'] == {'years': [STAGING['model_year'] if active else 9999]}
    assert Filter.from_json(definition['filter']).matches(STAGING['model_year']) == active
    assert entry['command_id'] == Command.from_json(definition).id
    assert definition['freq'] == member['interval_seconds'] == TIERS[entry['polling_tier']]
    assert entry['response_status'] == member['response_status'] == 'unobserved'
    assert entry['sample'] is None
    assert entry['observed_target_payload_bytes'] is None
    assert member['payload_bytes'] is None
    assert entry['raw_signal_ids'] == member['raw_signal_ids']
    assert len(definition['signals']) == entry['raw_view_bytes'] == member['raw_view_bytes']
    for i, signal in enumerate(definition['signals']):
        assert signal['id'] == entry['raw_signal_ids'][i]
        assert signal['path'] == f"OBD.Testing.{entry['category']}"
        assert signal['name'].startswith(f"[{entry['staging_group']}]")
        assert 'candidate raw byte' in signal['name']
        assert signal['description'].startswith(f"[Polling: {entry['polling_tier']}] ")
        assert 'unverified' in signal['description'] or 'unknown' in signal['description']
        assert signal['fmt'] == ({'len': 8, 'max': 255, 'unit': 'scalar'} |
                                  ({'bix': i*8} if i else {}))


@pytest.mark.parametrize('entry', ACQUISITIONS, ids=lambda e: e['key'])
def test_synthetic_full_response_preserves_bytes_and_extra_payload(entry):
    definition = COMMANDS[entry['key']]
    # Include zero, FF and high-bit values without inventing invalid-code rules.
    payload = bytes((i*73) % 256 for i in range(entry['raw_view_bytes']))
    payload = (b'\x00\xFF\x80' + payload[3:])[:entry['raw_view_bytes']]
    extra = b'\xFE\xED'
    pdu = bytes.fromhex('62' + definition['cmd']['22']) + payload + extra
    packet = parse_one(definition['rax'], pdu)
    registry = CommandRegistry([Command.from_json(definition)])
    responses = registry.identify_commands(packet)
    assert len(responses) == 1
    assert responses[0].data == payload + extra
    assert responses[0].values == dict(zip(entry['raw_signal_ids'], payload))


@pytest.mark.parametrize('entry', ACQUISITIONS, ids=lambda e: e['key'])
def test_synthetic_short_reply_never_zero_fills_missing_bytes(entry):
    definition = COMMANDS[entry['key']]
    length = min(2, entry['raw_view_bytes'] - 1)
    payload = b'\xFE\x80'[:length]
    pdu = bytes.fromhex('62' + definition['cmd']['22']) + payload
    packet = parse_one(definition['rax'], pdu)
    registry = CommandRegistry([Command.from_json(definition)])
    responses = registry.identify_commands(packet)
    assert len(responses) == 1
    assert responses[0].values == dict(zip(entry['raw_signal_ids'], payload))
    assert len(responses[0].values) < entry['raw_view_bytes']


@pytest.mark.parametrize('entry', ACQUISITIONS, ids=lambda e: e['key'])
def test_synthetic_wrong_ecu_and_negative_reply_are_not_measurements(entry):
    definition = COMMANDS[entry['key']]
    registry = CommandRegistry([Command.from_json(definition)])
    pdu = bytes.fromhex('62' + definition['cmd']['22']) + bytes(entry['raw_view_bytes'])
    assert registry.identify_commands(parse_one('6AA', pdu)) == []
    assert registry.identify_commands(parse_one(definition['rax'], bytes.fromhex('7F2231'))) == []


def test_inferred_routes_and_session_requests_keep_their_qualification():
    by_did = {COMMANDS[a['key']]['cmd']['22']: a for a in ACQUISITIONS}
    for did in ('D114', 'D96B', 'DAD6'):
        entry = by_did[did]
        assert 'hypothesis' in entry['route_status']
        assert len(entry['route_profile_references']) == 2
        assert all('hypothesis' in s['description'] for s in COMMANDS[entry['key']]['signals'])
    for did in ('413A', '4140', '4131'):
        definition = COMMANDS[by_did[did]['key']]
        command = Command.from_json(definition)
        assert command.diagnostic_level_in == 3
        assert command.diagnostic_level_out == 1
        assert all('session' in s['description'] and 'keepalive' in s['description'] for s in definition['signals'])
