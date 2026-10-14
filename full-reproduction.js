'use strict';
const $=id=>document.getElementById(id);
const node=(tag,text,cls)=>{const n=document.createElement(tag);if(text!==undefined)n.textContent=text;if(cls)n.className=cls;return n;};
let data=null,loading=false;
const labels={channels:'Channels',positive_per_channel_model_uL:'Positive / channel · model µL',negative_per_channel_model_uL:'No aspiration / channel · model µL',parcel_model_uL:'Parcel · model µL',physics_steps_per_run:'Physics steps / run',numerical_checks:'Numerical checks',checks_passed:'Checks passed',initial_density_residual:'Initial mean density residual',final_density_residual:'Final mean density residual',simulation_s:'Native simulation · s',physics_steps:'Native physics steps',placement_error_mm:'Final placement error · mm',product_high:'Product / high · source units',product_40C_shadow:'Product / 40°C shadow · source units'};
function format(x){return Number.isInteger(x)?x.toLocaleString():Math.abs(x)<.001?x.toExponential(3):x.toFixed(4);}
function renderRequirements(){if(!data)return;const query=$('search').value.trim().toLowerCase(),family=$('family').value;const rows=data.requirements.filter(r=>(family==='all'||r.family===family)&&[r.id,r.reference,r.acceptance,r.gap].join(' ').toLowerCase().includes(query));$('visible-count').textContent=rows.length+' / '+data.requirements.length+' requirements';$('requirements-list').replaceChildren();for(const r of rows){const d=node('details'),s=node('summary');s.append(node('span',r.id,'code'),node('span',r.reference,'name'),node('span',r.published_function_reproduced?'FUNCTION REPRODUCED / FULL OPEN':r.status==='PARTIAL'?'PARTIAL / FULL OPEN':'OPEN','badge '+(r.published_function_reproduced?'pass':r.status==='PARTIAL'?'partial':'open')));const b=node('div',undefined,'requirement-body');b.append(node('p',r.family.replaceAll('_',' ')+' · '+r.kind,'muted'),node('p','REQUIRED EVIDENCE','label'),node('p',r.acceptance),node('p','REMAINING GAP','label'),node('p',r.gap));if(r.published_function_reproduced){b.append(node('p','QUALITATIVE SIMULATION FUNCTION REPRODUCED','label'),node('p','Configuration: declared adaptation. Quantitative equivalence: not established by this qualitative test. Real deployment: not reproduced.'));const a=node('a','Read the published-function coverage review ↗');a.href='data/published-function-coverage-r1.json';b.append(a,node('p','Review SHA-256 · '+r.functional_evidence_sha256,'hash'));}d.append(s,b);$('requirements-list').append(d);}}
function render(){const age=(Date.now()-Date.parse(data.exported_at_utc))/60000;$('updated').textContent='Exported '+new Date(data.exported_at_utc).toLocaleString()+(age>25?' · STALE':'');$('updated').classList.toggle('stale',age>25);$('full-count').textContent=data.requirements.filter(r=>r.published_function_reproduced===true).length;$('module-count').textContent=data.modules.length;$('runtime').replaceChildren();if(data.active){const a=data.active;$('runtime').append(node('span',a.process_verified_alive?'RUNNING':a.phase==='COMPLETED'?'COMPLETED · CHECK EVIDENCE':'PROCESS NOT VERIFIED','badge '+(a.process_verified_alive?'partial':'open')),node('p',a.id),node('strong',format(a.simulation_s)+' s'),node('p',format(a.physics_steps)+' physics steps','muted'));}else $('runtime').append(node('p','No native run is registered as active. See scoped experiments and open requirements below.'));
 $('modules').replaceChildren();for(const m of data.modules.slice().reverse()){const card=node('article',undefined,'module');card.append(node('span',m.subsystem_passed?'SCOPED CHECKS PASS':'CHECKS NOT CLOSED','badge '+(m.subsystem_passed?'pass':'open')),node('h3',m.title),node('p',m.scope));const metrics=node('div',undefined,'metric-grid');for(const [k,v]of Object.entries(m.metrics)){const cell=node('div');cell.append(node('strong',format(v)),node('span',labels[k]||k.replaceAll('_',' ')));metrics.append(cell);}card.append(metrics,node('p',m.remaining,'limits'),node('p','Evidence SHA-256 · '+m.evidence_sha256,'hash'));$('modules').append(card);}
 $('boundaries').replaceChildren(...data.source_boundaries.map(t=>node('li',t)));$('assets').textContent=data.asset_progress;$('sources').replaceChildren();for(const source of data.source_links){const a=node('a',source.title+' ↗');a.href=source.url;a.rel='noopener noreferrer';a.target='_blank';$('sources').append(a);}renderRequirements();}
async function refresh(){if(loading)return;loading=true;$('refresh').disabled=true;try{const response=await fetch('data/full-reference-progress.json?t='+Date.now(),{cache:'no-store'});if(!response.ok)throw Error('HTTP '+response.status);const d=await response.json();if(d.schema_version!==1||d.full_reference_reproduction!==false||d.requirements.length!==36)throw Error('Unexpected evidence contract');data=d;$('error').hidden=true;render();}catch(e){$('error').hidden=false;$('error').textContent='Could not refresh evidence. The last snapshot is retained; please retry.';}finally{loading=false;$('refresh').disabled=false;}}
$('refresh').addEventListener('click',refresh);$('search').addEventListener('input',renderRequirements);$('family').addEventListener('change',renderRequirements);refresh();setInterval(refresh,60000);

// Defer inactive clip loading and restore position only when a clip is played.
const clips=[...document.querySelectorAll('#videos video')];
for(const clip of clips){
 clip.preload='none';
 const resume=()=>{
  if(clip.paused||clip.readyState<1)return;
  const resume=Number(clip.dataset.resumeTime);
  if(Number.isFinite(resume)&&resume>0&&resume<clip.duration)clip.currentTime=resume;
  delete clip.dataset.resumeTime;
 };
 clip.addEventListener('loadedmetadata',resume);
 clip.addEventListener('play',()=>{
  resume();
  for(const other of clips){
   if(other===clip||other.readyState===0)continue;
   if(other.currentTime>0)other.dataset.resumeTime=String(other.currentTime);
   other.pause();other.preload='none';other.load();
  }
 });
}
