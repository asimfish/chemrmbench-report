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
  $('taskCards').replaceChildren(...data.tasks.map(task=>{
   const card=document.createElement('article');card.className='task';
   const top=document.createElement('div');top.className='task-top';
   const number=document.createElement('span');number.className='number';number.textContent=task.number;
   const badge=document.createElement('span');badge.className='badge '+task.status;badge.textContent=labels[task.status]||task.status;top.append(number,badge);
   const title=document.createElement('h3');title.textContent=task.title;
   const dimension=document.createElement('p');dimension.textContent=task.dimension;
   const progress=document.createElement('div');progress.className='progress';const fill=document.createElement('i');fill.style.width=Math.min(100,task.dataset_unique_seeds/20*100)+'%';progress.append(fill);
   const counts=document.createElement('p');counts.className='task-metrics';counts.textContent=`${task.dataset_unique_seeds} / 20 个唯一 seed　·　随机化尝试 ${task.dataset_attempts}`;
   const rate=document.createElement('p');rate.textContent=task.dataset_attempts?`成功 ${task.successes} / ${task.dataset_attempts}（${(task.success_rate*100).toFixed(1)}%） · 失败 ${task.status_counts.fail||0} · 报错 ${task.status_counts.error||0}`:'随机化成功率尚未测量';
   const evidence=document.createElement('p');evidence.textContent=`已复核随机化录像 ${task.verified_dataset_attempts} 条 · 资格检查 ${task.qualification_attempts} 次，物理安全成功 ${task.qualification_safe_successes} 次`+(task.calibration_attempts?` · 历史专家校准 ${task.calibration_attempts} 条（成功 ${task.calibration_status_counts.success||0} / 失败 ${task.calibration_status_counts.fail||0} / 报错 ${task.calibration_status_counts.error||0}）`:'')+(task.memory_gate_attempts?` · 像素门槛前缀 ${task.memory_gate_attempts} 条`:'')+(task.id==='delayed_cue_memory'?` · 提示后像素门槛 ${task.memory_layout_gates_passed||0}/3 布局`:'')+(task.render_diagnostic_attempts?` · 另有 ${task.render_diagnostic_attempts} 次短前缀渲染诊断`:'');
   card.append(top,title,dimension,progress,counts,rate,evidence);return card;
  }));
 }catch(error){$('updated').textContent='暂未读取到最新统计，请稍后刷新；视频仍可观看。';}
}
async function loadVideos(){
 const response=await fetch('data/native-video-index.json');if(!response.ok)throw Error('video index unavailable');
 const videos=await response.json();const select=$('taskSelect');
 for(const item of videos){const option=document.createElement('option');option.value=item.id;option.textContent=item.title;select.append(option);}
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
