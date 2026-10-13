"""Read registered development receipts; emit an allowlisted private staging snapshot.

No simulator, model, training API or SSH is invoked. A private config registers each
closed receipt by digest and live development directory explicitly.
"""
import argparse
import csv
import fcntl
import os
from pathlib import Path
import re
import subprocess

from dashboard_io import (atomic_json, digest, identifier, number, read_json, sha,
                          utcnow, validate_public, within)


def stages(raw):
    root = raw / 'stages'
    header_path = root / 'episode.json'
    header = read_json(header_path)
    if header.get('schema') != 'chemrm-stage-evidence-v1' or 'DEVELOPMENT' not in header.get('provenance', {}).get('scope', ''):
        raise ValueError('only registered development stages may be exported')
    if header.get('training_admitted') is not False or header.get('simulation_restart_supported') is not False:
        raise ValueError('unrecognized stage admission')
    plan = header['plan']
    if not isinstance(plan, list) or not 1 <= len(plan) <= 32:
        raise ValueError('invalid stage plan')
    result, previous_end, gap = [], 0, False
    for i, entry in enumerate(plan):
        sid = entry['id']
        if not re.fullmatch(r'[A-Za-z0-9_]{1,60}', sid):
            raise ValueError('unsafe stage identifier')
        start = number(entry['start_tick'], integer=True)
        end = number(entry['end_tick'], integer=True)
        if start != previous_end or end <= start:
            raise ValueError('noncontiguous stage plan')
        previous_end = end
        marker, manifest = root / sid / 'COMMITTED.json', root / sid / 'manifest.json'
        committed = False
        if marker.exists():
            if gap or digest(within(manifest, raw)) != sha(read_json(within(marker, raw))['manifest_sha256']):
                raise ValueError('invalid committed stage')
            m = read_json(manifest)
            if (m['header_sha256'] != digest(header_path) or m['episode_id'] != header['episode_id'] or
                    m['index'] != i or m['start_tick'] != start or m['end_tick'] != end):
                raise ValueError('stage does not bind to its plan')
            committed = True
        else:
            gap = True
        # Fixed stage ordinal and duration only, never live private event times.
        result.append({'label': '阶段 ' + str(i + 1), 'duration_s': (end - start) / 60,
                       'committed': committed})
    return result


