#!/usr/bin/env python3
"""Build reviewed discovery-only picker groups; no phone or network operations.

Input evidence/source decisions live in discovery-catalog.json; the original
manifest remains immutable historical provenance. --check verifies determinism.
"""
import argparse
import copy
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESEARCH = ROOT / 'tests/research'
sys.path.insert(0, str(ROOT / 'tests/schemas/python'))
from json_formatter import format_json_data


def key(c):
    return '|'.join((c['hdr'], c.get('eax', ''), ''.join(k + v for k, v in c['cmd'].items())))


def build():
    old = json.loads((RESEARCH / 'staging-groups-before-reset.json').read_text())
    catalog = json.loads((RESEARCH / 'discovery-catalog.json').read_text())
    plan = json.loads((RESEARCH / 'discovery-plan.json').read_text())
    data = json.loads((ROOT / 'signalsets/v3/default.json').read_text())
    entries = {e['key']: e for e in catalog['entries']}
    members = {m['key']: m for g in old['groups'] for m in g['commands']}
    commands = {key(c): c for c in data['commands']}
    active = [k for g in plan['groups'] for k in g['candidate_keys']]
    eligible = {k for k, e in entries.items() if not e['accepted_locally'] and not commands[k].get('din') and not commands[k].get('dout')}
    if any(e['included_in_discovery_pass'] != (k in eligible) for k, e in entries.items()):
        raise ValueError('Catalog discovery eligibility disagrees with acceptance/session requirements')
    if len(active) != len(set(active)) or set(active) != eligible:
        raise ValueError('Plan must cover each unresolved ordinary-read discovery candidate exactly once, including captured positives')
    # Strip generated display views only. Requests, formats, validity, routing,
    # applicability and frequency remain exactly as published at the reset.
    data['signalGroups'] = [g for g in data.get('signalGroups', []) if not g['id'].startswith('BMW_TEST_')]
    for c in data['commands']:
        c['signals'] = [s for s in c['signals'] if not s['id'].startswith('BMW_TEST_REF_')]
        for s in c['signals']:
            if s.get('path', '').startswith('Battery.TG'):
                s['path'] = 'Battery.Research'
                s['name'] = re.sub(r'^\[TG[^\]]+\]\s*', '', s['name'])
    groups = []
    common = plan['common_reference_command_keys']
    for number, proposed in enumerate(plan['groups']):
        gid = proposed['id']
        if gid != 'TG' + str(number):
            raise ValueError('Discovery identifiers must be contiguous from TG0')
        route_keys = proposed['candidate_keys']
        if not 1 <= len(route_keys) <= plan['max_candidates_per_group']:
            raise ValueError('Candidate count outside reviewed bound')
        refs = list(dict.fromkeys(common + proposed.get('additional_reference_command_keys', [])))
        path = 'Battery.' + gid
        aliases, visible, group_members = {}, [], []
        for k in route_keys:
            c = commands[k]
            if c.get('din') or c.get('dout'):
                raise ValueError('Session-dependent requests require a separate acquisition review')
            m = copy.deepcopy(members[k])
            m['discovery_disposition'] = entries[k]['discovery_disposition']
            m['evidence_record'] = 'tests/research/discovery-catalog.json#' + k
            m['discovery_goal'] = entries[k]['discovery_goal']
            m['historical_response_status'] = m.get('response_status')
            m['response_status'] = entries[k]['support']
            m['capture_status'] = entries[k]['support']
            m['current_payload_lengths'] = entries[k]['observed_payload_lengths']
            m['remaining_question'] = entries[k]['remaining_question']
            m['source_family'] = entries[k]['source_family']
            group_members.append(m)
            for s in c['signals']:
                s['path'] = path
                s['name'] = '[' + gid + '] ' + re.sub(r'^\[TG[^\]]+\]\s*', '', s['name'])
                if not s.get('hidden', False):
                    visible.append(s['id'])
        for k in refs:
            c = commands[k]
            originals = [s for s in c['signals'] if not s.get('hidden', False) and not s['id'].startswith('BMW_TEST_REF_')]
            for original in originals:
                alias = copy.deepcopy(original)
                alias['id'] = 'BMW_TEST_REF_' + gid + '_' + original['id']
                alias['path'] = path
                alias['name'] = '[' + gid + '] ' + original['name'] + ' (context)'
                alias['description'] = '[Polling: On demand] Existing published reference shown as general discovery context; shares the original request and decoder. ' + original.get('description', '')
                aliases[alias['id']] = original['id']
                visible.append(alias['id'])
                c['signals'].append(alias)
        count = len(set(route_keys) | set(refs))
        budget = old['testing_budget_requests_per_minute']
        groups.append({'id': gid, 'path': path, 'purpose': proposed['purpose'],
                       'acquisition_kind': 'discovery_only', 'commands': group_members,
                       'reference_command_keys': refs, 'reference_signal_aliases': aliases,
                       'context_roles': plan['reference_roles'], 'total_unique_requests': count,
                       'estimated_hz_per_request': budget / count / 60,
                       'rate_estimate_caveat': 'Unmeasured equal-request planning arithmetic; multi-frame replies and background traffic invalidate a guaranteed cadence.',
                       'response_cost_note': proposed.get('response_cost_note'),
                       'stop_condition': proposed['stop_condition']})
        data['signalGroups'].append({'id': 'BMW_TEST_' + gid, 'path': 'Battery', 'name': gid,
                                     'matchingRegex': '^(?:' + '|'.join(re.escape(s) for s in visible) + ')$'})
    manifest = {k: copy.deepcopy(v) for k, v in old.items() if k != 'groups'}
    manifest.update(selection_mode='discovery_only', groups=groups,
                    common_reference_command_keys=common,
                    previous_group_catalog='tests/research/staging-groups-before-reset.json',
                    discovery_catalog='tests/research/discovery-catalog.json',
                    policy='All unresolved ordinary-read candidates are active, including already captured positives. Discovery seeks useful meanings and decoders with source knowledge and broad conditions; no targeted experiment groups.')
    return data, manifest


def render(data):
    return format_json_data(data)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    data, manifest = build()
    outputs = {ROOT / 'signalsets/v3/default.json': render(data),
               RESEARCH / 'staging-groups.json': json.dumps(manifest, indent=2) + '\n'}
    for path, content in outputs.items():
        if args.check:
            if path.read_text() != content:
                raise SystemExit('Generated content differs: ' + str(path))
        else:
            path.write_text(content)
    print(json.dumps({'groups': len(manifest['groups']), 'candidate_requests': sum(len(g['commands']) for g in manifest['groups']), 'mode': 'checked' if args.check else 'built', 'publication': 'local_only'}))


if __name__ == '__main__':
    main()
