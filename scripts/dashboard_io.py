"""Small, explicit boundary between private evidence and the public dashboard."""
import datetime as dt
import hashlib
import json
import math
import os
from pathlib import Path
import re
import tempfile


def utcnow():
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds')


def unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('duplicate JSON field')
        result[key] = value
    return result


def read_json(path, limit=2_000_000):
    with open(path, 'rb') as handle:
        raw = handle.read(limit + 1)
    if len(raw) > limit:
        raise ValueError('JSON size limit')
    return json.loads(raw, object_pairs_hook=unique_pairs,
                      parse_constant=lambda value: (_ for _ in ()).throw(ValueError('nonfinite JSON')))


def digest(path):
    result = hashlib.sha256()
    with open(path, 'rb') as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b''):
            result.update(chunk)
    return result.hexdigest()


def within(path, root):
    path, root = Path(path).resolve(), Path(root).resolve()
    if path == root or not path.is_relative_to(root):
        raise ValueError('path outside registered evidence root')
    return path


def number(value, low=0, high=1e9, integer=False):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError('invalid numeric evidence')
    if not low <= value <= high or (integer and value != int(value)):
        raise ValueError('numeric evidence outside bounds')
    return int(value) if integer else value


def identifier(value):
    if not isinstance(value, str) or not re.fullmatch(r'V[0-9]{1,4}(?:-R[0-9]{1,3})?', value):
        raise ValueError('unregistered public identifier')
    return value


def sha(value):
    if not isinstance(value, str) or not re.fullmatch(r'[a-f0-9]{64}', value):
        raise ValueError('invalid evidence digest')
    return value


def atomic_json(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False) + '\n'
    fd, temporary = tempfile.mkstemp(prefix='.' + path.name, dir=path.parent)
    try:
        with os.fdopen(fd, 'w') as handle:
            handle.write(raw)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


# The publisher rejects any snapshot key not explicitly admitted here. Raw receipts,
# paths, prompts and model replies cannot be passed through by the collector.
PUBLIC_FIELDS = {
    'root': {'schema', 'sampled_at_utc', 'published_at_utc', 'source_updated_at_utc',
             'collector', 'counts', 'latest', 'active_runs', 'gpus', 'tasks',
             'evidence_notes', 'history', 'next_steps'},
    'collector': {'state'},
    'counts': {'native_astra_episodes', 'qualified_demonstrations', 'policy_training_runs'},
    'latest': {'id', 'duration_s', 'committed_stages', 'planned_stages', 'stages',
               'delivery_manifest_sha256', 'completion_receipt_sha256', 'timing_anchors',
               'native_wall_s', 'gpu_hours_upper_bound', 'native_model_tokens',
               'second_cycle_target_count', 'full_second_cycle', 'scientific_admission',
               'training_admitted', 'benchmark_complete', 'conference_ready'},
    'stage': {'label', 'duration_s', 'committed'},
    'anchor': {'label', 'short_label', 'error_interval_s'},
    'run': {'id', 'state', 'stages', 'committed_stages', 'planned_stages'},
    'gpu': {'index', 'name', 'utilization_percent', 'memory_used_mib',
            'memory_total_mib', 'temperature_c', 'sampled_at_utc'},
    'task': {'id', 'code', 'title', 'state', 'summary', 'notice', 'metrics',
             'collection', 'engineering', 'scientific', 'next'},
    'metric': {'label', 'value'},
    'history': {'date', 'title', 'detail'},
}


def fields(obj, kind):
    required=PUBLIC_FIELDS[kind];optional={'outcome'} if kind=='stage' else set()
    if not isinstance(obj, dict) or not required.issubset(obj) or set(obj)-required-optional:
        raise ValueError('unexpected or missing public fields: ' + kind)