def load_closed(config):
    registration = config['closed_receipt']
    receipt = within(registration['path'], config['experiment_root'])
    if digest(receipt) != sha(registration['sha256']):
        raise ValueError('registered completion receipt changed')
    data = read_json(receipt)
    package = within(data['package'], config['experiment_root'])
    manifest_path = within(package / 'delivery_manifest.json', config['experiment_root'])
    if digest(manifest_path) != sha(data['package_manifest_sha256']):
        raise ValueError('closed package manifest changed')
    manifest = read_json(manifest_path)
    audit_path = package / 'analysis/timing_audit_r1.json'
    if digest(audit_path) != sha(manifest['files']['analysis/timing_audit_r1.json']):
        raise ValueError('timing audit changed')
    audit = read_json(audit_path)
    if data['native_status'] != 'COMPLETE' or data['native_exit_code'] != 0 or data['owned_native_process_present'] is not False:
        raise ValueError('receipt is not a completed development run')
    for key in ('training_admitted', 'benchmark_complete', 'conference_ready', 'calibrated_chemical_AB', 'task_memory_evaluated'):
        if data[key] is not False:
            raise ValueError('unsupported scientific admission')
    actor = data['live_actor']
    resource = data['resource']
    stage_list = stages(package / 'raw/r1')
    anchors = []
    for label, short, scores in [
        ('公开观测时刻 → B 电机事件', '公开时刻 → B', actor['public_capture_current_time_to_motor_event_scores']),
        ('视觉材质更新命令 → B 电机事件', '视觉命令 → B', actor['visual_material_command_to_motor_event_scores']),
        ('实际 A 电机事件 → B 电机事件', 'A 电机事件 → B', audit['effective_motor_gap_scores']),
    ]:
        bounds = scores[0]['error_interval_s']
        if any(s['error_interval_s'] != bounds or s['benchmark_eligible'] is not False for s in scores):
            raise ValueError('inconsistent diagnostic timing intervals')
        anchors.append({'label': label, 'short_label': short, 'error_interval_s': bounds})
    latest = {
        'id': identifier(registration['id']), 'duration_s': number(data['native_duration_s']),
        'committed_stages': sum(s['committed'] for s in stage_list), 'planned_stages': len(stage_list),
        'stages': stage_list, 'delivery_manifest_sha256': data['package_manifest_sha256'],
        'completion_receipt_sha256': digest(receipt), 'timing_anchors': anchors,
        'native_wall_s': number(resource['native_wall_seconds']),
        'gpu_hours_upper_bound': number(resource['upper_bound_allocated_gpu_hours']),
        'native_model_tokens': number(actor['known_billed_tokens'], integer=True),
        'second_cycle_target_count': number(actor['second_cycle_command_count'], integer=True),
        'full_second_cycle': actor['second_cycle_full70targets'],
        'scientific_admission': False, 'training_admitted': False,
        'benchmark_complete': False, 'conference_ready': False,
    }
    counts = {'native_astra_episodes': number(data['physical_parent_episodes'], integer=True),
              'qualified_demonstrations': 0, 'policy_training_runs': 0}
    # Closed evidence only. These details must not be read from a live pilot.
    notes = [
        '一个连续开发父试次；8 个固定采集阶段不是 8 次独立实验。',
        f"保存 {number(data['actual_states'], integer=True)} 个状态、{number(data['RGBD'], integer=True)} 帧 RGBD、{number(data['liquid_snapshots'], integer=True)} 组液体快照。",
        'Astra 在新图像上给出未来动作提案，执行器实际采用；第一段动作由脚本执行。',
        '模型通过 CLI 显式选择 gpt-6-astra；后端未暴露实际模型版本标识。',
        '只登记接收器 2 的一个技能；不构成五路任务识别、多任务学习或 M1 事件记忆证据。',
        f"第二段动作发送 {latest['second_cycle_target_count']} 个目标；固定采集时长截断了最后保持。",
        f"终态杯外液体代理点 {number(audit['final_allsource_cup_exterior_points'], integer=True)} 个，不能称为零泄漏或标定剂量。",
        f"{number(data['cold_engineering_checks'], integer=True)} 项封存工程检查、{number(data['unit_contract_tests'], integer=True)} 项契约测试、{number(data['terminal_checks'], integer=True)} 项交付检查；非独立科学评审。",
        '阶段保存保留可观察证据，PhysX/PBD 物理状态恢复和快照原子性尚未建立。',
        '未标定独立化学 A/B、剂量、真实事件与视觉提示延迟；科学、训练、benchmark 和会议准入保持未通过。',
    ]
    return latest, counts, notes, data['created_at_utc']


def live_runs(config):
    result = []
    for registration in config.get('live_runs', []):
        raw = within(registration['path'], config['pilot_root'])
        if not raw.exists() or not (raw / 'stages/episode.json').exists():
            continue
        if (raw / 'manifest.json').exists() and read_json(raw / 'manifest.json').get('status') == 'COMPLETE':
            continue
        stage_list = stages(raw)
        start = read_json(raw / 'start.json')
        pid = number(start['pid'], integer=True)
        alive = False
        try:
            # PID identity is checked privately; no PID or command line is exported.
            command = Path(f'/proc/{pid}/cmdline').read_bytes().replace(b'\0', b' ')
            alive = str(raw).encode() in command
        except (OSError, ValueError):
            pass
        complete = all(s['committed'] for s in stage_list)
        result.append({'id': identifier(registration['id']),
                       'state': 'collecting' if alive else 'awaiting_seal' if complete else 'interrupted',
                       'stages': stage_list, 'committed_stages': sum(s['committed'] for s in stage_list),
                       'planned_stages': len(stage_list)})
    for registration in config.get('development_checks', []):
        raw = within(registration['path'], config['experiment_root'])
        parent_running = raw / 'parent_running.json'
        if not parent_running.exists():
            continue
        stage_list = []
        alive = False
        for phase in ('parent', 'child'):
            receipt = raw / (phase + '_running.json')
            resource = raw / (phase + '_resource.json')
            result_path = raw / phase / 'RESULT.json'
            if receipt.exists() and not resource.exists():
                pid = number(read_json(receipt)['pid'], integer=True)
                try:
                    command = Path(f'/proc/{pid}/cmdline').read_bytes().replace(b'\0', b' ')
                    alive |= str(raw).encode() in command
                except OSError:
                    pass
            stage_list.append({'label': '同进程核验' if phase == 'parent' else '新进程核验',
                               'duration_s': 0.0, 'committed': result_path.exists()})
        if alive:
            result.append({'id': identifier(registration['id']), 'state': 'collecting',
                           'stages': stage_list, 'committed_stages': sum(s['committed'] for s in stage_list),
                           'planned_stages': 2})
    return result


