"""Discovery reset preservation and acquisition-scope regressions."""
import copy
import importlib.util
import json
from pathlib import Path
import re
import hashlib

import pytest

ROOT = Path(__file__).resolve().parents[2]
DATA = json.loads((ROOT / 'signalsets/v3/default.json').read_text())
MANIFEST = json.loads((ROOT / 'tests/research/staging-groups.json').read_text())
CATALOG = json.loads((ROOT / 'tests/research/discovery-catalog.json').read_text())
PLAN = json.loads((ROOT / 'tests/research/discovery-plan.json').read_text())
HISTORICAL = json.loads((ROOT / 'tests/research/staging-groups-before-reset.json').read_text())


def key(c):
    return '|'.join((c['hdr'], c.get('eax', ''), ''.join(k + v for k, v in c['cmd'].items())))


def test_discovery_scope_and_contiguous_numbering():
    entries = {e['key']: e for e in CATALOG['entries']}
    candidates = [m['key'] for g in MANIFEST['groups'] for m in g['commands']]
    expected = {k for k, e in entries.items() if e['included_in_discovery_pass']}
    assert set(candidates) == expected and len(candidates) == len(set(candidates))
    assert [g['id'] for g in MANIFEST['groups']] == ['TG' + str(i) for i in range(len(MANIFEST['groups']))]
    assert all(g['acquisition_kind'] == 'discovery_only' for g in MANIFEST['groups'])
    definitions = {key(c): c for c in DATA['commands']}
    for k in candidates:
        assert entries[k]['accepted_locally'] is False
        assert entries[k]['support'] in ('supported', 'not_observed')
        assert not definitions[k].get('din') and not definitions[k].get('dout')
    assert not (set(candidates) & set(MANIFEST['rejected_2019_command_keys']))
    # Regression for the earlier scope error: a positive response is not a
    # resolved meaning. Every captured unresolved ordinary-read PID stays in.
    captured = {k for k, e in entries.items() if e['support'] == 'supported' and not e['accepted_locally'] and not definitions[k].get('din') and not definitions[k].get('dout')}
    assert captured <= set(candidates)
    assert len(captured) >= 295
    assert len(candidates) == 318
    assert '6F1|12|22F150' in candidates
    assert len({k for k, e in entries.items() if e['accepted_locally']}) == 96


def test_existing_evidence_and_source_hypotheses_are_not_discarded():
    members = {m['key']: m for g in HISTORICAL['groups'] for m in g['commands']}
    assert len(members) == len(CATALOG['entries']) == 417
    assert {e['key'] for e in CATALOG['entries']} == set(members)
    for e in CATALOG['entries']:
        assert e['source_catalog'] == 'tests/research/staging-groups-before-reset.json'
        assert e['source_hypothesis_count'] == len(members[e['key']].get('decoding_hypotheses', []))
        if e['discovery_disposition'] == 'already_captured_interpretation_pending':
            assert e['native_witnesses']
            assert e['remaining_question']
    held = {e['key'] for e in CATALOG['entries'] if e['discovery_disposition'] == 'session_dependent_acquisition_hold'}
    assert held == {'6F1|18|224131', '6F1|18|22413A', '6F1|18|224140'}


def test_large_reply_is_isolated_and_reference_budget_is_small():
    group = next(g for g in MANIFEST['groups'] if any(m['key'] == '6F1|60|22D12F' for m in g['commands']))
    assert len(group['commands']) == 1
    assert '210' in group['response_cost_note']
    assert all(len(g['commands']) <= 8 and len(g['reference_command_keys']) <= 4 for g in MANIFEST['groups'])
    assert all(g['stop_condition'] and g['rate_estimate_caveat'] for g in MANIFEST['groups'])


def test_no_decoder_or_request_changes_since_published_reset():
    contract = json.loads((ROOT / 'tests/research/discovery-reset-contract.json').read_text())
    commands = copy.deepcopy(DATA['commands'])
    assert len(commands) == contract['command_count']
    for command in commands:
        signals = []
        for signal in command['signals']:
            if signal['id'].startswith('BMW_TEST_REF_'):
                continue
            if signal.get('path', '').startswith('Battery.TG'):
                signal['path'] = 'Battery.Research'
                signal['name'] = re.sub(r'^\[TG[^\]]+\]\s*', '', signal['name'])
            signals.append(signal)
        command['signals'] = signals
    actual = hashlib.sha256(json.dumps(commands, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    assert actual == contract['normalized_commands_sha256']


def load_builder():
    spec = importlib.util.spec_from_file_location('discovery_builder', ROOT / 'scripts/build_discovery_groups.py')
    builder = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(builder)
    return builder


def test_generation_is_reproducible():
    builder = load_builder()
    data, manifest = builder.build()
    assert builder.render(data) == (ROOT / 'signalsets/v3/default.json').read_text()
    assert manifest == MANIFEST


@pytest.mark.parametrize('mutation', ['duplicate', 'omit_supported', 'add_accepted', 'add_session_held'])
def test_generation_rejects_incomplete_or_ineligible_candidate_coverage(monkeypatch, mutation):
    builder = load_builder()
    original = builder.json.loads
    def altered_plan(text):
        d = original(text)
        if isinstance(d, dict) and d.get('scope') == PLAN['scope']:
            if mutation == 'duplicate':
                d['groups'][0]['candidate_keys'].append(d['groups'][0]['candidate_keys'][0])
            elif mutation == 'omit_supported':
                for g in d['groups']:
                    if '6F1|12|22F150' in g['candidate_keys']:
                        g['candidate_keys'].remove('6F1|12|22F150')
            elif mutation == 'add_accepted':
                d['groups'][0]['candidate_keys'].append('6F1|12|224521')
            else:
                d['groups'][0]['candidate_keys'].append('6F1|18|224131')
        return d
    monkeypatch.setattr(builder.json, 'loads', altered_plan)
    with pytest.raises(ValueError, match='exactly once'):
        builder.build()


def test_new_positive_does_not_remove_unresolved_pid_or_unhold_session_request(monkeypatch):
    builder = load_builder()
    original = builder.json.loads
    def changed_support(text):
        d = original(text)
        if isinstance(d, dict) and d.get('entries') and 'collection_run_id' in d:
            for e in d['entries']:
                if e['key'] in ('6F1|12|22402B', '6F1|18|224131'):
                    e['support'] = 'supported'
        return d
    monkeypatch.setattr(builder.json, 'loads', changed_support)
    _, manifest = builder.build()
    keys = {m['key'] for g in manifest['groups'] for m in g['commands']}
    assert '6F1|12|22402B' in keys
    assert '6F1|18|224131' not in keys
    assert len(keys) == 318
