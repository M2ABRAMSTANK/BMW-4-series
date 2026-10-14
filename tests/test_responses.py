import copy
import json
import glob
import os
import pytest
from pathlib import Path

# These will be imported from the schemas repository
from schemas.python.json_formatter import format_file
from schemas.python.overlapping_signals import check_overlapping_signals
from schemas.python.signals_testing import find_test_yaml_files, register_test_classes

REPO_ROOT = Path(__file__).parent.parent.absolute()
TEST_CASES_DIR = os.path.join(Path(__file__).parent, 'test_cases')

# Find all test files grouped by model year
test_files_by_year = find_test_yaml_files(TEST_CASES_DIR)

# Register test classes dynamically
register_test_classes(test_files_by_year)

def get_json_files():
    """Get all JSON files from the signalsets/v3 directory."""
    signalsets_path = os.path.join(REPO_ROOT, 'signalsets', 'v3')
    json_files = glob.glob(os.path.join(signalsets_path, '*.json'))
    # Convert full paths to relative filenames
    return [os.path.basename(f) for f in json_files]

@pytest.mark.parametrize("test_file",
    get_json_files(),
    ids=lambda x: x.split('.')[0].replace('-', '_')  # Create readable test IDs
)
def test_formatting(test_file):
    """Test signal set formatting for all vehicle models in signalsets/v3/."""
    signalset_path = os.path.join(REPO_ROOT, 'signalsets', 'v3', test_file)

    # TG references intentionally decode the same bytes in multiple folders.
    # Permit only the exact same-command aliases recorded in the manifest;
    # continue checking all original signals for unintended overlaps.
    formatted, _ = format_file(signalset_path, return_overlaps=True)
    data = json.loads(formatted)
    manifest_path = REPO_ROOT / 'tests/research/staging-groups.json'
    manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {'groups': []}
    expected = {alias: (source, group['path']) for group in manifest['groups']
                for alias, source in group.get('reference_signal_aliases', {}).items()}
    seen = set()
    original = copy.deepcopy(data)
    for command in original['commands']:
        sources = {s['id']: s for s in command['signals'] if s['id'] not in expected}
        retained = []
        for signal in command['signals']:
            if signal['id'] in expected:
                source_id, path = expected[signal['id']]
                source = sources[source_id]  # Must share the same request.
                assert signal['fmt'] == source['fmt']
                assert signal['path'] == path
                assert not signal.get('hidden', False)
                assert signal['id'] not in seen
                seen.add(signal['id'])
            else:
                assert not signal['id'].startswith('BMW_TEST_REF_')
                retained.append(signal)
        command['signals'] = retained
    if test_file == 'default.json':
        assert seen == set(expected)
    check_overlapping_signals(json.dumps(original))

    with open(signalset_path) as f:
        assert f.read() == formatted

if __name__ == '__main__':
    # Use pytest's main function with xdist arguments
    pytest.main([__file__, '-xvs', '-n', 'auto'])
