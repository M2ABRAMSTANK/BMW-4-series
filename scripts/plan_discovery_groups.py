#!/usr/bin/env python3
"""Plan broad semantic-discovery groups from reviewed source-family mappings."""
import argparse
import collections
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESEARCH = ROOT / 'tests/research'


def plan():
    families = json.loads((RESEARCH / 'discovery-families.json').read_text())
    catalog = json.loads((RESEARCH / 'discovery-catalog.json').read_text())
    entries = {e['key']: e for e in catalog['entries']}
    eligible = {k for k, e in entries.items() if e['included_in_discovery_pass']}
    mapping = families['entries']
    if set(mapping) != eligible:
        raise ValueError('Reviewed family mapping must cover all unresolved ordinary-read candidates')
    groups = []
    for family in sorted(families['families'], key=lambda f: f['order']):
        routes = collections.defaultdict(list)
        for k, m in mapping.items():
            if m['family'] == family['id']:
                hdr, eax, request = k.split('|')
                routes[(hdr, eax, entries[k]['response_header'])].append(k)
        ordered = sorted(routes, key=lambda r: (not any(entries[k]['support'] == 'not_observed' for k in routes[r]), r))
        for route in ordered:
            members = sorted(routes[route], key=lambda k: (entries[k]['support'] != 'not_observed', k))
            for offset in range(0, len(members), 8):
                keys = members[offset:offset + 8]
                group = {'id': 'TG' + str(len(groups)),
                         'purpose': 'Broad meaning discovery: ' + family['name'],
                         'source_family': family['id'], 'candidate_keys': keys,
                         'additional_reference_command_keys': [family['additional_context_key']] if family['additional_context_key'] else [],
                         'stop_condition': 'Review retained source definitions and existing/new raw behavior across useful ordinary conditions. Close each candidate with a qualified decode, an evidence-supported fitment decision, or a precise question for the later targeted pass. A captured positive alone does not resolve its meaning.'}
                if family['id'] == 'cluster_large_history':
                    group['response_cost_note'] = 'Source expects at least 210 measurement bytes. Isolate this multi-frame reply; use complete stored payloads and avoid redundant high-rate copies when history/meaning can be investigated offline.'
                groups.append(group)
    return {'scope': '2019 BMW 430i; broad semantic discovery for every unresolved ordinary-read PID, captured or uncaptured',
            'publication': 'owner-approved for publication to M2ABRAMSTANK/BMW-4-series main',
            'max_candidates_per_group': 8,
            'common_reference_command_keys': ['7DF||010C', '7DF||010D', '7DF||0142'],
            'reference_roles': {'7DF||010C': 'Engine-running/stopped and speed context', '7DF||010D': 'Stationary/moving context',
                                '7DF||0142': 'Module supply-voltage context', '7DF||0104': 'Broad engine-load context',
                                '7DF||0105': 'Broad warm-up/thermal context'},
            'evidence_policy': 'Captured response is support evidence, not semantic resolution. Existing data informs analysis and reduces needless repetition without excluding unresolved candidates.',
            'groups': groups}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--check', action='store_true')
    args = p.parse_args()
    value = plan()
    path = RESEARCH / 'discovery-plan.json'
    content = json.dumps(value, indent=2) + '\n'
    if args.check:
        if path.read_text() != content:
            raise SystemExit('Discovery plan differs from reviewed family mapping')
    else:
        path.write_text(content)
    print(json.dumps({'groups': len(value['groups']), 'candidates': sum(len(g['candidate_keys']) for g in value['groups']), 'mode': 'checked' if args.check else 'planned'}))


if __name__ == '__main__':
    main()