def validate_public(data):
    fields(data, 'root')
    if data['schema'] != 'chemrmbench-live-dashboard-v1':
        raise ValueError('unsupported dashboard schema')
    fields(data['collector'], 'collector')
    if data['collector']['state'] not in ('healthy', 'degraded'):
        raise ValueError('unknown collector state')
    fields(data['counts'], 'counts')
    for key, val in data['counts'].items():
        number(val, integer=True)
    # This collector is development-only. Scientific admission needs a separately
    # reviewed exporter; refreshing a web page must never grant admission.
    if data['counts']['qualified_demonstrations'] or data['counts']['policy_training_runs']:
        raise ValueError('development exporter cannot admit formal data or training')
    fields(data['latest'], 'latest')
    latest = data['latest']
    identifier(latest['id'])
    for key in ('delivery_manifest_sha256', 'completion_receipt_sha256'):
        sha(latest[key])
    for key in ('scientific_admission', 'training_admitted', 'benchmark_complete', 'conference_ready'):
        if latest[key] is not False:
            raise ValueError('development gate cannot become true')
    for key in ('duration_s', 'committed_stages', 'planned_stages', 'native_wall_s',
                'gpu_hours_upper_bound', 'native_model_tokens', 'second_cycle_target_count'):
        number(latest[key])
    if type(latest['full_second_cycle']) is not bool:
        raise ValueError('invalid cycle flag')
    if not 0 <= latest['committed_stages'] <= latest['planned_stages'] <= 32:
        raise ValueError('invalid stage counts')
    if len(latest['stages']) != latest['planned_stages']:
        raise ValueError('stage count mismatch')
    if sum(s['committed'] is True for s in latest['stages']) != latest['committed_stages']:
        raise ValueError('committed count mismatch')
    for group in (latest['stages'], *[r['stages'] for r in data['active_runs']]):
        for stage in group:
            fields(stage, 'stage')
            number(stage['duration_s'], high=3600)
            if type(stage['committed']) is not bool:
                raise ValueError('invalid stage flag')
            if 'outcome' in stage:
                if stage['outcome'] not in ('pending','native_pass','native_failed'):
                    raise ValueError('unknown native outcome')
                if (stage['outcome']=='native_pass') != stage['committed']:
                    raise ValueError('native outcome and recorded success disagree')
    for item in latest['timing_anchors']:
        fields(item, 'anchor')
        bounds = item['error_interval_s']
        if not isinstance(bounds, list) or len(bounds) != 2:
            raise ValueError('invalid event interval')
        for val in bounds:
            number(val, -3600, 3600)
        if bounds[0] > bounds[1]:
            raise ValueError('inverted event interval')
    for run in data['active_runs']:
        fields(run, 'run')
        identifier(run['id'])
        if run['state'] not in ('collecting', 'waiting_resource', 'interrupted', 'awaiting_seal'):
            raise ValueError('unknown live state')
        number(run['planned_stages'], high=32, integer=True)
        number(run['committed_stages'], high=run['planned_stages'], integer=True)
    for gpu in data['gpus']:
        fields(gpu, 'gpu')
        number(gpu['index'], high=16, integer=True)
        number(gpu['utilization_percent'], high=100)
        number(gpu['memory_total_mib'], high=1_000_000)
        number(gpu['memory_used_mib'], high=gpu['memory_total_mib'])
        number(gpu['temperature_c'], high=150)
        if gpu['name'] not in ('RTX 5090', 'PRO 6000', 'NVIDIA GPU'):
            raise ValueError('unrecognized public device name')
    for task in data['tasks']:
        fields(task, 'task')
        for metric in task['metrics']:
            fields(metric, 'metric')
        if task['state'] not in ('development', 'blocked', 'planned'):
            raise ValueError('invalid task state')
    for entry in data['history']:
        fields(entry, 'history')
    for key in ('sampled_at_utc', 'source_updated_at_utc', 'published_at_utc'):
        val = data[key]
        if val is None and key == 'published_at_utc':
            continue
        if dt.datetime.fromisoformat(val).tzinfo is None:
            raise ValueError('timestamp lacks timezone')
    # Defense in depth, after structural minimization. Text is limited and inert.
    def text_boundary(value):
        if isinstance(value, dict):
            for v in value.values():
                text_boundary(v)
        elif isinstance(value, list):
            if len(value) > 64:
                raise ValueError('oversized public list')
            for v in value:
                text_boundary(v)
        elif isinstance(value, str):
            if len(value) > 2000 or re.search(r'(?i)(Bearer\s|ct-[a-f0-9]{20}|znt_[a-f0-9]{20}|/mnt/|/home/|/tmp/|ssh\s|(?:\d{1,3}\.){3}\d{1,3})', value):
                raise ValueError('private text boundary')
        elif value is not None and not isinstance(value, (bool, int, float)):
            raise ValueError('invalid public type')
    text_boundary(data)
    return data
