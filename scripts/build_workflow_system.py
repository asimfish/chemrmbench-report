"""Build the public workflow overview from specification-only inventory."""
import argparse
from html import escape
import json
from pathlib import Path


def render(data):
    if data['status'] != 'design_candidate' or data['native_tasks_added'] != 0:
        raise ValueError('review new qualification evidence before changing this page')
    if len(data['diagnostic_templates']) != 20 or len(data['long_protocols']) != 4:
        raise ValueError('review changed design scope')
    cells = ['M0_T0', 'M1_T0', 'M0_T1', 'M1_T1']
    memory = {'routing':'样品身份', 'weighing':'归还位置', 'dispensing':'接收容器',
              'endpoint':'目标端点颜色', 'instrument':'目标仪器 / 门'}
    times = {'routing':'提示后启动抓取 · 候选窗口 10 s', 'weighing':'天平驻留 · 2 / 4 / 6 s',
             'dispensing':'倾倒保持 · 2 / 4 / 6 s', 'endpoint':'端点后完成 · ≤ 5 s，零超量',
             'instrument':'开门驻留后关闭 · 2 / 4 / 6 s'}
    rows = []
    for name, family in data['families'].items():
        columns = ''.join(f'<td><span class="cell">{escape(name)}.{cell.replace("_", "·")}</span><small>规格已实现 · 原生待验收</small></td>' for cell in cells)
        rows.append(f'<tr><th><strong>{escape(family["title"])}</strong><small>记忆：{memory[name]}<br>计时：{times[name]}</small></th>{columns}</tr>')
    protocols = ''.join(f'<article><span class="tag">长程协议 · 待集成</span><h3>{escape(row["title"])}</h3><p>{row["semantic_nodes"]} 个语义节点；{row["memory_facts"]} 项待保持信息。</p></article>' for row in data['long_protocols'])
    blockers = ''.join(f'<details><summary>{escape(f["title"])}：下一项原生验收</summary><p>{escape("；".join(f["blockers"]))}</p><p>资产角色：{escape(f["asset_role"])}</p></details>' for f in data['families'].values())
    html = '''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>ChemRMBench · 基准体系</title><link rel="icon" href="assets/favicon.svg"><style>
:root{--ink:#193a40;--muted:#5c7074;--paper:#f6f5ef;--line:#d7e0dc;--accent:#12786d;--amber:#96651b}*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font:16px/1.7 system-ui,sans-serif}a{color:var(--accent)}nav{display:flex;justify-content:space-between;gap:20px;padding:18px max(5vw,20px);border-bottom:1px solid var(--line);flex-wrap:wrap}nav a{text-decoration:none;margin-right:20px}.brand{font-weight:800}main,header{max-width:1200px;margin:auto;padding:40px 26px}header{padding-top:64px}h1{font-size:clamp(30px,4vw,52px);line-height:1.3;max-width:940px;margin:14px 0 20px}h2{font-size:27px;margin:0 0 15px}h3{font-size:19px}.eyebrow,.tag{color:var(--accent);font-size:12px;font-weight:750;letter-spacing:.06em}.lead{max-width:880px;font-size:20px;color:var(--muted)}.status{border-left:4px solid var(--accent);padding:12px 18px;background:#e8f1eb;max-width:1000px}.status strong{color:var(--ink)}section{padding:32px 0 40px;border-top:1px solid var(--line)}.muted,small{color:var(--muted)}.flow,.cards{display:grid;gap:12px;grid-template-columns:repeat(4,1fr)}.flow>div,.cards>article{background:#fff;border:1px solid var(--line);padding:20px;border-radius:8px}.flow b{display:block;font-size:20px}.flow small{display:block}.scroll{overflow:auto}table{width:100%;border-collapse:collapse;background:white;font-size:14px}th,td{text-align:left;padding:17px 13px;border:1px solid var(--line);vertical-align:top}thead th{background:#e7efea}th:first-child{min-width:235px}td{min-width:160px}small{display:block;font-size:12px;margin-top:6px}.cell{font:12px ui-monospace,monospace;color:var(--amber)}.note{background:#fff0d8;border-left:3px solid #be9247;padding:14px 18px}.columns{display:grid;grid-template-columns:1.1fr 1fr;gap:26px}video{width:100%;background:#17333a;border-radius:8px}details{padding:13px 0;border-bottom:1px solid var(--line)}summary{cursor:pointer;font-weight:600}.links a{display:inline-block;margin:8px 20px 8px 0}footer{max-width:1200px;margin:auto;padding:20px 26px 50px;color:var(--muted)}@media(max-width:850px){.flow,.cards{grid-template-columns:repeat(2,1fr)}.columns{grid-template-columns:1fr}}@media(max-width:480px){.flow,.cards{grid-template-columns:1fr}header,main{padding:28px 18px}}
</style></head><body><nav><a class="brand" href="system.html">ChemRMBench / 基准体系</a><div><a href="task-library.html">原生数据与视频</a><a href="scenes.html">重建实验室</a><a href="capabilities.html">实现边界</a><a href="index.html">项目入口</a></div></nav>
<header><span class="eyebrow">EVENT MEMORY × OPERATION TIMING × LONG PROTOCOLS</span><h1>记住事件，按时操作，完成长程实验</h1><p class="lead">围绕同一个实验室工作流，分别控制线索是否需要记忆、操作是否需要准确计时，再测试这些能力能否跨阶段组合。</p><div class="status"><strong>已有数据：7 个原生基础任务，3 个直接计时任务。</strong><br>本轮新增：5 类工作流的 20 个对照规格、4 条长程协议。它们是待验收设计，新增原生成功数据为 0；旧数据和冻结协议保持不变。</div></header>
<main><section><h2>一个任务，四个可比较条件</h2><div class="flow"><div><b>01 / 物理场景</b><small>同一 A-Lab、FR3、布局和采样对象</small></div><div><b>02 / 工作流</b><small>同一目标图与物理成功条件</small></div><div><b>03 / M × T</b><small>只改变线索保留方式与时间计分</small></div><div><b>04 / 独立判定</b><small>读状态、接触和世界事件；保留所有失败</small></div></div><p>这样能分清操作失败、记忆失败、时机失败与长程衔接失败。换一个 seed、贴图或仪器模型，属于实例与泛化变化。</p></section>
<section><span class="eyebrow">FIVE WORKFLOW FAMILIES / TWENTY CONTROLLED SPECIFICATIONS</span><h2>工作流矩阵</h2><p>M0：线索持续可见；M1：1 秒线索后延迟 3 / 10 / 20 秒。T0：不按时间约束计分；T1：同时检查物理目标与声明的时间约束。四组共用同一采样世界和目标图。</p><div class="scroll"><table><thead><tr><th>工作流 / 要测什么</th><th>M0 · T0<br><small>操作对照</small></th><th>M1 · T0<br><small>记忆因素</small></th><th>M0 · T1<br><small>计时因素</small></th><th>M1 · T1<br><small>记忆与计时结合</small></th></tr></thead><tbody>__ROWS__</tbody></table></div><p class="note">所有新单元格仍待原生资格测试。表中的候选时窗不能回写旧 v0.1 指标；原生开合、三容器布局和跨阶段适配器仍需实现与验收。已有七项数据是构建模块的证据。</p></section>
<section><span class="eyebrow">SAME LIVE SCENE / MEASURED HANDOFFS</span><h2>长程协议：阶段之间保留同一物理世界</h2><div class="cards">__PROTOCOLS__</div><p>每一阶段检查测量得到的前提，保存全场景状态、关节与控制目标、事件游标和录像时间索引，再继续下一阶段。语义节点数不是已采机器人阶段数；独立 reset 的片段不能拼成一条长任务结果。</p><div class="columns"><div><video controls playsinline preload="metadata"><source src="assets/native-v01/t2-station-a-web.mp4" type="video/mp4"></video><small>已有 T2 原生专家完整轨迹：8 阶段，同一进程连续执行。代表视频为 seed 1，属于专家开发数据。</small></div><div><h3>已有实现与本轮复核</h3><p>T2 的 20 条既有轨迹，共 160 个阶段档案，时钟、事件游标、完整登记实体及关节控制字段检查全部一致。3 条物理任务失败也保留在这 20 条中。</p><p class="note">同进程阶段保存和继续已实现。任意阶段在新进程重建并续跑尚未解决；这次档案检查不证明冷恢复。旧普通冷重建覆盖仍为 1/8。</p></div></div></section>
<section><span class="eyebrow">ASSETS SERVE TASKS AND GENERALIZATION</span><h2>ChemLab 的位置：仪器操作与新物体留出</h2><div class="columns"><div><p>10 个资产通过被动物理准入，4 个有明确把手合同，0 个通过机器人开盖资格。先把开合与接触做通，再进入仪器工作流及新物体测试；这些留出资产不进入训练演示。</p><p>Ossila 已放回原重建实验室并录制双相机检查视频。完整 CPU 开盖路径仍未通过余量验收，因此没有开盖成功率可报告。</p><p>资产来源 <a href="https://huggingface.co/datasets/MBZUAI/ChemLab-Assets">MBZUAI / ChemLab-Assets</a>；CC BY-NC 4.0，质量和动力学未标定。<a href="capabilities.html">查看署名、原生视频及具体边界 →</a></p></div><div><h3>每类工作流的实际缺口</h3>__BLOCKERS__</div></div></section>
<section><h2>实验与实现顺序</h2><ol><li>先原生化“样品识别与转运”的四组对照：复用 T1/T8，资格测试后再开主批量。</li><li>依次接称量、倾倒与端点工作流；仪器开合随合格 ChemLab 资产加入。</li><li>第一条组合协议做“识别—称量—归还”，验收无 reset 衔接后扩展其余协议。</li><li>资格通过后冻结新 split，再报告四组成功率、记忆/计时差值、交互项、整任务成功与安全违规；旧主表单列。</li></ol><p>现有 DP 与 v0.1 评测继续按冻结协议推进。新模板不会自动启动 GPU；只对软件、数据和队列均就绪的任务分配卡，不以申请更多卡或占满无用显存来展示进度。</p><div class="links"><a href="data/workflow-design.json">设计目录 JSON</a><a href="benchmark-docs/benchmark_system.md">研究问题、数学定义与实验协议</a><a href="benchmark-docs/adr_workflow_suite.md">结构决策与取舍</a><a href="task-library.html">已有主表、双相机视频与失败记录</a></div></section></main><footer>本页区分规格、软件验收和原生实验。当前仍为基准候选；没有把新设计计为新原生任务。</footer></body></html>'''
    return html.replace('__ROWS__', ''.join(rows)).replace('__PROTOCOLS__', protocols).replace('__BLOCKERS__', blockers)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--inventory', type=Path, required=True)
    parser.add_argument('--site', type=Path, required=True)
    args = parser.parse_args()
    data = json.loads(args.inventory.read_text())
    (args.site / 'system.html').write_text(render(data), encoding='utf-8')
    (args.site / 'data/workflow-design.json').write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
