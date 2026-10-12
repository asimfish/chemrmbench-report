"""Publish ONLY the reviewed public JSON to an unprotected Pages branch.

Credentials stay in Git's existing credential helper. No shell construction,
force push, raw evidence copy, or branch protection changes are performed.
"""
import argparse
import datetime as dt
import fcntl
import json
import os
from pathlib import Path
import subprocess
import urllib.request

from dashboard_io import atomic_json, read_json, utcnow, validate_public


def git(site, *args):
    return subprocess.run(['git', '-C', str(site), *args], capture_output=True,
                          text=True, check=True, timeout=45,
                          env=os.environ | {'GIT_TERMINAL_PROMPT': '0'}).stdout.strip()


def check_remote(site, config):
    owner_repo = config['github_repository']
    if owner_repo != 'asimfish/chemrmbench-report' or config['pages_branch'] != 'main':
        raise ValueError('unreviewed publication target')
    if git(site, 'remote', 'get-url', 'origin') != 'https://github.com/' + owner_repo + '.git':
        raise ValueError('unexpected remote')
    result = subprocess.run(['git', 'credential', 'fill'],
                            input='protocol=https\nhost=github.com\n\n', text=True,
                            capture_output=True, check=True, timeout=10,
                            env=os.environ | {'GIT_TERMINAL_PROMPT': '0'})
    credential = dict(line.split('=', 1) for line in result.stdout.splitlines() if '=' in line)
    request = urllib.request.Request('https://api.github.com/repos/' + owner_repo + '/branches/main',
                                     headers={'Authorization': 'Bearer ' + credential['password'],
                                              'User-Agent': 'ChemRMBench-dashboard',
                                              'Accept': 'application/vnd.github+json'})
    with urllib.request.urlopen(request, timeout=15) as response:
        branch = json.load(response)
    if branch.get('protected') is not False:
        raise ValueError('protected branch; publication withheld')


def publish(config):
    site = Path(config['site_root']).resolve()
    data = validate_public(read_json(config['snapshot_path']))
    age = dt.datetime.now(dt.timezone.utc) - dt.datetime.fromisoformat(data['sampled_at_utc'])
    if not -dt.timedelta(seconds=30) <= age <= dt.timedelta(seconds=180):
        raise ValueError('snapshot stale; do not publish it as new')
    if git(site, 'branch', '--show-current') != config['pages_branch']:
        raise ValueError('publication checkout is not on the Pages branch')
    if git(site, 'status', '--porcelain'):
        raise ValueError('dirty publication checkout; preserve existing work')
    check_remote(site, config)
    git(site, 'fetch', 'origin', config['pages_branch'])
    git(site, 'merge', '--ff-only', 'origin/' + config['pages_branch'])
    data['published_at_utc'] = utcnow()
    target = site / 'data/collection.json'
    atomic_json(target, data)
    git(site, 'add', '--', 'data/collection.json')
    paths = git(site, 'diff', '--cached', '--name-only').splitlines()
    if paths != ['data/collection.json']:
        raise ValueError('unexpected staged publication paths')
    git(site, 'commit', '-m', '[dashboard/chore]: Refresh verified experiment progress')
    git(site, 'push', 'origin', config['pages_branch'])
    receipt = {'published_at_utc': data['published_at_utc'], 'commit': git(site, 'rev-parse', 'HEAD'),
               'snapshot_sampled_at_utc': data['sampled_at_utc'], 'evidence_id': data['latest']['id'],
               'status': 'PUSHED_PAGES_BUILD_PENDING'}
    atomic_json(config['publication_receipt_path'], receipt)
    return receipt


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', required=True)
    args = parser.parse_args()
    config = read_json(args.config)
    with open(config['publication_receipt_path'] + '.lock', 'a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        receipt = publish(config)
    print('public snapshot pushed: ' + receipt['commit'][:12])


if __name__ == '__main__':
    try:
        main()
    except Exception:
        raise SystemExit('publication withheld or failed; inspect private service status')
