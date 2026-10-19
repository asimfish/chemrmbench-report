"""Public task-library projection: selected statistics, never raw task truth."""
from collections import Counter
from datetime import datetime, timezone
import json
from pathlib import Path
import re

ROOT=Path('/mnt/nas/data/lyf/chem_mem/paperA-experiments/chemrmbench_v0_1_20261019')
CATALOG=[
 ('T2','bottle_balance','瓶子 → 天平 → 返回','M0 / T0 · 八阶段长任务'),
 ('T1','pick_place','烧杯抓取与放置','M0 / T0 · 基础物理对照'),
 ('T4','press','提示后按压','T-dl · 3 秒响应窗口'),
 ('T6','timed_stirring','按钮启停搅拌','T-dur · 4 / 8 / 12 秒'),
 ('T7','endpoint_stop','颜色端点停止','T-event · 零超量、5 秒内完成'),
 ('T8','delayed_cue_memory','延迟线索选瓶','M1 · 3 / 10 / 20 秒延迟'),
 ('T3','pour','限时倾倒','T-dur · 2 / 4 / 6 秒；工程级'),
 ('T5','open_cabinet','开启铰接装置','M0 / T0 · ≥70% 行程、保持0.5秒'),
]


def read(path, default=None):
    try:return json.loads(path.read_text())
    except (OSError,ValueError):return default


def collect_task_library():
    ids={t[1] for t in CATALOG};records={t:[] for t in ids};active=set()
    memory_gates=read(ROOT/'T8_MEMORY_GATES.json',{})
    for path in sorted(ROOT.glob('*/manifest.jsonl')):
        config=read(path.parent/'collection.json',{})
        if config.get('backend')!='isaac' or config.get('collection_kind')=='view':continue
        rows=[]
        for line in path.read_text().splitlines():
            try:rows.append(json.loads(line))
            except ValueError:continue  # In-progress append; retain complete rows.
        if (config.get('collection_status')!='stopped_after_current_episodes' and
                len(rows)<len(config.get('tasks',[]))*config.get('episodes_per_task',0)):
            active.update(set(config.get('tasks',[]))&ids)
        for row in rows:
            if row.get('task_id') not in ids or row.get('variant')=='replay_zero':continue
            episode=Path(row['directory']);verdict=read(episode/'verdict.json',{})
            metadata=read(episode/'task.json',{})
            purpose=row.get('collection_purpose',metadata.get('collection_purpose'))
            metrics=verdict.get('metrics',{})
            records[row['task_id']].append({
                'seed':row['seed'],'variant':row.get('variant'),
                'dataset':row.get('variant')=='default' and config.get('collection_kind')!='expert_calibration',
                'calibration':config.get('collection_kind')=='expert_calibration',
                'memory_gate':purpose=='memory_leak_gate',
                'diagnostic_prefix':config.get('max_steps')==1,
                'status':row['status'],'safe_success':verdict.get('safe_success') is True,
                'wall_time_s':round(row['wall_time_s'],2),
                'placement_error_mm':round(metrics['placement_error_m']*1000,3)
                    if metrics.get('placement_error_m') is not None else None,
                'return_error_mm':round(metrics['return_error_m']*1000,3)
                    if metrics.get('return_error_m') is not None else None,
                'stage_count':metrics.get('stage_count'),
                'recording_verified':read(episode/'acceptance.json',{}).get('passed') is True,
                'failure_reasons':[v for v in row.get('failure_reasons',[])
                    if re.fullmatch('[a-z_]{1,60}',v)],
                'visual_contrast_flag':read(episode.parent.parent/'visual_review.json',{}).get('status') in {
                    'LOW_CONTRAST','VISUAL_UNACCEPTED','TARGET_NOT_VISIBLE'},
            })
    tasks=[]
    for number,task_id,title,dimension in CATALOG:
        all_rows=records[task_id];rows=[r for r in all_rows if r['dataset']]
        calibration=[r for r in all_rows if r['calibration']]
        successes=sum(r['status']=='success' for r in rows)
        n=len(rows);unique=len({r['seed'] for r in rows})
        qualified=any(r['safe_success'] and not r['visual_contrast_flag'] and not r['diagnostic_prefix'] for r in all_rows)
        state=('needs_expert_fix' if n and successes/n<.8 else
               'batch_collected' if unique>=20 else 'collecting' if task_id in active else
               'needs_expert_fix' if calibration and not n else
               'smoke_passed' if qualified else 'planned')
        tasks.append({'number':number,'id':task_id,'title':title,'dimension':dimension,
            'status':state,'dataset_attempts':n,'dataset_unique_seeds':unique,'target_unique_seeds':20,
            'successes':successes,'success_rate':successes/n if n else None,
            'status_counts':dict(Counter(r['status'] for r in rows)),
            'verified_dataset_attempts':sum(r['recording_verified'] for r in rows),
            'qualification_attempts':sum(not r['dataset'] and not r['diagnostic_prefix'] and not r['calibration'] and not r['memory_gate'] for r in all_rows),
            'qualification_safe_successes':sum(r['safe_success'] for r in all_rows if not r['dataset'] and not r['diagnostic_prefix'] and not r['calibration'] and not r['memory_gate']),
            'calibration_attempts':len(calibration),
            'calibration_status_counts':dict(Counter(r['status'] for r in calibration)),
            'calibration_trials':calibration,
            'memory_gate_attempts':sum(r['memory_gate'] for r in all_rows),
            'memory_layout_gates_passed':sum(r.get('passed') is True for r in memory_gates.get('layouts',[])) if number=='T8' else None,
            'render_diagnostic_attempts':sum(r['diagnostic_prefix'] for r in all_rows),
            'failure_reasons':dict(Counter(v for r in rows for v in r['failure_reasons'])),
            'trials':rows,'engineering_only':number in {'T3','T6','T7'}})
    return {'schema_version':'chemrmbench-task-library-0.1',
            'updated_at_utc':datetime.now(timezone.utc).isoformat(),
            'tasks':tasks,'native_tasks_with_dataset':sum(t['dataset_attempts']>0 for t in tasks),
            'dataset_attempts':sum(t['dataset_attempts'] for t in tasks),
            'calibration_attempts':sum(t['calibration_attempts'] for t in tasks),
            'benchmark_complete':False,'conference_ready':False,
            'scope':'Native scripted expert development. M1, calibrated chemistry and model comparisons are pending.',
            'cold_restore_boundaries':{'verified':1,'total':8}}
