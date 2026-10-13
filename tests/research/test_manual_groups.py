"""Manual picker groups must select exactly the counted vehicle requests."""
import importlib.util
import json
from pathlib import Path
import re
import sys

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tests/schemas/python'))
from can.signals import Command

spec = importlib.util.spec_from_file_location('staging', ROOT / 'scripts/staging.py')
staging = importlib.util.module_from_spec(spec)
spec.loader.exec_module(staging)
DATA = json.loads((ROOT / 'signalsets/v3/default.json').read_text())
MANIFEST = json.loads((ROOT / 'tests/research/staging-groups.json').read_text())
COMMANDS = {staging.command_key(c): c for c in DATA['commands']}


@pytest.mark.parametrize('group', MANIFEST['groups'], ids=lambda g: g['id'])
def test_picker_regex_selects_exact_requests_and_references(group):
    picker = next(g for g in DATA['signalGroups'] if g['id'] == 'BMW_TEST_' + group['id'].replace('.', '_'))
    assert picker['path'] == 'Battery.Testing'
    assert picker['name'] == group['id'].replace('.', '_')
    assert picker['path'] + '.' + picker['name'] == group['path']
    assert group['path'].startswith('Battery.Testing.')
    # A dot is a path separator, so TG0.1 is one folder named TG0_1.
    assert len(group['path'].split('.')) == 3
    pattern = re.compile(picker['matchingRegex'])
    matched = {key for key, command in COMMANDS.items()
               if any(pattern.fullmatch(s['id']) for s in command['signals'])}
    for member in group['commands']:
        for signal in COMMANDS[member['key']]['signals']:
            assert 'path' not in signal  # No separate candidate-only folder.
            if not signal.get('hidden', False):
                assert pattern.fullmatch(signal['id'])
    estimate = staging.estimate(MANIFEST, [group['id']])
    assert matched == set(estimate['known_request_keys'])
    assert set(MANIFEST['common_reference_command_keys']) <= matched
    assert estimate['unique_requests'] == group['total_unique_requests']
    assert estimate['estimated_hz_per_request'] == group['estimated_hz_per_request']
    for key in matched:
        command = Command.from_json(COMMANDS[key])
        assert command.filter is None or command.filter.matches(2019)


def test_overlap_extra_commands_and_background_share_one_budget():
    one = staging.estimate(MANIFEST, ['TG0.1'])
    assert one['unique_requests'] == 18
    assert one['estimated_hz_per_request'] == pytest.approx(700 / 18 / 60)
    assert staging.estimate(MANIFEST, ['TG0.1', 'TG0.1'], extra_keys=['7DF||010C']) == one
    combined = staging.estimate(MANIFEST, ['TG0.1', 'TG0.2'],
                               extra_keys=['7DF||010C', 'external|route|PID'], background_count=3)
    assert combined['unique_requests'] == 30  # 16 candidates, 10 shared references, 1 extra, 3 background
    assert combined['estimated_hz_per_request'] * 60 * 30 == pytest.approx(700)
    assert combined['estimated_seconds_per_request'] == pytest.approx(30 * 60 / 700)
    assert not (set(MANIFEST['rejected_2019_command_keys']) & set(combined['known_request_keys']))


@pytest.mark.parametrize('selected,background', [(['bad'], 0), ([], 0), (['TG0.1'], -1)])
def test_invalid_budget_input(selected, background):
    with pytest.raises(ValueError):
        staging.estimate(MANIFEST, selected, background_count=background)


def test_new_evidence_covers_tg01_without_claiming_unobserved_discovery():
    review = json.loads((ROOT / 'tests/research/sessions-5421-5444-review.json').read_text())
    entries = {e['key']: e for e in review['commands']}
    assert len(review['sessions']) == 18
    assert sum(s['pid_requests'] for s in review['sessions']) == 59264
    for member in MANIFEST['groups'][0]['commands']:
        evidence = entries[member['key']]
        assert set(evidence['counts']) == {'positive'}
        assert evidence['counts']['positive'] >= 132
        assert evidence['payload_byte_lengths'] == [2]
        assert evidence['distinct_positive_payloads'] > 1
        sample = evidence['samples']['positive']
        hdr, eax, request = member['key'].split('|')
        assert sample['adapter_setup']['ATSH'] == hdr
        assert sample['adapter_setup']['ATCEA'] == eax
        assert sample['adapter_setup']['ATCRA'] == COMMANDS[member['key']]['rax']
        assert sample['packet_hex'].startswith('62' + request[2:])
    assert len(review['external_discovery']) == 26
    assert all(not e['counts'] for e in review['external_discovery'])
