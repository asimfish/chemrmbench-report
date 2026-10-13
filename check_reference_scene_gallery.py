"""Validate public scene provenance, preview files and acceptance boundaries."""
import hashlib
import json
from pathlib import Path
import re
import struct


def check(root):
    root=Path(root).resolve();p=root/'data/reproduction-scenes.json';d=json.loads(p.read_text())
    assert d['schema_version']==1 and d['assembled_scenes']==4
    assert d['full_reference_reproduction'] is False and d['raw_assets_exported'] is False
    assert d['hardware_calibrated'] is False
    ids={'matterix_heat_pour','matterix_ot2_station','auto_dual_flexiv_lab','auto_ur5e_lab'}
    assert {s['id'] for s in d['scenes']}==ids and len(d['scenes'])==4
    assert d['native_validated_scenes']==sum(s['native_validation_passed'] for s in d['scenes'])
    assert d['native_validated_scenes']==4
    pictures=0
    for s in d['scenes']:
        assert s['full_workflow_reproduced'] is False
        assert all(type(v) is bool for v in s['native_checks'].values())
        assert s['native_validation_passed']==all(s['native_checks'].values())
        assert re.fullmatch(r'[0-9a-f]{64}',s['scene_sha256'])
        assert re.fullmatch(r'[0-9a-f]{64}',s['evidence_sha256'])
        if s['id'].startswith('auto_'):
            assert s['native_contact_smoke'] is True and s['native_steps']==1000 and abs(s['simulated_seconds']-2)<1e-8
        else:
            assert s['timeline_stopped'] is True and s['native_steps']==0 and s['native_contact_smoke'] is False
        assert any(pic['view']=='overview' for pic in s['pictures'])
        for pic in s['pictures']:
            assert re.fullmatch(r'assets/scenes/[a-z0-9_]+\.png',pic['file'])
            p=root/pic['file'];assert p.is_file() and not p.is_symlink() and p.resolve().is_relative_to(root)
            b=p.read_bytes();assert b[:8]==b'\x89PNG\r\n\x1a\n' and struct.unpack('>II',b[16:24])==(1600,1000)
            assert hashlib.sha256(b).hexdigest()==pic['sha256'];pictures+=1
    for f in ['data/reproduction-scenes.json','reference-scenes.html','reference-scenes.css','reference-scenes.js']:
        text=(root/f).read_text();assert not any(x in text for x in ['/mnt/','/home/','Bearer ','github_pat_','ghp_'])
        assert not re.search(r'ct-[0-9a-f]{32}',text)
    return dict(passed=True,native_scenes=4,previews=pictures,full_reference_reproduction=False)


if __name__=='__main__':print(json.dumps(check(Path(__file__).resolve().parent)))
