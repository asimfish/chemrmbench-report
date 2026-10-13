"""Contract for the public detailed reproduction audit (no private file access)."""
import json
import math
from pathlib import Path
import re


def check(root):
    root=Path(root)
    data=json.loads((root/'data/full-reference-progress.json').read_text())
    assert data['schema_version']==1 and data['full_reference_reproduction'] is False
    requirements=data['requirements']
    assert len(requirements)==36 and len({r['id'] for r in requirements})==36
    assert {r['family'] for r in requirements}=={'MATTERIX','AUTO_ENGINEERING','BOTH'}
    for r in requirements:
        assert re.fullmatch('[NAV][0-9]{2}',r['id'])
        assert r['full_reference_accepted'] is False and r['status'] in ['OPEN','PARTIAL']
        assert len(r['acceptance'])>20 and len(r['gap'])>10
        if r.get('published_function_reproduced') is True:
            assert r['id'] in ['N20','N22']
            assert re.fullmatch('[0-9a-f]{64}',r['functional_evidence_sha256'])
            assert r['functional_evidence']=='data/published-function-coverage-r1.json'
            assert r['configuration_status']=='ADAPTED_WITH_DECLARED_DIFFERENCES'
            assert r['quantitative_equivalence']=='NOT_CLAIMED_BY_THIS_QUALITATIVE_ACCEPTANCE'
            assert r['real_world_reproduced'] is False
            import hashlib
            raw=(root/r['functional_evidence']).read_bytes()
            assert hashlib.sha256(raw).hexdigest()==r['functional_evidence_sha256']
            coverage=json.loads(raw)
            item=next(x for x in coverage['requirements'] if x['id']==r['id'])
            assert item['simulation_published_function_closed'] is True
            assert item['minimum_necessary_evidence_remaining_for_this_qualitative_function']==[]
    for module in data['modules']:
        assert type(module['subsystem_passed']) is bool and module['full_reference_accepted'] is False
        assert re.fullmatch('[0-9a-f]{64}',module['evidence_sha256'])
        assert module['scope'] and module['remaining']
        assert all(type(v) in [int,float] and math.isfinite(v) for v in module['metrics'].values())
    if data['active']:
        assert type(data['active']['process_verified_alive']) is bool
        assert data['active']['simulation_s']>=0 and data['active']['physics_steps']>=0
    content=json.dumps(data)
    assert not any(s in content for s in ['/mnt/','/home/','Bearer ','github_pat_','ghp_','.git-credentials'])
    assert not re.search(r'ct-[0-9a-f]{32}',content)
    for path in ['full-reproduction.html','full-reproduction.css','full-reproduction.js']:
        assert (root/path).is_file() and not (root/path).is_symlink()
    js=(root/'full-reproduction.js').read_text()
    assert 'innerHTML' not in js and 'textContent' in js
    return dict(passed=True,requirements=len(requirements),modules=len(data['modules']),
                published_functions_reproduced=sum(r.get('published_function_reproduced') is True for r in requirements),
                full_reference=False,private_assets_exported=False)


if __name__=='__main__':
    print(json.dumps(check(Path(__file__).resolve().parent)))