def gpu_sample(config, now):
    env = os.environ.copy()
    override = config.get('gpu_environment', {})
    if set(override) - {'LD_LIBRARY_PATH', 'LD_PRELOAD'}:
        raise ValueError('unrecognized telemetry environment')
    env.update(override)
    query = ['nvidia-smi', '--query-gpu=index,name,utilization.gpu,memory.used,memory.total,temperature.gpu',
             '--format=csv,noheader,nounits']
    response = subprocess.run(query, capture_output=True, text=True, timeout=5, env=env, check=True)
    result = []
    for row in csv.reader(response.stdout.splitlines()):
        if len(row) != 6:
            raise ValueError('invalid GPU telemetry')
        name = 'RTX 5090' if '5090' in row[1] else 'PRO 6000' if 'PRO 6000' in row[1] else 'NVIDIA GPU'
        result.append(dict(index=number(int(row[0]), high=16), name=name,
                           utilization_percent=number(float(row[2]), high=100),
                           memory_used_mib=number(float(row[3]), high=1_000_000),
                           memory_total_mib=number(float(row[4]), high=1_000_000),
                           temperature_c=number(float(row[5]), high=150), sampled_at_utc=now))
    return result


def worklines(latest):
    def task(tid, code, title, state, summary, notice, metrics, collection, engineering, scientific, next_step):
        return dict(id=tid, code=code, title=title, state=state, summary=summary, notice=notice,
                    metrics=[dict(label=k, value=v) for k, v in metrics], collection=collection,
                    engineering=engineering, scientific=scientific, next=next_step)
    return [
        task('c13', 'C13 · 操作计时', 'Astra 闭环操作计时', 'development',
             '新图像驱动未来动作提案，在同一条原生轨迹中执行并保留结果。',
             '当前是持续 LED 提示的电机代理。对公开时刻的误差通过 ±20 ms 诊断，但真实 A→B 电机事件仍晚于 ±100 ms，不能据此声称化学时间精确。',
             [('父试次', 1), ('状态', 2220), ('RGBD', 163), ('液体快照', 1230)],
             '1 条开发轨迹', '限定工程交付通过', 'BLOCKED · 化学标定缺失', '补完整第二段动作与事件标定'),
        task('stages', 'DATA · 长任务', '长任务分步保存', 'development',
             '将长试次分成固定采集时间段，逐段提交证据并绑定同一个父试次。',
             '保存完整性已验证；历史刚体适配器已有局部恢复证据并已接入。全场景、冷启动、长链和液体恢复未验收；详见场景与重建页。',
             [('阶段', f"{latest['committed_stages']} / {latest['planned_stages']}"), ('父试次', 1), ('物理恢复', '局部通过'), ('训练准入', 0)],
             '8 段已保存', '提交核验 + 历史局部恢复', '开发数据 · 不计正式样本', '先验全实体恢复与续采，再延长动作终态'),
        task('memory', 'M1 · 事件记忆', '短暂提示与事件记忆', 'planned',
             '提示消失后仍需记住接收器身份和事件时间，并执行对应操作。',
             '持续提示 M0 不能证明 M1。尚无随机起始、五路技能或遮挡后的记忆试验。',
             [('M1 样本', 0), ('正式专家', '0 / 700'), ('任务识别', '未测'), ('上下文消融', '未测')],
             '未采集', '任务协议已设计', '未验收', '先建立可执行五路技能和独立事件'),
        task('calibration', 'CAL · 物理标定', '化学事件、剂量与泄漏', 'blocked',
             '区分命令、视觉提示、实际运动与化学事件；再检验时间准确性和过程安全。',
             '杯外代理点不等于标定泄漏体积。当前没有独立试剂 A/B、传感器事件标定或外部校准。',
             [('杯外点', 123), ('标定单元', '0 / 18'), ('硬件协议', '0 / 200'), ('化学 A/B', '未建立')],
             '保留失败与原始证据', '计时区间已分开', 'BLOCKED', '对齐真实事件、视觉延迟和剂量'),
        task('learning', 'POLICY · 经验吸收', '多任务策略与训练', 'planned',
             '验证数据准入后，再推进初始策略、失败与恢复经验学习，以及学生状态上的蒸馏。',
             '不以开发电机代理直接训练。当前没有策略拟合、正式多任务结果或云端训练任务。',
             [('VLA 拟合', '0 / 15'), ('策略训练', 0), ('云任务', 0), ('会议准入', '未通过')],
             '0 条合格训练数据', '训练契约待接入', '未验收', '先补齐可验证数据与对照实验'),
    ]


