'use strict';
const copy = {
  en: {
    skip:'Skip to content', developing:'In development', contents:'IN THIS REPORT',
    'nav.overview':'Overview','nav.method':'Benchmark design','nav.evidence':'Current evidence','nav.failures':'Failure analysis','nav.roadmap':'Acceptance roadmap','nav.resources':'Resources & updates',
    snapshot:'Versioned snapshot','sidebar-note':'Results retain their original scope. Unrun experiments remain open.',
    eyebrow:'LABORATORY INTELLIGENCE / PUBLIC RESEARCH LOG',
    subtitle:'Memory, timing, and process compliance\nin laboratory tasks.',
    'hero-description':'Can an embodied policy remember which vessel was treated, wait for the required interval, and follow the process—even when the scene no longer reveals the answer?',
    explore:'Explore the protocol ↓','read-evidence':'Read the evidence →',
    'research-note-title':'A benchmark under construction.',
    'research-note':'The design separates memory and timing demands from tool access, and evaluates both outcomes and process traces. Current native results are development diagnostics. Full scientific acceptance and the contribution gate remain open.',
    expert:'QUALIFIED EXPERT DEMOS', fits:'MATCHED NATIVE VLA FITS', admission:'FRESH UNKNOWN ADMISSION', manuscript:'MANUSCRIPT',
    uncollected:'Not yet collected','not-started':'Not yet run',open:'Open',pages:'pages',draft:'ICML-style draft',readiness:'Not submitted · benchmark_complete = false · conference_ready = false',
    'method-title':'Same task. Different information.',
    'method-lead':'Five vessels share the same geometry and physical occlusion. A first operation identifies a recipient; a later operation must return to it after a specified delay. Memory and timing are varied while the world and controller stay matched.',
    'concept-label':'FIGURE 01 · INTERACTIVE CONCEPT',illustration:'Illustration, not a native result',
    'memory-mode':'Memory condition',persistent:'Persistent cue',transient:'Transient cue',recipient:'Recipient',
    'phase-a':'Operation A','phase-wait':'Wait D','phase-b':'Operation B','cue-appears':'Recipient cue appears',recall:'Remember & track time',return:'Return to the recipient',
    'concept-caption':'Proposed M0 uses a persistent dye cue. Proposed M1 uses only the real three-second A-pour cue; afterward, a common stationary home and physical occlusion must remove recipient and clock shortcuts. These physical cue requirements have not passed native validation.',
    'matched-title':'Eight matched conditions','matched-text':'M0 / M1 × relaxed / relative tolerance η=ε/D of 0.30 / 0.15 / 0.08. Shared world, seed, assets and controller. A finite scripted reference grid exists; the qualified physical eight-condition benchmark is incomplete.',
    'grid-caption':'○ planned benchmark conditions; not eight certified results','tracks-title':'Three policy access tracks',
    'track-a':'Raw RGBD + proprioception + language. No public clock.','track-b':'The same A fields, plus a bare timestamp.','track-c':'Tool-assisted reference track, reported separately.',
    'pipeline-task':'Task','pipeline-world':'Controlled world','pipeline-policy':'Frozen policy','pipeline-verifier':'Read-only verifier','pipeline-report':'Trace & report',
    'verifier-note':'Outcome and process are scored together; verifier state is private. Paper A evaluates frozen policies.',
    'evidence-title':'What has actually been tested.','evidence-lead':'Each result has a scope and a denominator. Native development runs, CPU feasibility, and formal benchmark experiments are separate populations.',
    all:'All evidence',native:'Native diagnostics',cpu:'CPU feasibility',failed:'Failed',loading:'Loading the versioned evidence snapshot…',
    'figure-two':'FIGURE 02 · ACTUAL CAMERA / PARTICLE DIAGNOSTIC','figure-three':'FIGURE 03 · ACTUAL FRANKA DRIVE TRACE',
    'camera-alt':'Actual development camera projection and saved particle row motion across lens/readback settings',
    'franka-alt':'Actual joint 1 and finger position traces during a limited Franka actuator diagnostic',
    'camera-caption':'V34 / 20 development captures. Diagnostic magenta markers are excluded from benchmark cues. Lens settings recover visibility of all five slots, but M0 dye readability remains open. Saved row displacement is not calibrated volume or verified particle identity; multiple settings changed.',
    'franka-caption':'V35 / one run, 360 physics states, 60 targets. Only joint 1 and finger movement are exercised here. Two shutdown callback errors are retained. This does not establish grasping, pouring, the 200-call reference hardware protocol, or VLA performance.',
    'failure-title':'Fix one cause. Keep the remaining failures.','failure-lead':'The shared-fluid diagnostic holds the planned stage, controller and trajectory fixed. Increasing aggregate capacity removes the reported PhysX backend error, but does not resolve tilt or particle scatter.',
    'comparison-caption':'V37 — two separate seen diagnostic runs',measurement:'Measurement',interpretation:'Interpretation',
    capacity:'GPU aggregate capacity','capacity-change':'Only planned backend capacity changed','physics-errors':'Critical PhysX errors','error-cleared':'Reported capacity error cleared',
    tilt:'Maximum actual cup tilt','tilt-fail':'FAIL · frozen threshold ≥90°',workspace:'Workspace containment gate','not-gated':'Not gated in R2','scatter-open':'Particle scatter remains unresolved',captures:'States / captures / target calls','one-run':'One fixed diagnostic run per revision',
    observed:'OBSERVED','observed-title':'Motion and containment are not certified.','observed-text':'Particles with very low world-z had left the finite floor footprint; low z alone is not proof of floor penetration. Fixed world-cylinder counts also do not establish liquid inside a moving receiver cup.',
    'next-test':'NEXT TEST','next-test-title':'Observe before changing the controller.','next-test-text':'V40 adds same-tick joint/body angular motion and receiver-pose traces. It keeps the drive and physics plan fixed, to distinguish tracking, velocity readout and receiver-motion hypotheses. This is a diagnostic, not a calibrated independent sensor.',
    'failure-note':'Original failed runs, warnings and frozen thresholds are retained. Engineering validity is not full dynamics or chemical calibration.',
    'replay-label':'Replay of actual V37-R3 failed development diagnostic','replay-title':'Watch the actual diagnostic.',
    'replay-description':'A fixed supply tool on the Franka hand moves above five receivers. This replay uses all 70 saved RGB captures at 10 fps, without added cue markers or annotations. It is a lossy presentation derivative of the closed captures.',
    'replay-scope':'One seen development run. The replay does not validate dye readability, a real three-second M1 cue, grasping or calibrated liquid transfer. Tilt and workspace containment fail.',
    'replay-download':'Download 7 s replay ↓',
    'roadmap-title':'What must close before the main claim.','roadmap-lead':'A formatted paper and reproducible diagnostics do not replace scientific admission. The original requirements remain the acceptance criteria.',
    'in-progress':'IN PROGRESS',pending:'PENDING',
    'r1-title':'Physical cue & control',r1:'Five-slot visibility, persistent M0 dye, real three-second M1 A-pour, common stationary home, liquid containment and calibrated quantity.',
    'r2-title':'Freeze observations. Test fresh unknown scenes.',r2:'Whole-scene five-fold elapsed-time ridge R² ≤0.05 (G8), cue presence / identity ≥0.95 and scene reliability (G9), with post-ID, paused, timestamp and oracle controls. No reuse of development scenes as fresh confirmation.',
    'r3-title':'Qualified data & matched training',r3:'700 actual expert demonstrations; per-stratum success ≥0.95 and |median(e)| ≤T_ctrl=0.1 s (one control period). Five matched VLA configurations × three seeds, shared backbone, data and compute, parameter counts within ±5%.',
    'r4-title':'Timing, process & generalization',r4:'Native 10 Hz / chunk 16 / replan 8 / >2 s timeout; paused and actual asynchronous conditions, 200 reference hardware calls. Paired language/numeric delays, held-out paraphrases, closed/compositional/open tasks and family/system transfer.',
    'r5-title':'Calibration & preregistered scientific evaluation',r5:'Two real benches × nine planned calibration cells; uncertainty, held-out residuals and ±30% sensitivity. Instrumented process/quantity/contact tasks. Preregister power and E1/E2/E3 effects ≥0.10; paired task/seed bootstrap (2,000) and Holm correction.',
    'acceptance-title':'Overall acceptance: OPEN','acceptance-text':'CON03 MAJOR_OPEN · 0 qualified demonstrations · 0 native VLA fits · 0 collected external calibration cells. Current diagnostics are excluded from these denominators.',
    'resources-title':'A report that can be checked.','snapshot-resource':'Progress snapshot','snapshot-resource-text':'Dated counts, scope, source digests and experiment summaries.',
    'audit-resource':'V37-R3 audit subset','audit-resource-text':'Ten physical diagnostic gates, actual tilt and bounded region counts.',
    'repo-resource':'Public report source','repo-resource-text':'Page source, owned vector figures, snapshot history and disclosure policy.',
    'updates-title':'Recent research updates','u1-title':'Public report / V41','u1':'Bilingual protocol, interactive mechanism, actual figures, failure comparison and acceptance roadmap. Curated evidence only.',
    'u2-title':'V40 dynamics diagnosis','u2':'The versioned progress snapshot records the latest preflight, CPU and native diagnostic status. Open the progress JSON if the snapshot cannot load.',
    'u3-title':'V39 common-home feasibility','u3':'Independent CPU review of five trajectories passed. Earlier inverse-kinematics and speed-limit failures remain archived. Physical execution is untested.',
    'u4-title':'V37-R3 shared-fluid diagnostic / FAIL','u4':'Backend capacity errors removed; actual ≥90° tilt and workspace containment still fail. The audit has not been promoted to a benchmark success.',
    'u5-title':'V38 manuscript candidate 11','u5':'54-page ICML-style draft with two new diagnostic appendix pages. Methods and presentation reviews are limited passes; contribution review remains Major Revision.',
    'disclosure-title':'Disclosure & provenance','disclosure-text':'This public subset contains authored summaries and owned figures. The unpublished full manuscript, credentials, private filesystem paths and licensed simulator assets are not distributed here. Source digests identify the underlying closed artifacts; the public subset is not a standalone reproduction capsule.',
    'snapshot-policy':'Snapshots are updated after evidence is checked. This page does not imply live telemetry, submission, acceptance, or complete benchmark release.',
    'reference-credit':'Presentation references:','back-top':'Back to top ↑',
  },
  zh: {
    skip:'跳至正文',developing:'研究进行中',contents:'报告目录',
    'nav.overview':'研究概览','nav.method':'Benchmark 方案','nav.evidence':'已有实验','nav.failures':'失败分析','nav.roadmap':'验收路线','nav.resources':'资源与进展',
    snapshot:'版本化进展快照','sidebar-note':'结果保留原始适用范围。未执行实验保持开放。',
    eyebrow:'实验室智能 / 公开研究记录',subtitle:'实验室任务中的记忆、计时\n与过程合规评测。',
    'hero-description':'当场景已不再透露答案，具身策略能否记住哪个器皿被操作、等待规定间隔，并遵循完整流程？',
    explore:'查看方案 ↓','read-evidence':'阅读实验结果 →','research-note-title':'正在建设的 benchmark。',
    'research-note':'方案将记忆、计时需求与工具访问分开，同时评价终局结果和过程轨迹。当前 native 结果属于开发诊断，完整科学验收与贡献门仍未关闭。',
    expert:'合格专家示范',fits:'匹配 NATIVE VLA 训练',admission:'全新未知场景准入',manuscript:'论文草稿',
    uncollected:'尚未采集','not-started':'尚未运行',open:'待验收',pages:'页',draft:'ICML 格式草稿',readiness:'未投稿 · benchmark_complete = false · conference_ready = false',
    'method-title':'任务相同，信息条件不同。','method-lead':'五个器皿共享几何与物理遮挡。第一步操作指定接收器皿，后续操作须在规定等待间隔后返回它。改变记忆与计时条件，保持世界和控制器匹配。',
    'concept-label':'图 01 · 可交互概念示意',illustration:'方案示意，非 native 结果','memory-mode':'记忆条件',persistent:'持久 cue',transient:'短暂 cue',recipient:'目标器皿',
    'phase-a':'操作 A','phase-wait':'等待 D','phase-b':'操作 B','cue-appears':'目标线索出现',recall:'记住目标并计时',return:'返回原目标',
    'concept-caption':'M0 计划使用持久染料线索；M1 仅使用真实三秒 A 倒液线索。之后通过共同静止 home 与物理遮挡，消除目标身份和时钟捷径。这些物理 cue 要求尚未通过 native 验证。',
    'matched-title':'八个匹配条件','matched-text':'M0 / M1 × relaxed / 相对容差 η=ε/D 为 0.30 / 0.15 / 0.08。共享 world、seed、assets 与 controller。已有有限手写 reference 八格执行，合格的物理八条件 benchmark 尚未完成。',
    'grid-caption':'○ 表示计划中的 benchmark 条件，不代表八格均已验收','tracks-title':'三种策略访问条件',
    'track-a':'原始 RGBD + 本体状态 + 语言，不公开时钟。','track-b':'与 A 相同的字段，仅增加裸时间戳。','track-c':'使用工具的参考策略，单独报告。',
    'pipeline-task':'任务','pipeline-world':'受控世界','pipeline-policy':'冻结策略','pipeline-verifier':'只读判定器','pipeline-report':'轨迹与报告',
    'verifier-note':'同时评价结果与过程；verifier 状态为私有。Paper A 评测冻结策略。',
    'evidence-title':'哪些实验确实运行过。','evidence-lead':'每项结果都有范围和分母。native 开发诊断、CPU 可行性与正式 benchmark 实验属于不同群体。',
    all:'全部证据',native:'Native 诊断',cpu:'CPU 可行性',failed:'失败',loading:'正在加载版本化证据快照…',
    'figure-two':'图 02 · 实际相机 / 粒子诊断','figure-three':'图 03 · 实际 FRANKA 驱动轨迹',
    'camera-alt':'不同 lens 和 readback 设置下，实际相机投影与保存粒子行运动诊断',
    'franka-alt':'限定 Franka 执行器诊断中的实际 joint 1 和 finger 位置轨迹',
    'camera-caption':'V34 / 20 张开发捕获。紫色诊断 marker 不进入 benchmark cue。lens 设置恢复五槽可见性，但 M0 染料可读性仍开放。保存行的位移不是标定体积或已验证粒子身份；此处同时改变了多个设置。',
    'franka-caption':'V35 / 1 次运行、360 个物理状态、60 次 targets。仅测试 joint 1 与 finger 运动，保留两次关闭 callback 错误。不证明抓取、倒液、200-call reference hardware protocol 或 VLA 性能。',
    'failure-title':'修复一个原因，保留其他失败。','failure-lead':'共享流体诊断保持原计划场景、控制器与轨迹不变。提高 aggregate 容量消除了报告的 PhysX backend 错误，但未解决倾角不足与粒子散逸。',
    'comparison-caption':'V37 — 两次独立的已见场景诊断',measurement:'测量项',interpretation:'解释',capacity:'GPU aggregate 容量',
    'capacity-change':'仅改变计划中的 backend 容量','physics-errors':'PhysX critical errors','error-cleared':'报告的容量错误消除',
    tilt:'实际最大杯倾角','tilt-fail':'FAIL · 冻结阈值 ≥90°',workspace:'工作区留存门','not-gated':'R2 尚无此门','scatter-open':'粒子散逸原因未关闭',captures:'状态 / 捕获 / target calls','one-run':'每版本仅一次固定诊断',
    observed:'已观察','observed-title':'运动与留存尚未认证。','observed-text':'world-z 很低的粒子已离开有限地板的 XY 范围，低 z 本身不能证明穿透地板。固定世界圆柱内的粒子计数，也不能证明液体位于实际移动烧杯内。',
    'next-test':'下一验证','next-test-title':'先增加观测，再改变控制器。','next-test-text':'V40 增加同 tick 的关节 / 刚体角运动与接收杯位姿 trace，保持驱动和物理计划不变，用于区分跟踪、速度读数和接收杯运动假设。它是诊断，不是标定的独立传感器。',
    'failure-note':'保留原失败、警告与冻结阈值。工程有效性不等于完整动力学或化学校准。',
    'replay-label':'V37-R3 实际失败开发诊断的回放','replay-title':'直接查看实际诊断。',
    'replay-description':'Franka 手部固定的供液工具在五个接收杯上方运动。使用全部 70 张已保存 RGB，以 10 fps 回放，不添加 cue marker 或标注。视频是闭合捕获的有损展示衍生产物。',
    'replay-scope':'仅一次已见开发运行。不验证染料可读性、真实三秒 M1 cue、抓取或标定液体转移。倾角与工作区留存仍失败。',
    'replay-download':'下载 7 秒回放 ↓',
    'roadmap-title':'主结论成立前，仍须完成什么。','roadmap-lead':'论文格式与可复现诊断不能替代科学准入。最初要求继续作为验收标准。','in-progress':'进行中',pending:'待完成',
    'r1-title':'物理 cue 与控制',r1:'五槽可见、M0 持久染料、M1 真实三秒 A 倒液、共同静止 home、液体留存与标定量。',
    'r2-title':'冻结观察后，验证全新未知场景',r2:'whole-scene 五折 elapsed-time ridge R² ≤0.05（G8）；cue presence / identity ≥0.95 与 scene 可靠性（G9），含 post-ID、paused、timestamp、oracle 正控。不将开发场景复用作 fresh confirmation。',
    'r3-title':'合格数据与匹配训练',r3:'700 条实际专家示范，逐 stratum 成功率 ≥0.95、|median(e)| ≤T_ctrl=0.1 s（一个控制周期）。5 个匹配 VLA 配置 × 3 seeds，共享 backbone、data、compute，参数量差异在 ±5% 内。',
    'r4-title':'计时、过程与泛化',r4:'native 10 Hz / chunk 16 / replan 8 / >2 s timeout；paused 与实际异步条件、200 reference hardware calls。language / numeric 延迟配对、保留 paraphrases、closed / compositional / open 任务与跨 family / system transfer。',
    'r5-title':'校准与预注册科学实验',r5:'两个真实台架 × 九格计划校准，含不确定性、held-out residuals 与 ±30% sensitivity。instrumented process / quantity / contact 任务。预注册 power 与 E1/E2/E3 效应 ≥0.10；task / seed 配对 bootstrap（2,000 次）及 Holm 校正。',
    'acceptance-title':'整体科学验收：OPEN','acceptance-text':'CON03 MAJOR_OPEN · 0 合格示范 · 0 native VLA fits · 0 已采外部校准格。当前诊断不进入这些科学分母。',
    'resources-title':'可以核查的公开报告。','snapshot-resource':'进展快照','snapshot-resource-text':'带日期的计数、范围、来源摘要与实验说明。',
    'audit-resource':'V37-R3 审计公开子集','audit-resource-text':'十项物理诊断门、实际倾角与有限区域计数。',
    'repo-resource':'公开报告源码','repo-resource-text':'页面源码、自有矢量图、快照历史与披露规则。',
    'updates-title':'近期研究进展','u1-title':'公开报告 / V41','u1':'中英方案、交互机制示意、实际实验图、失败对比与验收路线，仅包含经过整理的公开证据。',
    'u2-title':'V40 动力学诊断','u2':'版本化进展快照记录最新的预检、CPU 和 native 诊断状态。若快照不能加载，请查看进展 JSON。',
    'u3-title':'V39 共同 home 可行性','u3':'五条轨迹的独立 CPU 审阅通过；之前的 IK 与速度门失败继续存档。物理执行尚未验证。',
    'u4-title':'V37-R3 共享流体诊断 / FAIL','u4':'backend 容量错误消除，实际 ≥90° 倾角和工作区留存仍失败，没有将审计升级为 benchmark 成功。',
    'u5-title':'V38 论文 candidate 11','u5':'54 页 ICML 格式草稿，新增两页诊断附录。方法与展示审阅限定通过，贡献审阅仍为 Major Revision。',
    'disclosure-title':'披露与来源','disclosure-text':'公开子集包含自撰摘要与自有图。未公开的完整论文、凭证、私有文件路径与授权受限的模拟器资产不在此分发。SHA 摘要对应底层闭合产物；公开子集不是独立复现 capsule。',
    'snapshot-policy':'证据核查后更新快照。本页不代表实时遥测、已投稿、已录用或完整 benchmark 发布。','reference-credit':'展示格式参考：','back-top':'返回顶部 ↑',
  }
};
let lang = new URLSearchParams(location.search).get('lang') === 'zh' ? 'zh' : 'en';
let mode = 'M1', phase = 'wait', recipient = 2, evidenceFilter = 'all', snapshot;
const views = ['overview','method','evidence','failures','roadmap','resources'];
const t = key => copy[lang][key] ?? copy.en[key] ?? key;
function element(tag, className, text){const el=document.createElement(tag);if(className)el.className=className;if(text!==undefined)el.textContent=text;return el;}
function updateUrl(view, push=false){const u=new URL(location.href);u.searchParams.set('lang',lang);if(view)u.searchParams.set('view',view);u.hash='';history[push?'pushState':'replaceState']({},'',u);}
function renderText(){
  document.documentElement.lang=lang;
  document.title=lang==='zh'?'ChemRMBench — 研究进展与方案':'ChemRMBench — Research progress & protocol';
  document.querySelectorAll('[data-i18n]').forEach(el=>{el.textContent=t(el.dataset.i18n);});
  document.querySelectorAll('[data-alt]').forEach(el=>el.alt=t(el.dataset.alt));
  document.querySelectorAll('[data-aria]').forEach(el=>el.setAttribute('aria-label',t(el.dataset.aria)));
  const toggle=document.getElementById('language-toggle');toggle.textContent=lang==='en'?'中文':'English';toggle.setAttribute('aria-label',lang==='en'?'Switch to Chinese':'切换至英文');
  document.querySelector('.hero-subtitle').style.whiteSpace='pre-line';
  renderMechanism();renderEvidence();
  if(snapshot){
    const date=snapshot.updated_at_utc.slice(0,10);document.getElementById('snapshot-date').textContent=date+' · UTC';document.getElementById('footer-snapshot').textContent=(lang==='en'?'Snapshot ':'快照 ')+date;
    const dynamics=snapshot.evidence.find(row=>row.id==='V40');
    if(dynamics){document.querySelector('[data-i18n="u2-title"]').textContent=dynamics.title[lang];document.querySelector('[data-i18n="u2"]').textContent=dynamics.detail[lang];}
  }
}
const svgNS='http://www.w3.org/2000/svg';
function svgElement(tag,attrs){const el=document.createElementNS(svgNS,tag);for(const [k,v]of Object.entries(attrs))el.setAttribute(k,v);return el;}
function renderMechanism(){
  const cups=document.getElementById('cups'), labels=document.getElementById('vessel-numbers');cups.replaceChildren();labels.replaceChildren();
  for(let i=0;i<5;i++){
    const x=115+i*145;const g=svgElement('g',{});const cue=i===recipient&&(mode==='M0'||phase==='A');
    g.append(svgElement('path',{d:`M${x-32} 139L${x-28} 246Q${x} 257 ${x+28} 246L${x+32} 139`,fill:'#fff',stroke:'#a9b2be','stroke-width':'2'}));
    g.append(svgElement('path',{d:`M${x-30} 176L${x-28} 245Q${x} 253 ${x+28} 245L${x+30} 176Z`,fill:cue?'#8e80d0':'url(#liquid)',opacity:cue?'.83':'1'}));
    g.append(svgElement('ellipse',{cx:x,cy:139,rx:32,ry:7,fill:'#f4f6fa',stroke:'#a9b2be','stroke-width':'2'}));cups.append(g);
    const l=svgElement('text',{x,y:280,'text-anchor':'middle',class:'vessel-label'});l.textContent=String(i+1).padStart(2,'0');labels.append(l);
  }
  const source=document.getElementById('source-tool');source.setAttribute('visibility',phase==='A'?'visible':'hidden');source.setAttribute('transform',`translate(${(recipient-2)*145-25},0)`);
  document.getElementById('window-label').textContent=lang==='en'?'shared low window':'共享低观察窗';
  document.getElementById('schematic-stage').textContent=phase==='A'?(lang==='en'?'OPERATION A / RECIPIENT CUE':'操作 A / 目标线索'):phase==='wait'?(lang==='en'?'WAIT / OBSERVATION':'等待 / 观察'):(lang==='en'?'OPERATION B / RECALL':'操作 B / 回忆');
  document.getElementById('operation-caption').textContent=lang==='en'?'Operation A':'操作 A';
  const s=lang==='en'?`Recipient ${recipient+1}. `:`目标器皿 ${recipient+1}。`;
  const message=phase==='A'?(lang==='en'?'The recipient cue is visible during operation A.':'操作 A 期间目标线索可见。'):mode==='M0'?(lang==='en'?'The persistent dye still identifies the recipient.':'持久染料仍能指示目标器皿。'):(lang==='en'?'The five vessel appearances match; the policy must recall the recipient.':'五个器皿外观相同，策略须回忆目标。');
  document.getElementById('mechanism-readout').textContent=s+message;
  document.getElementById('mechanism-svg-title').textContent=lang==='en'?'Memory cue and shared physical occlusion':'记忆线索与共享物理遮挡';
  document.getElementById('mechanism-svg-desc').textContent=message+(lang==='en'?' Conceptual illustration only.':'仅为概念示意。');
}
function renderEvidence(){
  if(!snapshot)return;
  const list=document.getElementById('evidence-list');list.replaceChildren();
  const rows=snapshot.evidence.filter(row=>evidenceFilter==='all'||row.kind===evidenceFilter||row.status===evidenceFilter);
  const statusText={limited:lang==='en'?'LIMITED SCOPE':'限定范围',fail:'FAIL',pending:lang==='en'?'PENDING':'待完成'};
  rows.forEach(row=>{
    const card=element('article','evidence-card');card.dataset.evidenceId=row.id;
    const top=element('div','evidence-card-top');top.append(element('span','',row.id),element('span','tag '+(row.status==='pending'?'open':row.status),statusText[row.status]));
    card.append(top,element('h3','',row.title[lang]),element('p','',row.detail[lang]),element('div','denominator',row.denominator[lang]));
    if(row.artifact){if(!/^data\/evidence\/[a-z0-9-]+\.json$/.test(row.artifact))throw new Error('Unsupported public artifact path');const a=element('a','artifact-link',lang==='en'?'Read audit subset →':'查看审计子集 →');a.href=row.artifact;card.append(a);}
    list.append(card);
  });
  document.getElementById('evidence-count').textContent=lang==='en'?`${rows.length} records`:`${rows.length} 条记录`;
}
document.getElementById('language-toggle').addEventListener('click',()=>{lang=lang==='en'?'zh':'en';updateUrl();renderText();});
document.querySelectorAll('[data-mode]').forEach(btn=>btn.addEventListener('click',()=>{mode=btn.dataset.mode;document.querySelectorAll('[data-mode]').forEach(b=>{b.classList.toggle('selected',b===btn);b.setAttribute('aria-pressed',String(b===btn));});renderMechanism();}));
document.querySelectorAll('[data-phase]').forEach(btn=>btn.addEventListener('click',()=>{phase=btn.dataset.phase;document.querySelectorAll('[data-phase]').forEach(b=>{b.classList.toggle('selected',b===btn);b.setAttribute('aria-pressed',String(b===btn));});renderMechanism();}));
document.getElementById('recipient-select').addEventListener('change',e=>{recipient=Number(e.target.value);renderMechanism();});
document.querySelectorAll('[data-filter]').forEach(btn=>btn.addEventListener('click',()=>{evidenceFilter=btn.dataset.filter;document.querySelectorAll('[data-filter]').forEach(b=>{b.classList.toggle('selected',b===btn);b.setAttribute('aria-pressed',String(b===btn));});renderEvidence();}));
function activeView(view){document.querySelectorAll('#report-nav a').forEach(a=>{const active=a.dataset.view===view;a.classList.toggle('active',active);if(active)a.setAttribute('aria-current','location');else a.removeAttribute('aria-current');});}
document.querySelectorAll('a[href^="#"]').forEach(a=>a.addEventListener('click',()=>{const view=a.getAttribute('href').slice(1);if(views.includes(view)){updateUrl(view,true);activeView(view);}}));
const observer=new IntersectionObserver(entries=>{const visible=entries.filter(e=>e.isIntersecting).sort((a,b)=>a.boundingClientRect.top-b.boundingClientRect.top);if(visible.length)activeView(visible[0].target.id);},{rootMargin:'-15% 0px -60% 0px',threshold:0});views.forEach(view=>observer.observe(document.getElementById(view)));
function initialView(){const u=new URL(location.href);const v=u.searchParams.get('view')||u.hash.slice(1);if(views.includes(v)){document.getElementById(v).scrollIntoView({behavior:'instant'});activeView(v);}}
window.addEventListener('popstate',()=>{lang=new URLSearchParams(location.search).get('lang')==='zh'?'zh':'en';renderText();initialView();});
renderText();requestAnimationFrame(initialView);
fetch('data/progress.json',{cache:'no-cache'}).then(r=>{if(!r.ok)throw new Error('Snapshot unavailable');return r.json();}).then(data=>{
  if(data.schema!=='chemrmbench-public-progress-v1'||data.benchmark_complete!==false||data.conference_ready!==false||!Array.isArray(data.evidence))throw new Error('Unexpected snapshot contract');
  snapshot=data;document.getElementById('demo-count').textContent=data.qualified_expert_demonstrations.actual;document.getElementById('fit-count').textContent=data.matched_native_VLA_fits.actual;document.getElementById('paper-pages').textContent=data.paper.draft_pages;renderText();
}).catch(()=>{const p=element('p','',lang==='en'?'Could not load the evidence snapshot. Open the public JSON resource below.':'证据快照加载失败，请查看下方公开 JSON 资源。');const a=element('a','',lang==='en'?'Progress JSON':'进展 JSON');a.href='data/progress.json';document.getElementById('evidence-list').replaceChildren(p,a);});
