"""Validate the public dashboard contract without access to private research files."""
import hashlib
import json
from pathlib import Path
import re


def check(root):
    root = Path(root).resolve()
    p=root/'data/reproduction-current.json'
    d=json.loads(p.read_text())
    assert d['schema_version']==1 and d['full_reference_reproduction'] is False
    assert len(d['coverage'])==13 and len({x['id'] for x in d['coverage']})==13
    assert all(x['full_reference_accepted'] is False for x in d['coverage'])
    assert d['private_assets_exported'] is False and d['hardware_calibrated'] is False
    assert d['confirmation_batch']['scheduled']==4 and d['confirmation_batch']['completed']<=4
    old=[x for x in d['trials'] if x['kind']=='historical-confirmation']
    assert len(old)==4 and sum(x['outcome']=='FAIL' for x in old)==2
    assert sum(x['outcome']=='INCONCLUSIVE' for x in old)==2
    paths={'reproduction.html','reproduction.css','reproduction.js','data/reproduction-current.json','data/reproduction-figures.json'}
    for t in d['trials']:
        assert t['outcome'] in ['PASS','FAIL','INCONCLUSIVE','RUNNING','QUEUED']
        if t.get('evidence'):
            assert re.fullmatch(r'data/reproduction-evidence/[a-z0-9-]+\.json',t['evidence'])
            paths.add(t['evidence'])
            v=json.loads((root/t['evidence']).read_text())
            assert re.fullmatch(r'[0-9a-f]{64}',v['source_sha256'])
            assert all(type(value) is bool for value in v['checks'].values())
            if t['outcome']=='PASS':assert v['accepted'] and all(v['checks'].values())
    for figure in json.loads((root/'data/reproduction-figures.json').read_text()):
        path='assets/reproduction/'+figure['file'];paths.add(path)
        assert hashlib.sha256((root/path).read_bytes()).hexdigest()==figure['sha256']
    for path in paths:
        p=root/path
        assert p.is_file() and not p.is_symlink() and p.resolve().is_relative_to(root)
        text=p.read_text()
        assert not any(s in text for s in ['/mnt/','/home/','Bearer ','github_pat_','ghp_'])
        assert not re.search(r'ct-[0-9a-f]{32}',text)
    return dict(passed=True, public_artifacts_checked=len(paths), trials=len(d['trials']), full_reference_reproduction=False)


if __name__=='__main__':
    print(json.dumps(check(Path(__file__).resolve().parent)))
