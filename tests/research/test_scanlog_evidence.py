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
        assert sum(60 / m['interval_seconds'] for m in group['commands']) + STAGING['background_testing_requests_per_minute'] <= 200
        assert STAGING['testing_budget_requests_per_minute'] == 200
        for member in group['commands']:
            definition = research_commands[member['key']]
            command = Command.from_json(definition)
            assert command.debug
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
