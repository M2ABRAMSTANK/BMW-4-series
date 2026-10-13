#!/usr/bin/env python3
"""List manual BMW testing groups or estimate a combined selection's shared budget.

Read-only: selection happens in the app. No group is hidden or activated here.
"""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def command_key(command):
    return '|'.join((command['hdr'], command.get('eax', ''),
                     ''.join(k + v for k, v in command['cmd'].items())))


def estimate(manifest, selected, *, extra_keys=(), background_count=0):
    """Count shared requests once; background_count is additional unique requests.

    Byte views and signal count do not consume separate requests. Additional
    app reads must be supplied explicitly; the helper cannot inspect the app.
    """
    if not isinstance(background_count, int) or background_count < 0:
        raise ValueError('Background request count must be a nonnegative integer')
    groups = {g['id']: g for g in manifest['groups']}
    unknown = set(selected) - groups.keys()
    if unknown:
        raise ValueError('Unknown testing groups: ' + ', '.join(sorted(unknown)))
    keys = set(extra_keys)
    for identifier in selected:
        group = groups[identifier]
        keys.update(m['key'] for m in group['commands'])
        keys.update(group['reference_command_keys'])
    count = len(keys) + background_count
    if not count:
        raise ValueError('Select at least one request')
    budget = manifest['testing_budget_requests_per_minute']
    if budget <= 0:
        raise ValueError('Request budget must be positive')
    return {'unique_requests': count, 'known_request_keys': sorted(keys),
            'additional_background_requests': background_count,
            'requests_per_minute_total': budget,
            'estimated_hz_per_request': budget / count / 60,
            'estimated_seconds_per_request': count * 60 / budget}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('groups', nargs='*', help='Groups selected together, e.g. TG0.1 TG16.1')
    parser.add_argument('--extra', action='append', default=[], metavar='COMMAND_KEY',
                        help='Additional selected command key; repeats/overlap count once')
    parser.add_argument('--background-count', type=int, default=0,
                        help='Additional distinct app requests not already named in the selection')
    args = parser.parse_args()
    manifest = json.loads((ROOT / 'tests/research/staging-groups.json').read_text())
    try:
        if args.groups or args.extra:
            result = estimate(manifest, args.groups, extra_keys=args.extra,
                              background_count=args.background_count)
            print(json.dumps(result, indent=2))
        else:
            for group in manifest['groups']:
                result = estimate(manifest, [group['id']], background_count=args.background_count)
                print(f'{group["id"]}: {len(group["commands"])} candidates; '
                      f'{result["unique_requests"]} total unique requests including references/background; '
                      f'{result["estimated_hz_per_request"]:.3f} Hz each '
                      f'({result["estimated_seconds_per_request"]:.3f} s)')
    except ValueError as error:
        parser.error(str(error))


if __name__ == '__main__':
    main()
