"""Validate visual evidence identity and preserve physical/visual claim boundaries."""
import hashlib,json,re
from pathlib import Path
def check(root):
    root=Path(root);d=json.loads((root/'data/visual-audit.json').read_text())
    assert d['color_material_correction_passed'] is True
    assert d['full_reference_visual_match'] is d['full_reference_reproduction'] is False
    assert len(d['comparison_images'])==5 and len(d['corrected_videos'])==8
    for x in d['comparison_images']:
        assert re.fullmatch(r'assets/visual-audit/[a-z-]+\.png',x['file'])
        p=root/x['file'];assert p.is_file() and not p.is_symlink()
        assert hashlib.sha256(p.read_bytes()).hexdigest()==x['sha256']
    videos=json.loads((root/'data/reproduction-videos.json').read_text())['videos']
    for x in d['corrected_videos']:
        item=next(v for v in videos if v['id']==x['id'])
        assert item['kind']=='recorded_state_replay'
        assert item['video_sha256']==x['sha256'] and item['visual_material_corrected'] is True
    for p in [root/'visual-audit.html',root/'visual-audit.css',root/'data/visual-audit.json']:
        t=p.read_text();assert not any(x in t for x in ['/mnt/','/home/','Bearer ','github_pat_','ghp_'])
        assert not re.search(r'ct-[0-9a-f]{32}',t)
    return dict(passed=True,comparison_images=5,corrected_videos=8,full_reference_visual_match=False)
if __name__=='__main__':print(json.dumps(check(Path(__file__).resolve().parent)))
