#!/usr/bin/env python3
"""List or select one 2019 BMW research wave; requires the OBDb schema tooling."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tests' / 'schemas' / 'python'))
from can.signals import Command, Filter
from json_formatter import format_json_data


def command_key(command):
    return '|'.join((command['hdr'], command.get('eax', ''),
                     ''.join(k + v for k, v in command['cmd'].items())))


def select_group(root, selected):
    manifest_path = root / 'tests/research/staging-groups.json'
    manifest = json.loads(manifest_path.read_text())
    if selected != 'none' and selected not in {g['id'] for g in manifest['groups']}:
        raise ValueError(f'Unknown testing group: {selected}')
    for group in manifest['groups']:
        rate = sum(60 / member['interval_seconds'] for member in group['commands'])
        if rate + manifest['background_testing_requests_per_minute'] > manifest['testing_budget_requests_per_minute']:
            raise ValueError(f'Testing group {group["id"]} exceeds the request budget')
    definition_path = root / 'signalsets/v3/default.json'
    data = json.loads(definition_path.read_text())
    definitions = {command_key(c): c for c in data['commands']}
    managed = {m['key'] for g in manifest['groups'] for m in g['commands']}
    background = 0
    for key, definition in definitions.items():
        command = Command.from_json(definition)
        if key in managed or (command.filter and not command.filter.matches(manifest['model_year'])):
            continue
        debug = definition.get('dbg') or ('dbgfilter' in definition and
            Filter.from_json(definition['dbgfilter']).matches(manifest['model_year']))
        if debug:
            background += 60 / definition['freq']
    for group in manifest['groups']:
        rate = sum(60 / member['interval_seconds'] for member in group['commands'])
        if rate + background > manifest['testing_budget_requests_per_minute']:
            raise ValueError(f'Testing group {group["id"]} exceeds the request budget with current background testing')
    manifest['background_testing_requests_per_minute'] = background
    manifest['wave_budget_requests_per_minute'] = manifest['testing_budget_requests_per_minute'] - background
    audit_path = root / 'tests/research/scanlog-audit.json'
    audit = json.loads(audit_path.read_text())
    entries = {e['key']: e for e in audit['entries']}
    for group in manifest['groups']:
        active = group['id'] == selected
        for member in group['commands']:
            command = definitions[member['key']]
            command['filter'] = {'years': [manifest['model_year'] if active else 9999]}
            # Active research uses normal polling so the client can honor freq.
            # Parked waves remain debug-only and excluded by their year filter.
            if active:
                command.pop('dbg', None)
            else:
                command['dbg'] = True
            command.pop('dbgfilter', None)
            command['freq'] = member['interval_seconds']
            entry = entries[member['key']]
            entry['command_id'] = Command.from_json(command).id
            entry['disposition'] = 'active_research_2019' if active else 'parked_testing_wave'
    manifest['active_group'] = None if selected == 'none' else selected
    # Prepare all output before touching any file. Only managed wave definitions change.
    formatted = format_json_data(data)
    metadata = {k: v for k, v in audit.items() if k != 'entries'}
    audit_text = (json.dumps(metadata, indent=2)[:-2] + ',\n  "entries": [\n' +
                  ',\n'.join('    ' + json.dumps(e, separators=(',', ':'))
                             for e in audit['entries']) + '\n  ]\n}\n')
    definition_path.write_text(formatted.rstrip() + '\n')
    manifest_path.write_text(json.dumps(manifest, indent=2) + '\n')
    audit_path.write_text(audit_text)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('group', nargs='?', help='Group to enable, e.g. TG0.2; "none" parks all waves')
    args = parser.parse_args()
    if args.group:
        try:
            select_group(ROOT, args.group)
        except ValueError as error:
            parser.error(str(error))
    manifest = json.loads((ROOT / 'tests/research/staging-groups.json').read_text())
    for group in manifest['groups']:
        marker = '*' if group['id'] == manifest['active_group'] else ' '
        rate = sum(60 / m['interval_seconds'] for m in group['commands'])
        print(f'{marker} {group["id"]}: {len(group["commands"])} commands, {rate:g} requested polls/min')


if __name__ == '__main__':
    main()
