"""Public task-library projection: selected statistics, never raw task truth."""
from collections import Counter
from datetime import datetime, timezone
import json
from pathlib import Path
import re

ROOT=Path('/mnt/nas/data/lyf/chem_mem/paperA-experiments/chemrmbench_v0_1_20261019')
SSD=Path.home()/'.local/share/chemrm-collections/guidance7'
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


def particle_runtime_supported(row,episode):
    if row['task_id']!='pour':return None
    report=read(episode/'privileged/particle_runtime.json')
    if report is not None:
        return report.get('supported') is True and report.get('unsupported_messages')==[]
    # Older raw verdicts predate runtime admission. Export only a boolean,
    # never the private log, asset paths, hidden cues or arbitrary messages.
    try:
        log=Path(row['worker_log']).resolve()
        if not log.is_relative_to(ROOT.resolve()) or not log.is_file() or log.stat().st_size>8*1024**2:return None
        text=log.read_text(errors='replace')
    except (OSError,KeyError):return None
    return not any(marker in text for marker in (
        'failed to cook GPU-compatible mesh','Non-GPU-compatible convex mesh'))


def primary_pour_cohort():
    report=read(ROOT/'T3_BATCH_REPORT.json',{})
    counts=[report.get(k) for k in ('successes','failures','errors')]
    if (report.get('seeds')!=list(range(20)) or
            any(type(v) is not int or not 0<=v<=20 for v in counts) or sum(counts)!=20):return None
    return {'attempts':20,'successes':counts[0],'failures':counts[1],'errors':counts[2],
            'recording_accepted':report.get('acceptance_passed') is True,
            'runtime_supported':type(report.get('unsupported_gpu_geometry_warning_count')) is int
                and report['unsupported_gpu_geometry_warning_count']==0,
            'expert_threshold_passed':counts[0]>=16}


def evaluation_projection():
    """Counts only: never export split assignments, calibration or raw results."""
    mt={'press','timed_stirring','endpoint_stop','delayed_cue_memory','pour'}
    f0=read(ROOT/'step6_f0_paused/metrics.json',{})
    cpu=[]
    for task in sorted(mt):
        entry={'task_id':task}
        for policy in ['privileged_expert','ablation','public_heuristic']:
            metrics=f0.get('policies',{}).get(policy,{}).get('tasks',{}).get(task,{})
            attempts=metrics.get('attempts');successes=metrics.get('successes')
            if type(attempts) is int and type(successes) is int and 0<=successes<=attempts<=50:
                entry[policy]={'attempts':attempts,'successes':successes}
        cpu.append(entry)
    native=[]
    for label,task in [('t4','press'),('t7','endpoint_stop'),('t8','delayed_cue_memory'),('t3','pour'),('t6','timed_stirring')]:
        for mode in ['paused','latency_charged']:
            root=ROOT/('step6_native_'+label+'_'+mode);config=read(root/'collection.json',{})
            path=root/'manifest.jsonl'
            if config.get('collection_kind')!='heldout_evaluation' or not path.exists():continue
            rows=[]
            for line in path.read_text().splitlines():
                try:row=json.loads(line)
                except ValueError:continue
                if (row.get('task_id')==task and type(row.get('seed')) is int and 1000<=row['seed']<=1049
                    and row.get('expert_kind')=='evaluation_public_heuristic'
                    and row.get('status') in {'success','fail','error'}):rows.append(row)
            native.append({'task_id':task,'clock_mode':mode,'attempts':len(rows),
                'successes':sum(r['status']=='success' for r in rows),
                'status_counts':dict(Counter(r['status'] for r in rows)),
                'task_revision':'T4-v1' if task=='press' else None,
                'superseded':task=='press',
                'recording_accepted':read(root/'dataset_acceptance.json',{}).get('acceptance_passed') is True})
    return {'seeds_per_task':50,'seed_range':[1000,1049],
        'clock_modes':['paused','latency_charged'],'f0_cpu_contracts':cpu,'native_public_observation':native,
        'scope':'F0 schematic RGB/clock contracts are separate from native physical solvability; learned model results remain separate; T1 pipeline pilot is not a baseline.'}


