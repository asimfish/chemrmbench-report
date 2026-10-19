'use strict';
(async()=>{try{
 const response=await fetch('data/benchmark-release-v1.json');if(!response.ok)throw Error('release data missing');
 const data=await response.json();
 if(data.schema!=='chemrm-public-release-progress-v1'||data.full_benchmark_pass!==false||data.formal_M1_admission!==false||data.training_admission!==false)throw Error('scope mismatch');
 const put=(id,value)=>{document.getElementById(id).textContent=String(value);};
 put('releaseCount',data.contract.release_count);put('episodeCount',data.contract.episodes);
 put('nativeCount',data.native.runs);put('coverage',data.native.ordinary_restart_boundaries+' / '+data.native.task_boundaries);
 put('verificationStatus','合同执行与离线重算通过');
 for(const row of data.matrix_rows){const tr=document.createElement('tr');for(const key of ['group','policy','episodes','successful','detail']){const td=document.createElement('td');td.textContent=String(row[key]);tr.appendChild(td);}document.getElementById('matrixRows').appendChild(tr);}
 put('nativeAudit',data.native.runs+' 段视频逐一解码；'+data.native.stage_projections+' 个阶段投影、'+data.native.assets_verified+' 个资产通过关联与字节检查。');
 put('buildIdentity','复现包源提交 '+data.toolkit.source_commit.slice(0,12)+' · SHA-256 '+data.toolkit.sha256+' · '+(data.toolkit.bytes/1024/1024).toFixed(2)+' MB。');
 document.body.dataset.releaseState='ready';
}catch(error){document.getElementById('loadError').hidden=false;document.body.dataset.releaseState='error';}})();
