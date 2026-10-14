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
        phases=registration.get('phases',['parent','child'])
        leader=('live_a' if phases==['live_a','live_b'] else
                'live_control' if phases==['live_control','same_process_restore'] else 'parent')
        parent_running = raw / (leader+'_running.json')
        if not parent_running.exists():
            continue
        stage_list = []
        alive = False
        if phases not in (['parent','child'],['parent','no_fault_first'],['live_a','live_b'],['live_control','same_process_restore'],['parent','child_expired','child_retry'],
                          ['parent','child_expired_resource_retry1','child_retry'],
                          ['parent','child_interrupted','child_retry'],
                          ['parent','no_fault_first','recovery_first','recovery_retry','expired_first']):
            raise ValueError('unregistered native phase plan')
        labels={'parent':'父阶段封存','child':'新进程核验','child_expired':'过期提案拒绝',
                'child_expired_resource_retry1':'过期提案拒绝','child_interrupted':'中断失败证据保留',
                'child_retry':'从父检查点单次重试','no_fault_first':'无故障冷续跑对照',
                'recovery_first':'可行中断证据保存','recovery_retry':'保留原期限重试',
                'expired_first':'原期限过期拒绝','live_a':'连续运行基线 A','live_b':'连续运行基线 B',
                'live_control':'不中断物理对照','same_process_restore':'同进程状态恢复对照'}
        matched_paths={'no_fault_first':'branches/no_fault/child_first',
                       'recovery_first':'branches/recovery/child_first',
                       'recovery_retry':'branches/recovery/child_retry',
                       'expired_first':'branches/expired/child_first'}
        for phase in phases:
            receipt = raw / (phase + '_running.json')
            resource = raw / (phase + '_resource.json')
            output = raw / matched_paths.get(phase,'child_expired' if phase=='child_expired_resource_retry1' else phase)
            result_path = output / 'RESULT.json'
            if receipt.exists() and not resource.exists():
                pid = number(read_json(receipt)['pid'], integer=True)
                try:
                    command = Path(f'/proc/{pid}/cmdline').read_bytes().replace(b'\0', b' ')
                    alive |= str(raw).encode() in command
                except OSError:
                    pass
            refused=phase in ('child_expired','child_expired_resource_retry1','child_interrupted') and (raw/'RETRY_GATE.json').exists()
            if phase in ('recovery_first','expired_first') and (output/'task_clock_accounting.json').exists():
                account=read_json(output/'task_clock_accounting.json')
                expected='FAILED' if phase=='recovery_first' else 'REFUSED'
                refused=(account['outcome']==expected and
                         account['phase_callbacks'].get('TAIL_COMMANDS',0)==0 and
                         not (output/'task/agent/dispatch.json').exists())
            stage_list.append({'label': labels[phase],
                               'duration_s': 0.0, 'committed': result_path.exists() or refused})
        if alive:
            result.append({'id': identifier(registration['id']), 'state': 'collecting',
                           'stages': stage_list, 'committed_stages': sum(s['committed'] for s in stage_list),
                           'planned_stages': len(phases)})
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
             'V90 以原抬瓶事件为锚点，首次中断的 2.3875 原生秒及两次重建步全部扣除；重试不重设期限。71 个父文件保持一致，只执行 5,507 步余程。原事件到接触的误差区间 −4.165 至 +4.168 ms。化学、液体及完整长链仍待验收。',
             [('已保留前阶段', '5 段'), ('恢复后执行', '5,507 步'), ('最终放回误差', '0.456 mm'), ('训练准入', 0)],
             '前五段 + 恢复后三段', '刚体原事件期限恢复限定通过', '开发数据 · 不计正式样本', '原期限过期拒绝、匹配对照与独立化学计时'),
        task('memory', 'M1 · 事件记忆', '短暂提示与事件记忆', 'development',
             '提示消失后仍需记住接收器身份和事件时间，并执行对应操作。',
             'V90 首次完成原抬瓶事件到重试接触的期限保持。V89 的临时目录诊断只有两次封存输入调用，无新增物理试次；模型上游环境仍未完全核验。V86 的计时失败保留。正式随机化 M1 与化学计时未验收。',
             [('封存图像读出调用', 7), ('原生试次模型调用', 20), ('原期限恢复案例', 1), ('正式 M1 样本', 0)],
             '封存输入诊断 + 原生计时试次', '原期限限定通过；非配对成功率', '正式 M1 未验收', '随机化事件、等指令记忆干预与时间对照'),
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
                    {'date':'2026-10-14','title':'V95 · 同进程恢复仍有后续姿态失配','detail':'恢复前65实体物理记录与任务游标完全一致；已有进程内167次状态、目标和参数写入不推进积分。65实体×30步保持通过，随后1920步运送终态姿态0.999°超过原0.5°门槛，位置0.466mm低于1mm；启动前封存读出保留失败。126源文件/68连续对照文件不变，2组进程闭合，0调用/0训练/GPU分配上界0.140h。进程重启不是本例失配的必要条件；具体写入或隐藏状态原因未定。保存8/8，中途冷重建仍1/8。'},
                    {'date':'2026-10-14','title':'V94 · 两条连续基线完成，瓶体配对记录一致','detail':'每条连续运行相同固定种子的4560步前缀、30步保持、1920步运送，抬瓶边界不恢复状态。65实体终态和保持对照满足原门槛；1920对瓶体位姿记录一致，终态位置/姿态差0。角度公式微小浮点残差不代表物理漂移。124源文件、67基线A文件保留，启动前封存读出完成原始复核；0调用/0训练/GPU分配上界0.110h。V93姿态失败保留，完整重建仍1/8；同进程恢复对照 V95 已完成，负结果继续保留。'},
                    {'date':'2026-10-14','title':'V93 · 携物短时恢复通过，后续运送姿态失败','detail':'同源抬瓶边界：65实体×30步连续父进程与冷恢复比较通过；随后各运送1920步，双侧接触100%。终态姿态0.999°超过原0.5°门槛，位置0.466mm低于1mm。67父文件不变；0模型调用；GPU分配上界0.136h包含首轮实现失败。保留负结果，重建覆盖仍1/8；下一轮先测连续基线差异，不推断求解器原因。'},
                    {'date':'2026-10-14','title':'V92 · 八阶段完整状态保存验收，重建覆盖仍为一个边界','detail':'8份归档各含65个登记实体、速度与控制目标；源动作游标和宿主步数分开保存，持久化不推进物理。91个父文件不变；1次冷重建只跑5507步余程，原A→B误差−4.165至+4.168ms，放回0.383mm。2次调用/22,398tokens/GPU分配上界0.115h。启动显存拒绝保留，仅补启动子进程，无重采或额外模型调用。保存8/8，重建1/8；携物、液体和完整长链未验收。'},
                    {'date':'2026-10-14','title':'V91 · 同原事件期限的三分支执行器对照','detail':'无故障冷续跑、中断后原期限重试均满足 −4.165 至 +4.168 ms；过期开始窗口在 44.125 s 拒绝，0 余程动作。中断 3.125 原生秒全部计入；71 父文件不变，4 次各 65 实体 ×30 步重建。2 次实际先验调用 /22,400 tokens /GPU 分配上界0.234 h。固定240步交付不是实测模型延迟；8段轨迹证据只含1个已验收完整场景任务检查点。'},
                    {'date':'2026-10-14','title':'V90 · 中断与重建后保持原事件期限','detail':'原抬瓶事件 16.863–16.867 任务秒；接触 46.863–46.867，原目标间隔 30 秒。失败消耗 2.3875 原生秒被完整扣除，两次各 30 步重建均计时。71 个父文件不变、余程 5,507 步、放回误差 0.456 mm；误差 −4.165 至 +4.168 ms。4 次调用 / 44,853 tokens / GPU 分配上界 0.138 h。进程间任务时钟明确暂停，非化学连续钟或记忆因果收益。'},
                    {'date':'2026-10-14','title':'V88/V89 · 时钟下端点修复与调用路径诊断','detail':'修复可以排程与此刻可执行的混淆；22 项 CPU 时钟检查和 5 项临时目录检查通过。V89 两次真实封存输入诊断共 22,390 tokens，无新增物理执行；旧版本路径提示风险仍保留在证据边界中。'},
                    {'date': '2026-10-14', 'title': 'V87 · 过期拒绝与失败子阶段单次重试通过', 'detail': '58 步真实模型调用积分 + 1,440 步声明的交付延迟后拒绝提案，未执行余程。45 个父阶段文件和记忆保持一致；新进程单次重试只执行 5,507 步，接触 10.000–10.004 秒，放回误差 0.406 mm。四次调用 / 44,816 tokens / GPU 分配上界 0.148 h。重试是新尝试，不代表连续化学期限已恢复。'},
                    {'date': '2026-10-14', 'title': 'V86 · 延迟基线完成，计时失败原样保留', 'detail': '调用期间积分 1,299 步 / 5.413 原生秒，返回后仍等完整间隔；实际接触 15.413–15.417 秒，违反 10 秒目标。瓶体放回误差 0.444 mm；计时误差由漏记的原生时间加采样残差解释。模型宿主耗时 24.44 秒，与原生时间分开报告。'},
                    {'date': '2026-10-14', 'title': 'V85 · 连续积分时只等待未消耗的时间', 'detail': 'Astra 调用期间推进 67 步 / 0.279 原生秒；随后等待剩余 1,092 步。接触 10.000–10.004 秒，放回误差 0.406 mm。清空对照在 GPU 工作进程结束后离线调用；不是实时部署或配对成功率。'},
                    {'date': '2026-10-14', 'title': 'V84 · 绿色线索条件通过独立定时接触复核', 'detail': '新父子任务、三次真实模型调用；绿色线索记忆选择 10 秒接触，实际 10.000–10.004 秒。场景及记忆冷恢复后只执行 5,507 步余程。两种暂停线索条件现均完成，正式随机化 M1 仍为零。'},
                    {'date': '2026-10-13', 'title': 'V83 · 短时线索、记忆冷恢复与实际定时接触完成', 'detail': '三次新模型调用；前五阶段封存后，新进程恢复 56 刚体 / 9 关节系统及语义记忆。模型请求 16 秒接触，实际采样区间 16.000–16.004 秒，剩余 5,507 步完成，放回误差 0.33 mm。仿真暂停期间读出 36.8 秒；不是实时或化学计时验收。'},
                    {'date': '2026-10-13', 'title': 'V82 · Astra 语义记忆读出与清空对照封存', 'detail': '五次真实调用；两张历史提瓶图像、共同恢复画面、两段记忆。准确召回公开观测时刻并选择 10 / 16 秒排程；共同清空输入调用一次，选择等待。没有新增物理执行或计时验收。'},
                    {'date': '2026-10-13', 'title': 'V80 · 天平释放后中途恢复，只跑剩余任务', 'detail': '前五阶段 7,920 步与检查点保持完整；新进程恢复全实体及控制器游标，仅执行剩余 5,507 步，最终放回误差 0.55 mm。恢复后搬运漂移 6.05 mm（原门槛 20 mm）。Astra 记忆和连续化学时钟未验收。'},
                    {'date': '2026-10-13', 'title': 'V79 · 第一个实际瓶体任务与冷重建对照完成', 'detail': '每次 13,427 步、8 段保存、15 帧 RGBD。放回误差 0.74 / 0.54 mm，搬运双侧接触 99.83%。原始接触和全部恢复瞬态复核通过；尚无 Astra 决策、M1 或化学事件。'},
                    {'date': '2026-10-13', 'title': 'V78 · 原场景阶段恢复与失败重试实测', 'detail': '沿用 A-r7；同进程 / 新进程 / 子阶段失败重试覆盖 56 刚体与 9 关节系统。原阈值不变；仅空载夹爪技能，完整化学任务与连续时钟未验收。'},
                    {'date': '2026-10-13', 'title': '持续进度页与自动更新', 'detail': '接入白名单导出、分阶段进度和共享 GPU 遥测；网页时间戳区分研究结果、采样与发布。'},
                    {'date': '2026-10-12', 'title': 'V75 · 第一条实时 Astra 闭环开发采集封存', 'detail': '37 秒原生轨迹、8 段保存；保留 69/70 目标截断、杯外点和计时起点差异。正式准入仍未通过。'},
                    {'date': '2026-10-12', 'title': 'V74 · 分阶段长任务诊断', 'detail': '建立按阶段保留状态、图像、液体和边界证据的开发采集路径；不授予物理重启能力。'},
                ],
                next_steps=[
                    '八阶段完整登记状态已保存；逐个增加原生重建边界，再验收跨新检查点的记忆与原期限绑定。',
                    '携物冷恢复仍有姿态失败；两次连续基线瓶体记录一致。同进程恢复也有后续姿态失败；下一步封存单项状态写入对照，原门槛不变。随机化记忆及原事件连续父进程对照仍待实验。',
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