def pipeline_projection():
    budget=read(ROOT/'TRAINING_BUDGET.json',{})
    receipt=read(ROOT/'pilot20_r2_checkpoint/run_receipt.json',{})
    cpu=read(ROOT/'pilot20_r2_checkpoint/CPU_INFERENCE_RECEIPT.json',{})
    report=read(ROOT/'GUIDANCE6_ACTION_PILOT_REPORT.json',{})
    attempts=budget.get('native_action_pilot_attempts',[])
    return {'scope':'pipeline_validation_only','report_as_baseline':False,
        'checkpoint_saved':receipt.get('status')=='checkpoint_written',
        'training_updates':receipt.get('global_steps',0),
        'training_gpu_hours':sum(j.get('actual_gpu_hours_upper_bound',j.get('receipt',{}).get('gpu_hours_upper_bound',0.)) for j in budget.get('jobs',[])),
        'cpu_public_inference_passed':cpu.get('inference_passed') is True,
        'native_action_attempts':len(attempts),'native_action_required':10,
        'native_action_status_counts':dict(Counter(a['status'] for a in attempts)),
        'pipeline_complete':report.get('pipeline_complete') is True}


def t6_qualification_projection():
    approval=read(ROOT/'T6_LOCAL_PANEL_CONTACT_DECISION.json',{})
    screen=read(ROOT/'t6_guidance6_approved_panel_preflight/preflight.json',{})
    report=read(ROOT/'T6_GUIDANCE6_QUALIFICATION_REPORT.json',{})
    attempts=report.get('attempts',[])
    forces=[a['raw_global_robot_peak_n'] for a in attempts if a.get('raw_global_robot_peak_n') is not None]
    return {'local_panel_contact_approved':approval.get('approved_by')=='explicit user reply',
        'moving_geometry_scope':'hand_only; arm links are not covered',
        'whole_scene_transit_screen_passed':screen.get('passed') is True,
        'minimum_transit_clearance_mm':min((r['minimum_lower_bound_m']*1000
            for r in screen.get('results',[]) if r.get('passed')),default=None),
        'native_attempts':len(attempts),'native_passed':sum(a['passed'] for a in attempts),
        'native_required':3,'all_native_qualifications_passed':report.get('passed') is True,
        'maximum_raw_global_force_n':max(forces,default=None),'raw_force_limit_n':25}


def current_t6_projection():
    cpu=read(ROOT/'guidance7_t6_joint_path_preflight_cached/preflight.json',{})
    native=read(ROOT/'T6_GUIDANCE7_QUALIFICATION_REPORT.json',{})
    attempts=native.get('attempts',[])
    return {'cpu_passed':cpu.get('passed') is True,'cpu_attempts':len(cpu.get('results',[])),
        'moving_colliders':17,'minimum_clearance_mm':min((r['minimum_lower_bound_m']*1000
            for r in cpu.get('results',[]) if r.get('passed')),default=None),
        'native_attempts':len(attempts),'native_passed':sum(a.get('passed') is True for a in attempts),
        'native_required':3,'native_all_passed':native.get('passed') is True,
        'fixture_moved':False,'raw_force_limit_n':25}


def training_expansion_projection():
    raw=read(ROOT/'remote_training/guidance7_training_expansion/progress.json',{})
    counts=Counter()
    for row in raw.get('by_task_host_status_admission',[]):
        if row.get('task_id') not in {t[1] for t in CATALOG}:continue
        if row.get('status') not in {'success','fail','error'}:continue
        if type(row.get('attempts')) is not int or row['attempts']<0:continue
        counts[(row['task_id'],row['status'],row.get('training_admitted') is True)]+=row['attempts']
    return {'purpose':'training_only','strict_V2_passed':False,'main_table_eligible':False,
        'received_and_validated_attempts':sum(counts.values()),'target_new_attempts':400,
        'admitted_successes':sum(n for (task,status,admitted),n in counts.items() if admitted and status=='success'),
        'by_task_status':[{'task_id':k[0],'status':k[1],'training_admitted':k[2],'attempts':n}
            for k,n in sorted(counts.items())]}


