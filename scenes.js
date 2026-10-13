'use strict';
const node=id=>document.getElementById(id);let data=null,current='a1',camera=null;
function make(tag,text='',cls=''){const n=document.createElement(tag);n.textContent=text;if(cls)n.className=cls;return n;}
function localAsset(path,extension){if(typeof path!=='string'||!new RegExp('^assets/history/[a-z0-9_-]+\\.'+extension+'$','i').test(path))throw Error('invalid media asset');return path;}
function renderBottleFrame(){
  const phase=node('bottleRun').value,frames=data.bottle_probe.frames[phase],frame=frames[Number(node('bottleCursor').value)];
  if(!frame||!/^assets\/native-v79\/(parent|child)-[0-9]{5}\.jpg$/.test(frame.image))throw Error('invalid native image');
  node('bottleImage').src=frame.image;
  node('bottleFrameLabel').textContent=(phase==='parent'?'不中断基线':'任务起点冷重建后执行')+' · 第 '+frame.command_index.toLocaleString('zh-CN')+' 步 · 此进程原生时间 '+frame.native_time_s.toFixed(3)+' s';
}
function renderBottle(){
  const p=data.bottle_probe;
  if(!p||p.status!=='PASS_SCOPED_NATIVE_BOTTLE_PAIR'||p.scientific_admission!==false)throw Error('native bottle evidence unavailable');
  const stats=node('bottleStats');stats.replaceChildren();
  for(const [label,value]of[['每次实际控制步','13,427'],['每次已封存阶段','8 / 8'],['每次 RGBD 实测','15 帧'],['任务中的位姿写入','0 次']]){const n=make('div','','mini');n.append(make('strong',value),make('span',label));stats.append(n);}
  const rows=node('bottleComparison');rows.replaceChildren();
  for(const [phase,label]of[['parent','不中断基线'],['child','任务起点冷重建后执行']]){
    const x=p.phases[phase],tr=make('tr');
    for(const text of[label,x.final_return_error_mm.toFixed(3)+' mm',(x.transport_bilateral_contact_fraction*100).toFixed(2)+'%',x.maximum_relative_displacement_mm.toFixed(3)+' mm',x.close_command_to_bilateral_contact_ms.map(n=>n.toFixed(1)).join('–')+' ms'])tr.append(make('td',text));
    rows.append(tr);
  }
  const r=p.restore;
  node('bottleRestore').textContent='冷恢复覆盖 '+r.rigid_objects+' 刚体 / '+r.articulations+' 关节系统，30 个瞬态样本均通过。全瞬态最大漂移 '+r.maximum_position_error_mm.toFixed(3)+' mm / '+r.maximum_orientation_error_deg.toFixed(3)+'°；原门槛 1 mm / 0.5° 保留。';
  node('bottleRun').addEventListener('change',renderBottleFrame);node('bottleCursor').addEventListener('input',renderBottleFrame);renderBottleFrame();
}
function renderMidTask(){
  const p=data.mid_task_probe;
  if(!p||p.status!=='PASS_SCOPED_NATIVE_MID_TASK_BOTTLE_RESUME'||p.scientific_admission!==false)throw Error('mid task evidence unavailable');
  const pictures=node('midTaskImages');pictures.replaceChildren();
  for(const frame of p.frames){
    if(!/^assets\/native-v80\/(parent|child)-[0-9]{5}\.jpg$/.test(frame.image))throw Error('invalid mid task image');
    const f=make('figure'),img=make('img');img.src=frame.image;img.alt=frame.label;img.loading='lazy';f.append(img,make('figcaption',frame.label));pictures.append(f);
  }
  const r=p.restore,x=p.phases.child;
  node('midTaskResult').textContent='父阶段和检查点摘要核验保持一致；恢复游标 '+p.restored_command_cursor.toLocaleString('zh-CN')+'，实际只执行剩余 '+p.tail_commands.toLocaleString('zh-CN')+' 步。最终转盘放回误差 '+x.placement_error_mm.toFixed(3)+' mm。全部恢复瞬态最大漂移 '+r.maximum_position_error_mm.toFixed(3)+' mm / '+r.maximum_orientation_error_deg.toFixed(3)+'°。';
  const rows=node('midTaskComparison');rows.replaceChildren();
  for(const [phase,label]of[['parent','前五阶段 → 天平'],['child','恢复后剩余阶段 → 转盘']]){const x=p.phases[phase],tr=make('tr');for(const v of[label,x.placement_error_mm.toFixed(3)+' mm',(x.transport_bilateral_contact_fraction*100).toFixed(2)+'%',x.maximum_relative_displacement_mm.toFixed(3)+' mm'])tr.append(make('td',v));rows.append(tr);}
}
function renderMemory(){
  const p=data.memory_probe;
  if(!p||p.status!=='PASS_SCOPED_PRESERVED_OBSERVATION_MEMORY_READOUT'||p.new_native_trials!==0||p.operation_timing_measured_this_run!==false)throw Error('memory evidence scope');
  const pictures=node('memoryImages');pictures.replaceChildren();
  for(const frame of p.frames){
    if(!/^assets\/native-v82\/(past-early|past-late|current)\.jpg$/.test(frame.image))throw Error('invalid memory image');
    const f=make('figure'),img=make('img');img.src=frame.image;img.alt=frame.label;img.loading='lazy';f.append(img,make('figcaption',frame.label));pictures.append(f);
  }
  const rows=node('memoryComparison');rows.replaceChildren();
  for(const x of p.readout_cases){const tr=make('tr');for(const value of['保留记忆 '+(x.case_id+1),x.past_public_observation_s.toFixed(3)+' s',x.remembered_public_observation_s.toFixed(3)+' s',x.selected_deadline_s+' s',x.proposed_skill_start_after_resume_s.toFixed(3)+' s'])tr.append(make('td',value));rows.append(tr);}
  const tr=make('tr');for(const value of['清空记忆 · 共同输入调用一次','—','未编造历史','等待','未排程'])tr.append(make('td',value));rows.append(tr);
  node('memoryResult').textContent='共 '+p.model_calls+' 次真实 Astra 调用，已知计费 '+p.known_billed_tokens.toLocaleString('zh-CN')+' tokens。记忆摘要绑定原物理检查点与控制器游标；恢复读出没有附上旧图片。新增物理执行 0 次，操作截止时间尚未在本轮执行。';
}
function renderNativeMemory(){
  const choices=data.native_memory_conditions||[data.native_memory_probe],select=node('nativeMemoryCondition');
  if(!select.options.length){for(const [i,p]of choices.entries()){const o=make('option',p.label||'橙色 · 恢复后 16 秒');o.value=String(i);select.append(o);}select.value=String(choices.length-1);select.onchange=renderNativeMemory;}
  const p=choices[Number(select.value)];
  if(!p||p.status!=='PASS_SCOPED_NATIVE_AGENT_MEMORY_TIMED_CONTACT'||p.scientific_admission!==false||p.simulation_paused_for_inference!==true)throw Error('native memory evidence scope');
  const pictures=node('nativeMemoryImages');pictures.replaceChildren();
  for(const frame of p.frames){
    if(!/^assets\/native-v(83|84)\/(cue|current|finished)\.jpg$/.test(frame.image))throw Error('invalid native memory image');
    const f=make('figure'),img=make('img');img.src=frame.image;img.alt=frame.label;img.loading='lazy';f.append(img,make('figcaption',frame.label));pictures.append(f);
  }
  const stats=node('nativeMemoryStats');stats.replaceChildren();
  for(const [label,value]of[['要求恢复后接触',p.desired_contact_after_resume_s+' s'],['实际接触采样区间',p.contact_after_resume_bounds_s.map(x=>x.toFixed(3)).join('–')+' s'],['实际放回误差',p.placement_error_mm.toFixed(3)+' mm'],['只执行剩余阶段',p.tail_commands.toLocaleString('zh-CN')+' 步']]){const n=make('div','','mini');n.append(make('strong',value),make('span',label));stats.append(n);}
  node('nativeMemoryResult').textContent='恢复后的保留记忆提案实际驱动技能，清空记忆选择等待；仅保留条件执行物理余程。接触误差区间 '+p.error_interval_ms.map(x=>x.toFixed(1)).join('–')+' ms，整体区间满足预设 ±20 ms。读出期间仿真暂停，宿主等待 '+p.host_readout_elapsed_s.toFixed(1)+' s。三次真实调用，共 '+p.known_billed_tokens.toLocaleString('zh-CN')+' 已知 tokens；不是实时响应验收。';
  node('nativeMemoryReceipt').href=p.receipt;node('nativeMemoryReceipt').textContent=p.id+' 独立物理验收、实际计时和资源摘要';
}
function timingTimeline(p){
  const ns='http://www.w3.org/2000/svg',svg=document.createElementNS(ns,'svg');svg.setAttribute('viewBox','0 0 900 154');svg.setAttribute('role','img');svg.setAttribute('aria-label',p.label+'：模型调用、剩余等待、技能执行与实际接触的原生时间轴');
  const x=t=>60+t/17*780,add=(tag,attrs,text)=>{const n=document.createElementNS(ns,tag);for(const[k,v]of Object.entries(attrs))n.setAttribute(k,String(v));if(text)n.textContent=text;svg.append(n);};
  add('line',{x1:60,x2:840,y1:106,y2:106,stroke:'#bac8c4'});
  for(const t of[0,5,10,15]){add('line',{x1:x(t),x2:x(t),y1:102,y2:111,stroke:'#73847d'});add('text',{x:x(t),y:131,'text-anchor':'middle',fill:'#52675e','font-size':13},t+' s');}
  const segments=[[0,p.native_readout_elapsed_s,'#8eaecb'],[p.native_readout_elapsed_s,p.actual_skill_start_after_resume_s,'#ceddd7'],[p.actual_skill_start_after_resume_s,p.contact_after_resume_bounds_s[1],p.requested_deadline_pass?'#397d63':'#b45643']];
  for(const[a,b,color]of segments)add('rect',{x:x(a),y:59,width:Math.max(1,x(b)-x(a)),height:28,rx:3,fill:color});
  add('line',{x1:x(10),x2:x(10),y1:36,y2:100,stroke:'#263e34','stroke-dasharray':'4 4'});add('text',{x:x(10),y:24,'text-anchor':'middle','font-size':13,fill:'#263e34'},'要求接触 10 s');
  add('circle',{cx:x(p.contact_after_resume_bounds_s[1]),cy:73,r:5,fill:'#182f25'});
  add('text',{x:60,y:151,'font-size':12,fill:'#53675f'},'蓝：模型调用期间积分　浅绿：等待　深色：技能执行至实际接触（采样区间）');
  node('continuousTimingTimeline').replaceChildren(svg);
}
function renderContinuousTiming(){
  const choices=data.continuous_timing_probes,select=node('continuousTimingCondition');
  if(!Array.isArray(choices)||choices.length!==2)throw Error('continuous timing evidence unavailable');
  if(!select.options.length){for(const[i,p]of choices.entries()){const o=make('option',p.label);o.value=String(i);select.append(o);}select.onchange=renderContinuousTiming;}
  const p=choices[Number(select.value)];
  if(p.scientific_admission!==false||p.simulation_paused_for_inference!==false||p.real_time_speed_assumed!==false)throw Error('continuous timing scope');
  const pictures=node('continuousTimingImages');pictures.replaceChildren();
  for(const frame of p.frames){if(!/^assets\/native-v(85|86)\/(cue|current|finished)\.jpg$/.test(frame.image))throw Error('invalid continuous native image');const f=make('figure'),img=make('img');img.src=frame.image;img.alt=frame.label;img.loading='lazy';f.append(img,make('figcaption',frame.label));pictures.append(f);}
  const stats=node('continuousTimingStats');stats.replaceChildren();
  for(const[label,value]of[['调用期间原生积分',p.physical_callbacks_during_readout.toLocaleString('zh-CN')+' 步 / '+p.native_readout_elapsed_s.toFixed(3)+' s'],['实际接触采样区间',p.contact_after_resume_bounds_s.map(x=>x.toFixed(3)).join('–')+' s'],['瓶体放回误差',p.placement_error_mm.toFixed(3)+' mm'],['计时准入',p.requested_deadline_pass?'通过 ±20 ms':'失败 · 晚于时间窗']]){const n=make('div','','mini');n.append(make('strong',value),make('span',label));stats.append(n);}
  const detail=p.requested_deadline_pass?'模型返回后只等待剩余 '+p.remaining_wait_ticks.toLocaleString('zh-CN')+' 步；调用期间的时间只计入一次。':'基线在返回后另等完整 '+p.remaining_wait_ticks.toLocaleString('zh-CN')+' 步；计时误差 '+p.error_interval_ms.map(x=>x.toFixed(1)).join('–')+' ms。漏记的原生时间解释了误差，剩余采样残差 '+p.error_minus_readout_ms.map(x=>x.toFixed(3)).join('–')+' ms；正常准入会拒绝这一过期提案。';
  node('continuousTimingResult').textContent=detail+' 模型调用宿主时间 '+p.host_readout_elapsed_s.toFixed(2)+' s，原生时间 '+p.native_readout_elapsed_s.toFixed(3)+' s，分别记录。清空记忆诊断在 GPU 工作进程结束后使用原封存输入调用一次，不参与物理调用延迟。';
  node('continuousTimingReceipt').href=p.receipt;node('continuousTimingReceipt').textContent=p.id+' 独立计时复核与原始数据摘要校验值';timingTimeline(p);
  const rows=node('continuousTimingComparison');rows.replaceChildren();
  for(const c of choices){const tr=make('tr');for(const v of[c.id+' · '+c.label,c.native_readout_elapsed_s.toFixed(3)+' / '+c.host_readout_elapsed_s.toFixed(2)+' s',c.contact_after_resume_bounds_s.map(x=>x.toFixed(3)).join('–')+' s',c.requested_deadline_pass?'通过':'失败',c.placement_error_mm.toFixed(3)+' mm'])tr.append(make('td',v));rows.append(tr);}
}
function renderScene(){const scene=data.scenes.find(s=>s.id===current)||data.scenes[0];current=scene.id;const view=scene.views.find(v=>v.id===camera)||scene.views[0];camera=view.id;node('sceneTitle').textContent=scene.station+' 站 · '+scene.title;node('sceneChoices').replaceChildren();for(const s of data.scenes){const b=make('button',s.station+' · '+s.title);b.type='button';b.classList.toggle('active',s.id===current);b.setAttribute('aria-pressed',String(s.id===current));b.addEventListener('click',()=>{current=s.id;camera=null;renderScene();});node('sceneChoices').append(b);}node('cameraChoices').replaceChildren();for(const v of scene.views){const b=make('button',v.label);b.type='button';b.classList.toggle('active',v.id===camera);b.setAttribute('aria-pressed',String(v.id===camera));b.addEventListener('click',()=>{camera=v.id;renderScene();});node('cameraChoices').append(b);}const video=node('sceneVideo');video.pause();video.poster=localAsset(view.poster,'jpg');video.src=localAsset(view.video,'mp4');video.load();node('sceneVideoNote').textContent=scene.revision+' · '+view.frames+' 帧 / '+view.fps+' fps · '+view.duration_s.toFixed(1)+' 秒 · '+view.label;node('sceneScope').textContent=scene.scope+' '+scene.demo_acceptance;const digests=node('sceneDigests');digests.replaceChildren();for(const text of['渲染记录：'+scene.render_manifest_sha256,'位姿核验：'+scene.pose_checks_sha256,'当前视频：'+view.video_sha256])digests.append(make('p',text));}
function renderRestore(){
  const r=data.reconstruction,p=data.native_probe;
  const nativePassed=p&&p.status==='PASS_SCOPED_RELEASED_RIGID_RECONSTRUCTION';
  if(nativePassed){
    const c=p.fresh_process;
    node('nativeProbeState').textContent='V78 原场景空载阶段恢复已实测：同进程与新进程都覆盖 '+c.rigid_objects+' 个刚体、'+c.articulations+' 个关节系统，每个恢复物理步均保存全部登记实体。30 步后最大漂移 '+c.maximum_position_error_mm.toFixed(3)+' mm / '+c.maximum_orientation_error_deg.toFixed(3)+'°，阈值仍为 1 mm / 0.5°。恢复后夹爪完成约 '+c.measured_gripper_movement_mm.toFixed(1)+' mm 闭合再张开。工作进程采用明确记录的受控终止，SDK 正常退出尚未通过；跨进程原生时钟不连续。此结果不覆盖携瓶、倒液、完整长链或时间精确操作验收。';
  }else if(p){
    node('nativeProbeState').textContent='完整场景原生核验：启动等待 '+p.wall_s.toFixed(1)+' 秒后超时，未进入物理测量；冷恢复未启动。失败记录保留。';
  }
  const rows=[
    ['分阶段证据保存','V74/V75 已提交阶段、摘要与持久化检查','已实现 · 存储完整性'],
    ['场景位姿重建与回放','本页 6 个历史回放 · 30 个已核帧机位','已实现 · 不积分物理'],
    ['局部携物恢复后续跑','历史 A 站保存 → 恢复 → 放回实测','限定通过 · 运动学支持'],
    ['原场景空载物理恢复',nativePassed?'本轮覆盖 56 刚体 / 9 关节系统；30 步全实体状态': '历史携物整体漂移与覆盖不足',nativePassed?'限定通过 · 原阈值保留':'未通过'],
    ['实际瓶体任务',data.bottle_probe?'V79 两次 13,427 步，实际接触与放回核验':'真实物体任务待补',data.bottle_probe?'任务起点恢复后取放通过':'尚未验收'],
    ['语义阶段续采接入',data.mid_task_probe?'V80 天平释放后保存 → 冷重建 → 只跑剩余 5,507 步':'任务起点恢复与存储验证',data.mid_task_probe?(data.native_memory_probe?'阶段续跑与语义记忆接入通过':'刚体释放边界续跑通过 · agent 记忆待补'):'中途阶段续跑待补'],
    ['新进程重建',nativePassed?'保存父阶段 → 终止进程 → 新实例恢复 → 实测技能':'缺少独立匹配原生验收',nativePassed?'限定通过 · 时钟分别记录':'尚未验证'],
    ['完整长任务与精确操作时间','携物、事件记忆、物理事件锚点尚未接入本轮恢复','尚未验收'],
    ['PBD / 液体状态恢复','当前适配器拒绝该类 checkpoint','未实现']
  ];
  if(p&&p.child_retry)rows.splice(6,0,['失败子阶段重试','父阶段数据与状态保留；只重做失败子阶段',p.child_retry.status==='PASS_NATIVE_FAILED_CHILD_RETRY'?'空载原生实测通过':'仍待验收']);
  node('restoreMatrix').replaceChildren();
  for(const row of rows){const tr=make('tr');for(const text of row)tr.append(make('td',text));node('restoreMatrix').append(tr);}
  const nums=node('restoreNumbers');nums.replaceChildren();
  for(const [label,value]of[['历史局部相对位置误差',r.local_relative_position_error_mm.toFixed(4)+' mm'],['历史局部相对姿态误差',r.local_relative_orientation_error_deg.toFixed(4)+'°'],['历史不中断放回误差',r.baseline_placement_mm.toFixed(4)+' mm'],['历史恢复后放回误差',r.resumed_placement_mm.toFixed(4)+' mm']]){const n=make('div','','mini');n.append(make('strong',value),make('span',label));nums.append(n);}
  node('restoreFailure').textContent='历史携物整体恢复 FAIL 保留：研杵旋转漂移 '+r.pestle_orientation_drift_deg.toFixed(3)+'° > '+r.original_orientation_limit_deg+'°；当时恢复 30 tick 后只有 '+r.settled_tracked_bodies+'/'+r.checkpoint_bodies+' 个刚体被逐 tick 覆盖。本轮空载结果不覆盖这项历史失败。';
}
async function load(){try{const response=await fetch('data/reconstruction.json',{cache:'no-store'});if(!response.ok)throw Error('source unavailable');data=await response.json();if(data.schema!=='chemrm-preserved-scenes-v1'||data.scenes.length!==6||data.reconstruction.scientific_admission!==false)throw Error('evidence schema');node('recordDate').textContent='本轮核验 '+new Intl.DateTimeFormat('zh-CN',{timeZone:'Asia/Shanghai',dateStyle:'short',timeStyle:'medium'}).format(new Date(data.verified_at_utc))+' · 恢复检索 '+data.history_message_count.toLocaleString('zh-CN')+' 条可见历史消息';renderScene();renderRestore();renderBottle();renderMidTask();renderMemory();renderNativeMemory();renderContinuousTiming();}catch(error){node('sceneError').hidden=false;node('sceneError').textContent='证据索引读取失败。静态预览保留；不能据此推断重建、恢复或实验已通过。';}}
load();