def collect(config):
    latest, counts, notes, source_time = load_closed(config)
    now = utcnow()
    state = 'healthy'
    try:
        gpus = gpu_sample(config, now)
    except (OSError, ValueError, subprocess.SubprocessError):
        gpus, state = [], 'degraded'
    try:
        active = live_runs(config)
    except (OSError, ValueError, KeyError):
        active, state = [], 'degraded'
    data = dict(schema='chemrmbench-live-dashboard-v1', sampled_at_utc=now,
                published_at_utc=None, source_updated_at_utc=source_time,
                collector={'state': state}, counts=counts, latest=latest,
                active_runs=active, gpus=gpus, tasks=worklines(latest), evidence_notes=notes,
                history=[
                    {'date': '2026-10-13', 'title': '持续进度页与自动更新', 'detail': '接入白名单导出、分阶段进度和共享 GPU 遥测；网页时间戳区分研究结果、采样与发布。'},
                    {'date': '2026-10-12', 'title': 'V75 · 第一条实时 Astra 闭环开发采集封存', 'detail': '37 秒原生轨迹、8 段保存；保留 69/70 目标截断、杯外点和计时起点差异。正式准入仍未通过。'},
                    {'date': '2026-10-12', 'title': 'V74 · 分阶段长任务诊断', 'detail': '建立按阶段保留状态、图像、液体和边界证据的开发采集路径；不授予物理重启能力。'},
                ],
                next_steps=[
                    '在新的版本目录延长采集时长，完整保留模型延迟启动后的 70 个动作目标和保持终态。',
                    '校准真实 A 事件、视觉提示与 B 实际操作之间的延迟；保留区间计分和失败。',
                    '建立独立 A/B 操作、剂量和泄漏验证，再扩展五路技能、随机起始与 M1 短暂提示。',
                    '完成独立验收与匹配对照后，将合格经验送入训练，并更新论文结果与机制图。',
                ])
    return validate_public(data)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', required=True)
    args = parser.parse_args()
    config = read_json(args.config)
    with open(config['snapshot_path'] + '.lock', 'a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        data = collect(config)
        atomic_json(config['snapshot_path'], data)
    print('snapshot exported: ' + data['latest']['id'] + ' / ' + data['collector']['state'])


if __name__ == '__main__':
    try:
        main()
    except Exception:
        # Private filesystem paths and unexpected raw input are not logged.
        raise SystemExit('snapshot export failed; retain the previous snapshot')
