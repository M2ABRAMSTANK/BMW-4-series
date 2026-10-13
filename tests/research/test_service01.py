"""2019 service 01 support, route selection, and captured multi-frame evidence."""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tests/schemas/python'))
from can.can_frame import CANFrameScanner
from can.command_registry import CommandRegistry, get_model_year_command_registry
from can.signals import Command

COMMANDS = json.loads((ROOT / 'signalsets/v3/default.json').read_text())['commands']
EVIDENCE = json.loads((ROOT / 'tests/research/service01-2019-provenance.json').read_text())
SERVICE01 = [c for c in COMMANDS if c.get('rax') in {'7E8', '7E9'} and '01' in c.get('cmd', {})]


def test_bitmap_coverage_matches_observed_routes():
    expected = {
        '7E8': set('01 03 04 05 06 07 0B 0C 0D 0E 0F 10 11 13 15 1C 1F 21 23 2E 2F 30 31 33 34 3C 41 42 43 44 45 46 47 49 4A 4C 51 56 5C 62 63 68 83 8E 9D 9E A6'.split()),
        '7E9': set('01 04 05 0C 0D 11 21 41 42'.split()),
    }
    for route, pids in expected.items():
        assert set(EVIDENCE['advertised_data_pids'][route]) == pids
        configured = {c['cmd']['01'] for c in SERVICE01 if c['rax'] == route}
        assert pids <= configured
    assert EVIDENCE['advertised_without_positive_payload'] == {'7E8': ['41', '83'], '7E9': []}


def test_physical_route_and_polling_override_are_selected():
    # The production registry includes the shared SAE commands before the
    # vehicle's definitions. Check precedence with both sources present.
    registry = get_model_year_command_registry(2019)
    for route, expected_id, expected_value in [
        ('7E8', '7DF.7E8.0104|f=2019', 28 * 100 / 255),
        ('7E9', '7E1.7E9.0104|f=2019', 23 * 100 / 255),
    ]:
        raw = EVIDENCE['positive_records'][route]['04']['response']
        packets = list(CANFrameScanner.from_ascii_string(raw.replace('\r', '\n')))
        responses = [r for p in packets for r in registry.identify_commands(p)]
        assert len(responses) == 1
        assert responses[0].command.id == expected_id
        assert responses[0].command.update_frequency == 0.01
        assert abs(responses[0].values[('LOAD_PCT' if route == '7E8' else 'LOAD_PCT_7E9')] - expected_value) < 0.0001


def test_pid_68_real_multiframe_temperature_payload():
    command = Command.from_json(next(c for c in SERVICE01 if c['rax'] == '7E8' and c['cmd']['01'] == '68'))
    raw = EVIDENCE['positive_records']['7E8']['68']['full_response_ascii']
    packets = list(CANFrameScanner.from_ascii_string(raw.replace('\r', '\n')))
    responses = [r for p in packets for r in CommandRegistry([command]).identify_commands(p)]
    assert len(responses) == 1
    assert responses[0].values['IAT_11_SUP'] == 1
    assert responses[0].values['IAT_11'] == 18
    assert responses[0].values['IAT_12_SUP'] == 1
    assert responses[0].values['IAT_12'] == 5
    assert command.update_frequency == 0.01


def test_all_service01_commands_use_manual_polling():
    assert len(SERVICE01) == 65
    for command in SERVICE01:
        assert command['freq'] == 0.01
        assert all(s['description'].startswith('[Polling: On demand] ')
                   for s in command['signals'])


def test_uncaptured_pids_are_visible_for_manual_discovery():
    for pid in ('41', '83'):
        command = next(c for c in SERVICE01 if c['rax'] == '7E8' and c['cmd']['01'] == pid)
        assert 'dbg' not in command
        assert command['filter'] == {'years': [2019]}
        assert all(s['path'] == 'Battery.Testing.TG18_1' for s in command['signals'])
