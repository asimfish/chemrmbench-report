"""Public history subset: media identity + explicit reconstruction claim boundaries."""
import hashlib
import json
from pathlib import Path
import re

root=Path(__file__).resolve().parent
data=json.loads((root/'data/reconstruction.json').read_text())
assert data['schema']=='chemrm-preserved-scenes-v1'
assert len(data['scenes'])==6
assert data['history_message_count']==40496
rebuild=data['reconstruction']
for key in ['whole_scene_resume_pass','cold_restart_tested','full_long_chain_tested',
            'liquid_restart_tested','scientific_admission']:
    assert rebuild[key] is False,key
assert rebuild['settled_tracked_bodies']<rebuild['checkpoint_bodies']
assert rebuild['pestle_orientation_drift_deg']>rebuild['original_orientation_limit_deg']
count=0
for scene in data['scenes']:
    assert scene['scientific_admission'] is False
    assert len(scene['views'])==5
    for view in scene['views']:
        for field,extension in [('video','mp4'),('poster','jpg')]:
            value=view[field]
            assert re.fullmatch(r'assets/history/[a-z0-9_-]+\.'+extension,value),value
            p=root/value
            assert p.is_file() and p.resolve().is_relative_to((root/'assets/history').resolve())
            assert hashlib.sha256(p.read_bytes()).hexdigest()==view[field+'_sha256'],value
        assert view['fps']==12 and view['frames']>0
        assert abs(view['frames']/view['fps']-view['duration_s'])<.1
        count+=1
raw=json.dumps(data,ensure_ascii=False)
assert not re.search(r'(?i)Bearer\s|ct-[a-f0-9]{20}|znt_[a-f0-9]{20}|/mnt/|/home/|/data/|ssh\s',raw)
print(json.dumps(dict(status='PASS',checked_scene_replays=6,checked_camera_videos=count,
                     whole_scene_restore_accepted=False,cold_restart_accepted=False)))
