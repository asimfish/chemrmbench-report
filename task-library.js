const $=id=>document.getElementById(id);
const labels={planned:'尚未原生采集',collecting:'采集中',batch_collected:'已采满 20 个 seed',smoke_passed:'原生冒烟通过',needs_expert_fix:'需修复专家'};
const stageNames={tilt_started:'倾角越过60°',tilt_ended:'倾角回落60°',open:'开启',hold:'保持',release:'松爪',ready:'就绪',wait_cue:'提示出现',press:'物理按压',endpoint_observed:'颜色端点',stopped:'完成',cue_observed:'提示熄灭',retention_end:'保留结束',approach:'接近',grasp:'抓取',lift:'提起',transport:'运送',place_release:'放置与松爪',regrasp:'再次抓取',return:'返回',retreat:'撤退'};
async function refreshStats(){
 try{
  let data;
  const stamp=Date.now();
  for(const url of ['https://raw.githubusercontent.com/asimfish/chemrmbench-report/main/data/task-library.json?t='+stamp,'data/task-library.json?t='+stamp]){
   try{const signal=typeof AbortSignal!=='undefined' && typeof AbortSignal.timeout==='function'?AbortSignal.timeout(8000):undefined;const response=await fetch(url,{cache:'no-store',signal});if(!response.ok)continue;data=await response.json();if(Array.isArray(data.tasks))break;data=null;}catch(error){/* Retain the published snapshot as a fallback. */}
  }
  if(!data)throw Error('statistics unavailable');
  $('nativeCount').textContent=data.native_tasks_with_dataset;$('attemptCount').textContent=data.dataset_attempts;
  $('updated').textContent='记录更新时间：'+new Date(data.updated_at_utc).toLocaleString('zh-CN',{hour12:false})+' · 统计每分钟刷新';
  const pilot=data.pipeline_pilot;
  if(data.ssd_staging && $('ssdStaging')){
   const r=data.ssd_staging;$('ssdStaging').textContent='新增数据保存在本机持久 SSD，并逐条回传 NAS；以下进度不与任务卡数量相加。'+r.cohorts.map(c=>`${c.label} 已关闭 ${c.closed_attempts}/${c.expected_attempts} 条，已回传 ${c.mirrored_closed_attempts||0} 条，整批录像复核${c.batch_recording_accepted?'通过':'待完成'}`).join('；')+'。';
  }
  if(data.training_expansion && $('trainingExpansion')){
   const r=data.training_expansion;$('trainingExpansion').textContent=`远程训练数据扩采：已回传并验收 ${r.received_and_validated_attempts}/${r.target_new_attempts} 条，${r.admitted_successes} 条通过独立训练准入。严格 V2 等价未通过；远程数据仅用于训练，专家、消融和评测主表均在本机产生。`;
  }
  if(data.current_t6 && $('t6CurrentProgress')){
   const r=data.current_t6;$('t6CurrentProgress').textContent=`指导7 全臂修复：${r.moving_colliders} 个机器人碰撞体，CPU 连续路径资格 ${r.cpu_passed?'3/3通过':'进行中'}${r.minimum_clearance_mm!==null?'，最小运动界后余量 '+r.minimum_clearance_mm.toFixed(2)+' mm（含1mm跟踪余量）':''}。搅拌器保持原位；原生资格 ${r.native_passed}/${r.native_required} 通过，已尝试 ${r.native_attempts} 条，原始力上限仍为 ${r.raw_force_limit_n} N。${r.native_all_passed?'已满足主批量前置资格。':'尚未满足主批量前置资格。'}`;
   if(r.native_startup_errors)$('t6CurrentProgress').textContent+=`${r.native_startup_errors} 条在首个任务动作前报错，不能计为物理安全通过。`;
  }
  if(pilot && $('pipelineNotice')){
   $('pipelineNotice').textContent=`CPU 示意环境结果仅验证接口。T1 DP 链路试点：${pilot.training_updates} 次更新，训练累计 ${pilot.training_gpu_hours.toFixed(3)} GPU·小时（含失败）；检查点${pilot.checkpoint_saved?'已保存':'待保存'}，公开输入 CPU 推理${pilot.cpu_public_inference_passed?'通过':'待验收'}。原生动作轨道已记录 ${pilot.native_action_attempts}/${pilot.native_action_required} 条，${pilot.pipeline_complete?'链路已验收':'链路尚未验收'}。试点不作为基线数字；尚未调用 LLM/VLM。`;
  }
  const protocol=data.evaluation_protocol;
  if(protocol && $('evalCards')){
   const names=Object.fromEntries(data.tasks.map(t=>[t.id,t.number+' · '+t.title]));
   $('evalCards').replaceChildren(...protocol.f0_cpu_contracts.map(task=>{
    const card=document.createElement('article');card.className='task';
    const title=document.createElement('h3');title.textContent=names[task.task_id]||task.task_id;
    const cpu=document.createElement('p');
    const count=key=>task[key]?`${task[key].successes}/${task[key].attempts}`:'待测';
    cpu.textContent=`CPU 示意合同${task.superseded?'（T4-v1 旧设计，不能代表 v2）':''}：特权上界 ${count('privileged_expert')} · 固定响应下界 ${count('ablation')} · 公开观测规则 ${count('public_heuristic')}`;
    const native=document.createElement('p');const rows=protocol.native_public_observation.filter(r=>r.task_id===task.task_id);
    native.textContent=rows.length?'原生公开观测：'+rows.map(r=>`${r.superseded?'T4-v1 已停用：':''}${r.clock_mode} ${r.successes}/${r.attempts}，录像${r.recording_accepted?'已复核':'待复核'}`).join('；'):'原生公开观测：排在主批量与消融之后，尚未开始。';
    card.append(title,cpu,native);return card;
   }));
  }
  $('taskCards').replaceChildren(...data.tasks.map(task=>{
   const card=document.createElement('article');card.className='task';
   const top=document.createElement('div');top.className='task-top';
   const number=document.createElement('span');number.className='number';number.textContent=task.number;
   const badge=document.createElement('span');badge.className='badge '+task.status;badge.textContent=labels[task.status]||task.status;top.append(number,badge);
   const title=document.createElement('h3');title.textContent=task.title;
   const dimension=document.createElement('p');dimension.textContent=task.dimension;
   const progress=document.createElement('div');progress.className='progress';const fill=document.createElement('i');fill.style.width=Math.min(100,task.dataset_unique_seeds/20*100)+'%';progress.append(fill);
   const counts=document.createElement('p');counts.className='task-metrics';counts.textContent=`${task.dataset_unique_seeds} / 20 个唯一 seed　·　随机化尝试 ${task.dataset_attempts}`;
   const rate=document.createElement('p');rate.textContent=task.dataset_attempts?`验收成功 ${task.successes} / ${task.dataset_attempts}（${(task.success_rate*100).toFixed(1)}%） · 失败 ${task.status_counts.fail||0} · 报错 ${task.status_counts.error||0}`:'随机化成功率尚未测量';
   const evidence=document.createElement('p');evidence.textContent=`已复核随机化录像 ${task.verified_dataset_attempts} 条 · 资格检查 ${task.qualification_attempts} 次，验收成功 ${task.qualification_safe_successes} 次`+(task.calibration_attempts?` · 历史专家校准 ${task.calibration_attempts} 条（成功 ${task.calibration_status_counts.success||0} / 失败 ${task.calibration_status_counts.fail||0} / 报错 ${task.calibration_status_counts.error||0}）`:'')+(task.memory_gate_attempts?` · 像素门槛前缀 ${task.memory_gate_attempts} 条`:'')+(task.id==='delayed_cue_memory'?` · 提示后像素门槛 ${task.memory_layout_gates_passed||0}/3 布局`:'')+(task.render_diagnostic_attempts?` · 另有 ${task.render_diagnostic_attempts} 次短前缀渲染诊断`:'');
   card.append(top,title,dimension,progress,counts,rate,evidence);
   for(const field of ['revision_note','rendering_note','initial_posture_note','fixture_note','observation_note']){
    if(task[field]){const note=document.createElement('p');note.textContent=task[field];card.append(note);}
   }
   if(task.superseded_history){const h=task.superseded_history;const note=document.createElement('p');note.textContent=`已停用 T4-v1 历史记录：主批量 ${h.main_successes}/${h.main_attempts}，消融 ${h.ablation_successes}/${h.ablation_attempts}，公开观测评测 ${h.evaluation_attempts} 条；均不计入 v2 进度。`;card.append(note);}
   if(task.qualification_gate){
    const gate=task.qualification_gate;const note=document.createElement('p');
    note.textContent=`历史手部预检与资格失败：针对全场景障碍物的 CPU 手部路径预检${gate.whole_scene_transit_screen_passed?'通过':'待通过'}${gate.minimum_transit_clearance_mm!==null?'，手部最小余量 '+gate.minimum_transit_clearance_mm.toFixed(2)+' mm':''}；当时未覆盖手臂连杆。局部面板指垫接触${gate.local_panel_contact_approved?'已确认':'待确认'}；原生资格 ${gate.native_passed}/${gate.native_required} 通过（已尝试 ${gate.native_attempts} 条）${gate.maximum_raw_global_force_n!==null?'，全机器人原始力峰值 '+gate.maximum_raw_global_force_n.toFixed(2)+' N':''}，上限 ${gate.raw_force_limit_n} N。${gate.all_native_qualifications_passed?'主批量已获准入。':'尚未获主批量准入。'}`;
    card.append(note);
   }
   if(task.evaluation_attempts){const note=document.createElement('p');note.textContent=`公开观测 held-out 评测：${task.evaluation_successes}/${task.evaluation_attempts}成功，独立于专家采集和消融。`;card.append(note);}
   if(task.ablation_target_attempts){const ablation=document.createElement('p');ablation.textContent=task.ablation_attempts?`固定响应消融：已完成 ${task.ablation_attempts}/${task.ablation_target_attempts}，成功 ${task.ablation_successes}，失败 ${task.ablation_status_counts.fail||0}，报错 ${task.ablation_status_counts.error||0}（与主专家分开统计）。`:'固定响应消融：待采集 10 个匹配 seed。';card.append(ablation);}
   if(task.runtime_rejections){const runtime=document.createElement('p');runtime.textContent=`粒子运行时拒绝 ${task.runtime_rejections} 次；原始测量保留，未计为成功。`;card.append(runtime);}
   if(task.primary_cohort){const cohort=document.createElement('p');cohort.textContent=`固定配置批次：成功 ${task.primary_cohort.successes}/20，失败 ${task.primary_cohort.failures}，报错 ${task.primary_cohort.errors}。`;card.append(cohort);}
   return card;
  }));
 }catch(error){$('updated').textContent='暂未读取到最新统计，请稍后刷新；视频仍可观看。';}
}
async function loadVideos(){
 const response=await fetch('data/native-video-index.json');if(!response.ok)throw Error('video index unavailable');
 const videos=await response.json();const select=$('taskSelect');
 for(const item of videos){const option=document.createElement('option');option.value=item.id;option.textContent=item.title;select.append(option);}
 const requested=new URLSearchParams(window.location.search).get('task');
 if(videos.some(item=>item.id===requested))select.value=requested;
 function choose(){
  const item=videos.find(v=>v.id===select.value)||videos[0];
  $('station').src=item.station_a;$('wrist').src=item.wrist;
  $('videoScope').textContent=item.scope;
  $('stageButtons').replaceChildren(...item.stages.map(stage=>{
   const button=document.createElement('button');button.textContent=(stageNames[stage.name]||stage.name)+' · '+stage.time_s.toFixed(1)+'s';
   button.onclick=()=>{for(const id of ['station','wrist'])$(id).currentTime=Math.min(stage.time_s,$(id).duration||stage.time_s);};return button;
  }));
 }
 select.onchange=choose;choose();
}
refreshStats();setInterval(refreshStats,60000);
loadVideos().catch(()=>{$('videoScope').textContent='视频索引暂未加载，请刷新后重试。';});

async function loadAssetAdmission(){
 const response=await fetch('data/chemlab-assets.json');
 if(!response.ok)throw Error('asset admission unavailable');
 const data=await response.json();
 $('assetStats').textContent=`${data.accepted} 个资产通过；共检查 ${data.attempts} 个，拒绝 ${data.status_counts.rejected||0}，报错 ${data.status_counts.error||0}。失败记录保留，未改变准入门槛。`;
 const select=$('assetSelect');
 for(const asset of data.assets){const option=document.createElement('option');option.value=asset.id;option.textContent=asset.id.replace('instrument.','')+' · '+asset.selected_joint;select.append(option);}
 function choose(){
  const asset=data.assets.find(a=>a.id===select.value)||data.assets[0];
  if(!asset)return;
  $('assetVideo').src=asset.video;$('assetVideo').poster=asset.thumbnail;
  $('assetCaption').textContent=asset.id+' · 2秒静置 + 0.25秒关节推动 + 0.5秒释放；55帧完整解码，关节读回通过。资产工程检查，不是机器人任务成功率。';
 }
 select.onchange=choose;choose();
}
loadAssetAdmission().catch(()=>{$('assetStats').textContent='资产验收数据暂未加载，请稍后刷新。';});
