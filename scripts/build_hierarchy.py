"""Publish protocol-family experiments, task scopes and compatible profile labels."""
import argparse
from html import escape as e
import json
from pathlib import Path

from build_workflow_system import render as render_matrix

EXAMPLES = {
    'L1':'抓取、放置、按压、开门；倒液从已经持握容器的就绪状态开始。',
    'L2':'限窗按压、保持时长、事件触发停机、受控流速或升温速率。',
    'L3':'抓取→放到仪器→启动；开门→装样→关门。核心为 2–5 个语义操作。',
    'L4':'显色→按条件等待→限窗读取；检测状态后继续、停止或重新处理。',
    'L5':'准备→反应或分离→测量→记录结果→安全收尾，覆盖完整声明范围。',
    'L6':'完整实验中协调多个计时器、样品有效期、状态触发操作与共享仪器。'}
RULES = {
    'indicator_titration':'混合后端点色持续确认；近终点降速。没有通用整场秒级时限。',
    'iodine_clock':'混合时开始计时，显色时记录未知诱导期；不把记录等同于终止反应。',
    'orthophosphate_8114':'23°C 主协议：显色等待 7 分钟，计时结束后 2 分钟内读数。',
    'dpd_chlorine':'游离氯与总氯采用不同等待/读数规则，需逐管绑定方法与计时起点。',
    'bca_assay':'标准试管法 37°C 孵育 30 分钟；冷却后，全部试管读数跨度不超过 10 分钟。',
    'recrystallization':'需要时进行热过滤，先逐渐冷却至室温，再按成核状态进入下一阶段。',
    'gravimetric_constant_mass':'温度条件下陈化；反复干燥、冷却、称量，比较相邻周期质量。',
    'liquid_liquid_extraction':'混合/放气循环，等待乳化消退与相界面明确后分层。',
    'melting_point':'近熔点区控制温度斜率，分别记录初熔和全熔状态。',
    'aspirin_back_titration':'特定协议规定加热/冷却时长，并在回滴前检查状态、必要时返工。',
    'winkler_dissolved_oxygen':'特定归档协议：现场固定后，采集至实验室测量不得超过 8 小时。',
    'actinometry':'累计有效光照暴露；必须声明光强、模型、装置与适用条件。',
    'crystal_violet_kinetics':'实时采集开始后每 30 秒读数，终点为反应开始后 5 分钟；保留两个时间锚点。'}
LABELS={'open_cabinet':'T5 开门','press':'T4-v2 按压','pick_place':'T1 抓放',
        'bottle_balance':'T2 天平往返','delayed_cue_memory':'T8 延迟选样',
        'pour':'T3 倾倒代理','endpoint_stop':'T7 端点代理'}