def ssd_projection():
    result=[]
    for name,label in [('t4_v2_twenty_seed','T4-v2 main'),('t4_v2_ablation_ten_seed','T4-v2 ablation'),
        ('step6_native_t7_paused_ssd','T7 public suffix'),('step6_native_t8_paused_ssd','T8 public'),
        ('step6_native_t3_paused_ssd','T3 public')]:
        config=read(SSD/name/'collection.json',{})
        if config.get('backend')!='isaac':continue
        rows=[];p=SSD/name/'manifest.jsonl'
        if p.is_file():
            for line in p.read_text().splitlines():
                try:row=json.loads(line)
                except ValueError:continue
                if row.get('status') in {'success','fail','error'}:rows.append(row)
        result.append({'label':label,'closed_attempts':len(rows),'expected_attempts':config['episodes_per_task'],
            'measured_status_counts':dict(Counter(r['status'] for r in rows)),
            'batch_recording_accepted':read(SSD/name/'dataset_acceptance.json',{}).get('acceptance_passed') is True,
            'NAS_mirror_pending':True})
    return {'scope':'durable SSD staging during NAS write stall; separate from NAS admitted cohort counts',
        'cohorts':result,'T7_retained_valid_successes':3,'T7_case1003_original_receipt_pending':True}


def collect_task_library():
    ids={t[1] for t in CATALOG};records={t:[] for t in ids};active=set()
    memory_gates=read(ROOT/'T8_MEMORY_GATES.json',{})
    for path in sorted(ROOT.glob('*/manifest.jsonl')):
        config=read(path.parent/'collection.json',{})
        if config.get('backend')!='isaac' or config.get('collection_kind') in {'view','recovered_subset_view'}:continue
        rows=[]
        for line in path.read_text().splitlines():
            try:rows.append(json.loads(line))
            except ValueError:continue  # In-progress append; retain complete rows.
        if (config.get('expert_kind','main')=='main' and
                config.get('collection_status') not in {'stopped_after_current_episodes','interrupted_recovered'} and
                len(rows)<len(config.get('tasks',[]))*config.get('episodes_per_task',0)):
            active.update(set(config.get('tasks',[]))&ids)
            if config.get('task_revisions',{}).get('press')!='T4-v2':active.discard('press')
        for row in rows:
            if row.get('task_id') not in ids or row.get('variant')=='replay_zero':continue
            episode=Path(row['directory']);verdict=read(episode/'verdict.json',{})
            metadata=read(episode/'task.json',{})
            purpose=row.get('collection_purpose',metadata.get('collection_purpose'))
            if (row['task_id']=='timed_stirring' and path.parent.name=='t6_guidance4_smoke'):
                purpose='expert_qualification'  # Guidance6: retained old expert, outside new main cohort
            expert_kind=row.get('expert_kind',metadata.get('expert_kind','main'))
            evaluation=purpose=='heldout_evaluation' or config.get('collection_kind')=='heldout_evaluation'
            metrics=verdict.get('metrics',{})
            supported=particle_runtime_supported(row,episode)
            rejected=row['task_id']=='pour' and supported is not True
            records[row['task_id']].append({
                'superseded':row['task_id']=='press' and metadata.get('definition',{}).get('task_revision')!='T4-v2',
                'primary_legacy_press':path.parent.name=='t4_twenty_seed_r2',
                'seed':row['seed'],'variant':row.get('variant'),
                'dataset':row.get('variant')=='default' and config.get('collection_kind')!='expert_calibration' and expert_kind=='main' and not evaluation and purpose!='expert_qualification',
                'evaluation':evaluation,
                'expert_kind':expert_kind,'ablation':expert_kind in {'ablation_no_memory','ablation_no_timing'},
                'calibration':config.get('collection_kind')=='expert_calibration',
                'memory_gate':purpose=='memory_leak_gate',
                'diagnostic_prefix':config.get('max_steps')==1,
                'status':'error' if rejected else row['status'],
                'measured_status':row['status'],'particle_runtime_supported':supported,
                'runtime_rejected':rejected,
                'safe_success':verdict.get('safe_success') is True and not rejected,
                'wall_time_s':round(row['wall_time_s'],2) if row.get('wall_time_s') is not None else None,
                'placement_error_mm':round(metrics['placement_error_m']*1000,3)
                    if metrics.get('placement_error_m') is not None else None,
                'return_error_mm':round(metrics['return_error_m']*1000,3)
                    if metrics.get('return_error_m') is not None else None,
                'stage_count':metrics.get('stage_count'),
                'recording_verified':read(episode/'acceptance.json',{}).get('passed') is True,
                'failure_reasons':[v for v in row.get('failure_reasons',[])
                    if re.fullmatch('[a-z_]{1,60}',v)]+(
                        ['unsupported_particle_geometry' if supported is False else 'particle_runtime_unverified']
                        if rejected else []),
                'visual_contrast_flag':read(episode.parent.parent/'visual_review.json',{}).get('status') in {
                    'LOW_CONTRAST','VISUAL_UNACCEPTED','TARGET_NOT_VISIBLE'},
            })
    tasks=[]
    for number,task_id,title,dimension in CATALOG:
        historical=records[task_id]
        superseded=[r for r in historical if r.get('superseded')]
        all_rows=[r for r in historical if not r.get('superseded')]
        rows=[r for r in all_rows if r['dataset']]
        calibration=[r for r in all_rows if r['calibration']]
        ablations=[r for r in all_rows if r['ablation']]
        evaluation=[r for r in all_rows if r['evaluation']]
        successes=sum(r['status']=='success' for r in rows)
        n=len(rows);unique=len({r['seed'] for r in rows})
        qualified=any(r['safe_success'] and not r['visual_contrast_flag'] and not r['diagnostic_prefix'] for r in all_rows)
        primary=primary_pour_cohort() if task_id=='pour' else None
        if task_id in active:state='collecting'
        elif primary:
            state='batch_collected' if all(primary[k] for k in (
                'recording_accepted','runtime_supported','expert_threshold_passed')) else 'needs_expert_fix'
        else:state=('needs_expert_fix' if n and successes/n<.8 else
               'batch_collected' if unique>=20 else
               'needs_expert_fix' if calibration and not n else
               'smoke_passed' if qualified else 'needs_expert_fix' if all_rows else 'planned')
        tasks.append({'number':number,'id':task_id,'title':title,'dimension':dimension,
            'status':state,'dataset_attempts':n,'dataset_unique_seeds':unique,'target_unique_seeds':20,
            'primary_cohort':primary,
            'task_revision':'T4-v2' if task_id=='press' else None,
            'revision_note':'T4-v2：提示均匀分布于2–17秒，响应窗口3秒；任意固定时刻策略成功率上界3/15=20%。T4-v1设计不合格（固定策略约75%可过），已停用，旧录像和数据保留。' if task_id=='press' else None,
            'superseded_history':{'revision':'T4-v1','main_attempts':sum(r['primary_legacy_press'] for r in superseded),
                'main_successes':sum(r['primary_legacy_press'] and r['status']=='success' for r in superseded),
                'ablation_attempts':sum(r['ablation'] for r in superseded),
                'ablation_successes':sum(r['ablation'] and r['status']=='success' for r in superseded),
                'evaluation_attempts':sum(r['evaluation'] for r in superseded)} if task_id=='press' else None,
            'qualification_gate':t6_qualification_projection() if task_id=='timed_stirring' else None,
            'runtime_rejections':sum(r['runtime_rejected'] for r in all_rows),
            'successes':successes,'success_rate':successes/n if n else None,
            'status_counts':dict(Counter(r['status'] for r in rows)),
            'verified_dataset_attempts':sum(r['recording_verified'] for r in rows),
            'qualification_attempts':sum(not r['dataset'] and not r['diagnostic_prefix'] and not r['calibration'] and not r['memory_gate'] and not r['ablation'] and not r['evaluation'] for r in all_rows),
            'qualification_safe_successes':sum(r['safe_success'] for r in all_rows if not r['dataset'] and not r['diagnostic_prefix'] and not r['calibration'] and not r['memory_gate'] and not r['ablation'] and not r['evaluation']),
            'evaluation_attempts':len(evaluation),'evaluation_successes':sum(r['safe_success'] for r in evaluation),
            'ablation_attempts':len(ablations),'ablation_successes':sum(r['status']=='success' for r in ablations),
            'ablation_status_counts':dict(Counter(r['status'] for r in ablations)),
            'ablation_expert_kinds':sorted({r['expert_kind'] for r in ablations}),
            'ablation_target_attempts':10 if task_id in {'press','timed_stirring','endpoint_stop','delayed_cue_memory','pour'} else None,
            'rendering_note':'烧杯采用不透明磨砂蓝材质（opacity=1.0）；CAD 和质量参数保留。' if task_id=='pick_place' else None,
            'initial_posture_note':'initial_posture: prepress_ready_3mm。从3mm就绪姿态考定时响应，接近与对准由T1/T2/T5覆盖；旧10条校准保留。' if task_id=='press' else
                'initial_posture: prepress_ready_nominal。保留原就绪姿态，各次触压先到3mm间隙；不等同于T4的3mm初始姿态。' if task_id=='endpoint_stop' else None,
            'fixture_note':'搅拌器不带温度探头组件（v0.1固定装置）。原始USD及r1–r4失败保留；完整装配与探头挪移列为v0.2候选。' if task_id=='timed_stirring' else None,
            'observation_note':'受控观测：恒定环境光，评测必须提供站位A相机。腕部相机有14/20条看不到提示，不作为单独的记忆观测设置。' if task_id=='delayed_cue_memory' else None,
            'calibration_attempts':len(calibration),
            'calibration_status_counts':dict(Counter(r['status'] for r in calibration)),
            'calibration_trials':calibration,
            'memory_gate_attempts':sum(r['memory_gate'] for r in all_rows),
            'memory_layout_gates_passed':sum(r.get('passed') is True for r in memory_gates.get('layouts',[])) if number=='T8' else None,
            'observation_profile':memory_gates.get('profile') if number=='T8' else None,
            'render_diagnostic_attempts':sum(r['diagnostic_prefix'] for r in all_rows),
            'failure_reasons':dict(Counter(v for r in rows for v in r['failure_reasons'])),
            'trials':rows,'engineering_only':number in {'T3','T6','T7'}})
    return {'schema_version':'chemrmbench-task-library-0.1',
            'evaluation_protocol':evaluation_projection(),'pipeline_pilot':pipeline_projection(),
            'training_expansion':training_expansion_projection(),'current_t6':current_t6_projection(),
            'ssd_staging':ssd_projection(),
            'updated_at_utc':datetime.now(timezone.utc).isoformat(),
            'tasks':tasks,'native_tasks_with_dataset':sum(t['dataset_attempts']>0 for t in tasks),
            'dataset_attempts':sum(t['dataset_attempts'] for t in tasks),
            'calibration_attempts':sum(t['calibration_attempts'] for t in tasks),
            'benchmark_complete':False,'conference_ready':False,
            'scope':'Native privileged expert development. T8 uses controlled ambient lighting with per-layout pixel controls; agent memory results, chemistry calibration and model comparisons are pending.',
            'cold_restore_boundaries':{'verified':1,'total':8}}
