"""Decode and authenticate the eighteen reviewed recorded-state videos."""
import hashlib
import json
from pathlib import Path
import subprocess


def check(root):
    root = Path(root).resolve()
    manifest = json.loads((root / 'data/full-reference-media.json').read_text())
    assert manifest['full_reference_reproduction'] is False
    assert len(manifest['videos']) == 18
    results = []
    for item in manifest['videos']:
        path = root / item['path']
        assert path.resolve().is_relative_to(root) and not path.is_symlink()
        assert item['full_reference_accepted'] is False
        assert hashlib.sha256(path.read_bytes()).hexdigest() == item['sha256']
        probe = json.loads(subprocess.run([
            'ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_streams',
            '-of', 'json', str(path)
        ], check=True, capture_output=True, text=True).stdout)['streams'][0]
        if 'panda-plate-' in path.name:
            positive = 'placement' in path.name
            expected = (669, 44.5 if positive else 44.498333, 1920, 740)
            assert probe['time_base'] == '1/600'
            frames = json.loads(subprocess.run([
                'ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_frames',
                '-show_entries', 'frame=best_effort_timestamp', '-of', 'json', str(path)
            ], check=True, capture_output=True, text=True).stdout)['frames']
            assert [f['best_effort_timestamp'] for f in frames] == [0]+list(range(39, 26680, 40))+[26699 if positive else 26698]
        elif 'seed201' in path.name:
            expected = (72, 7.2, 1600, 900)
        elif 'dual-flexiv-gate-stop-' in path.name:
            expected = (525, 21.0, 1600, 900)
        elif 'dual-flexiv-handoff-' in path.name:
            expected = (475, 19.0, 1600, 900)
        elif 'ur5e-whole-workflow-' in path.name:
            expected = (575, 23.0, 1600, 900)
        elif 'ur5e-' in path.name:
            expected = (312, 12.48, 1600, 900)
        elif 'ot2-sixwell-' in path.name:
            expected = (915, 61.0, 1920, 740)
        elif 'ot2-' in path.name:
            expected = (390, 26.0, 1920, 740)
        else:
            expected = (121, 3.025, 1000, 720)
        assert probe['codec_name'] == 'h264'
        actual = (int(probe['nb_frames']), float(probe['duration']), probe['width'], probe['height'])
        assert actual == expected, (path.name, actual, expected)
        subprocess.run(['ffmpeg', '-v', 'error', '-xerror', '-i', str(path),
                        '-f', 'null', '-'], check=True, capture_output=True)
        assert (root / item['poster']).is_file()
        results.append(dict(path=item['path'], sha256=item['sha256'],
                            frames=actual[0], duration_s=actual[1], decoded=True))
    return dict(passed=True, videos=results, full_reference_accepted=False)


if __name__ == '__main__':
    print(json.dumps(check(Path(__file__).resolve().parent)))
