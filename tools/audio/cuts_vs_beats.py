"""How hard cuts in the reference relate to the musical grid.

Beat grid: librosa beat tracking over the whole mix (handles the slower first
~76 s), checked against the strict 120 BPM grid where it holds.
usage: python3 -I cuts_vs_beats.py TRACK STRUCTURE_JSON CUTS1 CUTS2 OUT_JSON
"""
import sys, json, subprocess
import numpy as np
import librosa

SR, HOP = 22050, 256
OFF = [11.061, 202.216]


def main():
    track, sj, c1, c2, outp = sys.argv[1:6]
    st = json.load(open(sj))
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', track, '-f', 'f32le', '-ac', '1', '-ar', str(SR), '-'], check=True, capture_output=True).stdout
    y = np.frombuffer(raw, dtype=np.float32).copy()
    _, yp = librosa.effects.hpss(y)
    oenv = librosa.onset.onset_strength(y=yp, sr=SR, hop_length=HOP, aggregate=np.median)
    _, beats = librosa.beat.beat_track(onset_envelope=oenv, sr=SR, hop_length=HOP, start_bpm=119, tightness=400, units='time')
    grid = np.array(st['beats'])
    # use tracked beats before 76 s, the strict grid after
    b = np.r_[beats[beats < 76.0], grid[grid >= 76.0]]
    ibi = np.diff(beats)
    # downbeats: phase from the strict grid region (first downbeat 1.5273 + 2k); before 76 s count back from the first grid downbeat >= 76 by 4-beat steps
    bars_grid = np.array(st['bars'])
    first_gd = bars_grid[bars_grid >= 76.0][0]
    idx_first = int(np.argmin(np.abs(b - first_gd)))
    is_down = np.zeros(len(b), bool)
    is_down[idx_first % 4::4] = True
    cuts = []
    for path, off in ((c1, OFF[0]), (c2, OFF[1])):
        for line in open(path):
            t, score = map(float, line.split())
            cuts.append((t + off, score))
    cuts.sort()
    # merge cut detections within 0.25 s (one visual event)
    merged = []
    for t, s in cuts:
        if merged and t - merged[-1][0] < 0.25:
            if s > merged[-1][1]:
                merged[-1] = (t, s)
        else:
            merged.append((t, s))
    rows = []
    for t, s in merged:
        i = int(np.argmin(np.abs(b - t)))
        d = t - b[i]
        half = np.r_[b, b[:-1] + np.diff(b) / 2]
        j = int(np.argmin(np.abs(half - t)))
        rows.append({'t': round(t, 3), 'score': s, 'to_beat_ms': round(d * 1000), 'on_downbeat': bool(is_down[i]),
                     'to_eighth_ms': round((t - half[j]) * 1000)})
    tol = 0.070  # 2 frames at 30 fps
    on_beat = [r for r in rows if abs(r['to_beat_ms']) <= tol * 1000]
    on_8th = [r for r in rows if abs(r['to_eighth_ms']) <= tol * 1000]
    on_down = [r for r in on_beat if r['on_downbeat']]
    rng = np.random.default_rng(0)
    rand = rng.uniform(b[0], b[-1], 20000)
    chance_beat = float(np.mean([np.min(np.abs(b - t)) <= tol for t in rand]))
    res = {'n_cuts': len(rows), 'on_beat_70ms': len(on_beat), 'on_eighth_70ms': len(on_8th), 'on_downbeat': len(on_down),
           'chance_on_beat': round(chance_beat, 3), 'tracked_ibi_first76s_median': float(np.median(ibi[beats[1:] < 76])),
           'tracked_bpm_first76s': round(60 / float(np.median(ibi[beats[1:] < 76])), 2), 'cuts': rows}
    json.dump(res, open(outp, 'w'), indent=1)
    print({k: v for k, v in res.items() if k != 'cuts'})


if __name__ == '__main__':
    main()