def render(hierarchy, chemistry, matrix):
    if len(hierarchy['levels']) != 6 or len(hierarchy['temporal_types']) != 10:
        raise ValueError('review changed hierarchy before publishing')
    if chemistry['chemistry_calibrated'] or chemistry['native_tasks_added']:
        raise ValueError('new calibration claims require physical evidence')
    base = render_matrix(matrix)
    style = base.split('<style>',1)[1].split('</style>',1)[0]
    levels = ''.join(f'<tr><th><span class="level">{e(k)}</span> {e(v["title"])}</th><td>{EXAMPLES[k]}</td><td>{e("、".join(LABELS[t] for t in hierarchy["legacy_tasks_by_level"][k])) if hierarchy["legacy_tasks_by_level"][k] else "尚无完整原生实验"}</td></tr>' for k,v in hierarchy['levels'].items())
    timing = ''.join(f'<tr><th>{e(v["title"])}</th><td>{e(v["semantics"])}</td></tr>' for v in hierarchy['temporal_types'].values())
    cases=[]
    for key, case in chemistry['cases'].items():
        links=' · '.join(f'<a href="{e(chemistry["sources"][s]["url"],quote=True)}">{e(chemistry["sources"][s]["title"])}</a>' for s in case['source_ids'])
        cases.append(f'<tr data-levels="{" ".join(case["candidate_levels"])}"><th>{e(case["title"])}</th><td>{RULES[key]}<details><summary>依据与待验收边界</summary><p>{e(case["caution"])}</p><p>{links}</p></details></td><td>{" / ".join(case["candidate_levels"])}<small>来源支持的设计 · 原生未验收</small></td></tr>')
    organization=hierarchy['primary_organization']
    scope_examples={'atomic':'从已经验收的就绪状态完成一个主动操作，以物理结果或真实采集事件判定。','subprotocol':'完成一个有实验意义、可复用的单元。非循环核心通常为 2–5 个技能，条件循环另报实际次数。','complete_protocol':'从样品准备到结果：执行、测量、可追溯的科学结果、记录和安全收尾，覆盖声明的完整范围。'}
    scopes=''.join(f'<tr><th>{e(v["title"])}</th><td>{scope_examples[k]}</td></tr>' for k,v in organization['scopes'].items())
    questions=''.join(f'<tr><th>{e(v["title"])}</th><td>{e("、".join(chemistry["cases"][case]["title"] for case in v["examples"]))}</td></tr>' for v in organization['temporal_questions'].values())
    family_text={
        'endpoint_quantitation':('分次加液、混合、暂停确认；消退则继续','未知含量/浓度、初末体积与端点误差','瞬时变色 ≠ 稳定端点；当前体积 ≠ 已交付体积'),
        'development_quantitation':('逐管显色、空白归零、有效窗内读数','浓度、标准检查、样品身份与时间链','同一当前时钟，不同历史起点，应选择不同样品'),
        'thermal_gravimetry':('处理→干燥器冷却→称量→比较→必要时重复','所选方法的失重/质量分析结果与质量历史','同一当前质量，不同上一轮读数，应停止或继续'),
        'reaction_kinetics':('反应启动、转移、逐点采集与实际时间记录','完整时间序列、拟合量与不确定性','相近最终信号不代表相同的过程轨迹')}
    families=''.join(f'<tr><th>{e(v["title"])}</th><td>{family_text[k][0]}</td><td>{family_text[k][1]}</td><td>{family_text[k][2]}</td></tr>' for k,v in organization['protocol_families'].items() if v['priority']=='core')
    html='''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>ChemRMBench · 实验家族与过程能力</title><link rel="icon" href="assets/favicon.svg"><style>__STYLE__
.level{display:inline-block;border-radius:5px;padding:4px 8px;background:#d5e9e2;color:#0c635c;margin-right:8px}.filters{display:flex;gap:8px;flex-wrap:wrap;margin:18px 0}.filters button{border:1px solid #9cbbb3;background:white;border-radius:5px;padding:8px 14px;color:#193a40;cursor:pointer}.filters button[aria-pressed=true]{background:#12786d;color:white}.temporal{font-family:ui-monospace,system-ui;font-size:13px}.timer{display:grid;grid-template-columns:1fr 2fr 1fr;gap:8px;margin:24px 0}.timer div{padding:20px 14px;border:1px solid #b9cfc6;background:#e2ede6;border-radius:6px}.timer div:last-child{background:#f4e6c7}.step-unit{font-size:18px;background:white;padding:18px;border:1px solid #d7e0dc}details p{font-size:13px}tr[hidden]{display:none}
</style></head><body><nav><a class="brand" href="system.html">ChemRMBench / 实验设计</a><div><a href="task-library.html">已有原生数据</a><a href="workflow-matrix.html">M/T 诊断矩阵</a><a href="scenes.html">重建场景</a></div></nav>
<header><span class="eyebrow">ATOMIC OPERATIONS → COMPOSITIONS → COMPLETE EXPERIMENTS</span><h1>从操作成功，到实验结果正确</h1><p class="lead">按“实验家族 × 任务范围”组织：原子操作、实验单元、完整协议。时间、反应逻辑、记忆和多样本调度分别说明，不再混成一条难度阶梯。</p><div class="status"><strong>当前实证：7 个原生任务；完整且化学校准的 L5/L6 实验为 0。</strong><br>四个核心完整实验家族仍是设计目标；13 个来源主题是参考库，不计为新增原生数据。原 v0.1 数据与判据保持不变。</div></header>
<main><section><h2>主分类：三种任务范围</h2><div class="scroll"><table id="scopeTable"><thead><tr><th>范围</th><th>完成边界</th></tr></thead><tbody>__SCOPES__</tbody></table></div><p>多样本是独立维度：串行重复不等于并行调度。还要报告分支、循环、实际技能次数、关键路径和同时未完成的承诺。</p></section>
<section><h2>时间在实验中的五种角色</h2><div class="scroll"><table id="temporalQuestions"><thead><tr><th>需要回答的问题</th><th>典型规程</th></tr></thead><tbody>__QUESTIONS__</tbody></table></div><p>“必须按时完成”“时间是处理条件”“状态出现后行动”“把时间作为测量坐标”“协调多个计时器”是不同问题。恒重属于历史比较与条件循环，不能用单次读数稳定代替。</p></section>
<section><h2>四个核心实验家族，共用下层模块</h2><div class="scroll"><table id="familyTable"><thead><tr><th>家族</th><th>实验单元</th><th>完整实验的产出</th><th>关键辨别实验</th></tr></thead><tbody>__FAMILIES__</tbody></table></div><p class="note">这些是待实现、待校准的设计。分离/纯化作为后续扩展；相关来源规程不能拼成一份虚构 SOP。烘箱失重法与硫酸盐沉淀、过滤、灼烧法必须分开。</p></section>
<section><h2>六个入口标签：保留兼容，不代表统一难度排序</h2><div class="scroll"><table id="levelTable"><thead><tr><th>级别</th><th>评测什么</th><th>已有任务的范围归类</th></tr></thead><tbody>__LEVELS__</tbody></table></div><p class="note">上表是既有任务的语义归类，尚未进行新的逐级资格验收。T3/T7 仍是工程代理，不能据此宣称化学反应已经校准。泛化与移动能力不靠增加一个级别来计数。</p><p class="step-unit"><strong>“一步”的单位：</strong>一个有入口条件和测量终止条件的实验室操作。抓取内部的接近、对齐、闭爪、抬升属于内部阶段。T2 是四个语义操作、八个归档阶段，不是完整化学实验。2–5 步为局部组合核心，6–10 步单列扩展。</p></section>
<section><h2>底层十种契约算子，可组合使用</h2><div class="scroll"><table id="timeOperators"><thead><tr><th>时间类型</th><th>精确定义</th></tr></thead><tbody class="temporal">__TIMING__</tbody></table></div><p>计时锚点绑定具体样品、实际操作或可测状态。样品达到目标温度与加热器打开不同；连续保持与断续累计不同；样品有效期与教学课时、机器人超时也不同。</p></section>
<section><span class="eyebrow">PROTOCOL EVIDENCE / NOT ARBITRARY SECONDS</span><h2>把化学要求落到可检查的事件与状态</h2><h3>例：正磷酸盐显色读数，23°C 主协议</h3><div class="timer"><div>混合后<br><strong>启动反应计时</strong></div><div><strong>等待 7 分钟</strong><br>按该方法要求显色</div><div><strong>随后 2 分钟</strong><br>完成样品读数</div></div><p>空白归零、样品身份、温度及每管计时起点均需保留。来源还记录了温度干扰；不能把其它温度下的等待时间直接当作等精度变体。</p><h3>例：滴定端点确认</h3><p>观察混合后的颜色 → 接近端点时减慢添加 → 暂停进一步添加并检查连续保持 → 满足该协议的确认条件后记录。颜色消退可以继续；真实过量应判失败。</p><p class="note">“颜色持续至少 30 秒”不是允许继续滴加 30 秒。普通酸碱滴定没有可通用于所有协议的整场秒级 deadline。新增感知响应容差、仿真压缩时间和 RGB 阈值必须单列工程来源。</p></section>
<section><h2>来源参考库：按兼容入口筛选</h2><p>每个主题都保留原始来源、时间锚点、适用条件、观测量与实现缺口；以下全部是待实现/验收的实验设计。</p><div class="filters" role="group" aria-label="筛选候选级别"><button data-filter="all" aria-pressed="true">全部主题</button><button data-filter="L2" aria-pressed="false">L2</button><button data-filter="L4" aria-pressed="false">L4</button><button data-filter="L5" aria-pressed="false">L5</button><button data-filter="L6" aria-pressed="false">L6</button></div><p id="caseCount" class="muted">13 个来源支持的主题</p><div class="scroll"><table id="caseTable"><thead><tr><th>实验主题</th><th>真实规则与来源</th><th>候选层级</th></tr></thead><tbody>__CASES__</tbody></table></div></section>
<section><h2>长程实验必须保存过程历史</h2><div class="columns"><div><video controls playsinline preload="metadata"><source src="assets/native-v01/t2-station-a-web.mp4" type="video/mp4"></video><small>已有 T2 连续原生轨迹：四个语义操作，八个归档阶段。代表视频不是一个完整化学实验。</small></div><div><p>现有 T2 的 20 条轨迹、160 个阶段档案通过一致性检查。新的化学协议还需要保存样品身份、过程状态、未完成计时器、历史测量和仪器占用，阶段交接不能重置反应进度。</p><p>上层的“恒重”要求比较前后处理周期的质量；“多管显色”要求记住每管的开始时间和读取窗口。它们不由末帧图像或阶段数证明。</p><p class="note">同进程分阶段保存和继续已有实现；任意阶段的新进程重建续跑尚未解决。新化学过程档案和校准还待实现。</p></div></div></section>
<section><h2>成组评测，区分失败原因</h2><p>比较局部与完整协议、不同记忆支持、固定策略与反馈、串行与重叠样品、受控扰动下的恢复、以及独立的泛化轴。每项使用同一批实例与扰动流；批内关联样品不能冒充独立试验。</p><p>记忆检查要证明关键事实曾经可见、当前观测不能直接给出答案。计时检查不能删除化学方法的必要等待；规定的固定等待本来就可能是正确策略。不可行调度单列，不混入普通成功率。</p><p><strong>严格成功 = 物理完成 ∧ 过程有效 ∧ 时序有效 ∧ 安全 ∧ 结果正确。</strong>同时报告各分项和所有失败、报错。结果必须符合声明的保真度：工程虚拟协议需要经过独立检查的模型参考，化学准确性主张还需相应的实测验证。完整协议的范围与校准级别分别报告。</p></section>
<section><h2>下一步先验收两个小流程</h2><ol><li>端点连续确认：瞬时变色、消退、持续满足与额外加液的 CPU 合同。</li><li>23°C 磷酸盐读数窗：实际混合/样品年龄、仪器计时起点、逐管采集事件。</li><li>过程、公开观测、机器人与完整协议依次验收，再展开四个实验家族。</li></ol><p>ChemLab 的天平、烘箱和混合装置按真实功能进入任务；不能把浊度计或旋光仪改名为吸光度仪。原生仪器操作、过程模型和公开传感都要独立验收。</p><p>真实规程时值、工程容差、仿真时间压缩分别存储。加速过程时钟不能默默加速机械臂或安全判定；压缩后作为独立工程设置报告。不会因为新增设计而申请空闲卡。</p><div class="links"><a href="benchmark-docs/experimental_design.md">完整实验设计与成组对照</a><a href="benchmark-docs/hierarchical_benchmark.md">兼容入口与化学依据</a><a href="data/hierarchy-design.json">六级与十类契约 JSON</a><a href="data/chemistry-design-cases.json">13 类实验的来源目录</a><a href="workflow-matrix.html">已有 M/T 控制矩阵</a><a href="https://arxiv.org/html/2505.22634v2">LabUtopia 参考论文</a></div></section></main><footer>按实验家族与范围组织；来源支持、软件检查、原生成功和化学校准分别报告。</footer>
<script>const buttons=[...document.querySelectorAll('[data-filter]')],rows=[...document.querySelectorAll('#caseTable tbody tr')];for(const b of buttons)b.addEventListener('click',()=>{for(const x of buttons)x.setAttribute('aria-pressed',String(x===b));let n=0;for(const r of rows){r.hidden=b.dataset.filter!=='all'&&!r.dataset.levels.split(' ').includes(b.dataset.filter);if(!r.hidden)n++}document.querySelector('#caseCount').textContent=n+' 个来源支持的候选主题；原生未验收'});</script></body></html>'''
    return html.replace('__STYLE__',style).replace('__LEVELS__',levels).replace('__TIMING__',timing).replace('__CASES__',''.join(cases)).replace('__SCOPES__',scopes).replace('__QUESTIONS__',questions).replace('__FAMILIES__',families)


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    for key in ['hierarchy','chemistry','site']:parser.add_argument('--'+key,type=Path,required=True)
    args=parser.parse_args()
    h=json.loads(args.hierarchy.read_text());c=json.loads(args.chemistry.read_text())
    matrix=json.loads((args.site/'data/workflow-design.json').read_text())
    (args.site/'workflow-matrix.html').write_text(render_matrix(matrix),encoding='utf-8')
    (args.site/'system.html').write_text(render(h,c,matrix),encoding='utf-8')
    (args.site/'data/hierarchy-design.json').write_text(json.dumps(h,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (args.site/'data/chemistry-design-cases.json').write_text(json.dumps(c,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
