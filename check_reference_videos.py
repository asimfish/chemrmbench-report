"""Integrity and claim boundaries for the public video gallery."""
import hashlib,json,re,subprocess
from pathlib import Path

def check(root):
 root=Path(root);d=json.loads((root/'data/reproduction-videos.json').read_text());assert d['schema_version']==1 and d['full_reference_reproduction'] is False
 assert len(d['coverage'])==16 and len(d['supplemental'])==7
 assert all(x['status'] in ['partial','open'] and x['full_reference_reproduction'] is False for x in d['coverage'])
 ids={v['id'] for v in d['videos']};assert len(ids)==len(d['videos'])
 for v in d['videos']:
  assert v['full_reference_reproduction'] is False and v['playback_speed']==1
  assert re.fullmatch(r'assets/reference-videos/[a-z0-9_]+\.mp4',v['video'])
  assert re.fullmatch(r'assets/reference-videos/[a-z0-9_]+\.jpg',v['poster'])
  p=root/v['video'];assert p.is_file() and not p.is_symlink() and (root/v['poster']).is_file()
  assert hashlib.sha256(p.read_bytes()).hexdigest()==v['video_sha256']==v['source_video_sha256']
  stream=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-of','json',str(p)]))['streams'][0]
  assert stream['codec_name']=='h264' and int(stream['nb_frames'])==v['frames']
  assert abs(float(stream['duration'])-v['duration_s'])<.001
  # Decode every frame, including end-of-stream; a valid header alone is insufficient.
  subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-xerror','-i',str(p),'-f','null','-'],stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,check=True)
 assert '失败' in next(v['result'] for v in d['videos'] if v['id']=='pour_no_tilt')
 for row in d['coverage']:assert set(row['our_videos'])<=ids
 text=(root/'data/reproduction-videos.json').read_text()
 for private in ['/mnt/','/home/','Bearer ','ct-73','environment_overrides','tool_input']:assert private not in text
 return dict(passed=True,videos=len(ids),reference_entries=len(d['coverage']),supplemental_entries=len(d['supplemental']),all_frames_decoded=True,full_reference_reproduction=False)
if __name__=='__main__':print(json.dumps(check(Path(__file__).resolve().parent)))
