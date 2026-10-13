'use strict';
const node=id=>document.getElementById(id);let data=null,current='a1',camera=null;
function make(tag,text='',cls=''){const n=document.createElement(tag);n.textContent=text;if(cls)n.className=cls;return n;}
function localAsset(path,extension){if(typeof path!=='string'||!new RegExp('^assets/history/[a-z0-9_-]+\\.'+extension+'$','i').test(path))throw Error('invalid media asset');return path;}
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
    ['语义阶段续采接入',nativePassed?'16 项 CPU 契约测试 + 实测夹爪技能':'10 项 CPU 契约测试',nativePassed?'空载技能通过 · 真实物体任务待补':'完整原生验收待补'],
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
async function load(){try{const response=await fetch('data/reconstruction.json',{cache:'no-store'});if(!response.ok)throw Error('source unavailable');data=await response.json();if(data.schema!=='chemrm-preserved-scenes-v1'||data.scenes.length!==6||data.reconstruction.scientific_admission!==false)throw Error('evidence schema');node('recordDate').textContent='本轮核验 '+new Intl.DateTimeFormat('zh-CN',{timeZone:'Asia/Shanghai',dateStyle:'short',timeStyle:'medium'}).format(new Date(data.verified_at_utc))+' · 恢复检索 '+data.history_message_count.toLocaleString('zh-CN')+' 条可见历史消息';renderScene();renderRestore();}catch(error){node('sceneError').hidden=false;node('sceneError').textContent='证据索引读取失败。静态预览保留；不能据此推断重建、恢复或实验已通过。';}}
load();
