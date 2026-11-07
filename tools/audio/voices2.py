"""Frame-level voice labelling: BOT (low monotone ~80-95 Hz, flat harmonics) vs MAIN.

Two pYIN passes over the vocal stem: a low band (60-130 Hz) and a high band
(140-1000 Hz). A true low voice is voiced in the low pass and NOT in the high
pass; a higher voice is voiced in the high pass (its sub-harmonics also light the
low pass, so high-pass voicing wins). Bot frames must also be pitch-flat.

usage: python3 -I voices2.py VOCALS.wav MIX OUT_DIR
"""
import sys, os, json, subprocess
import numpy as np
import librosa
import scipy.ndimage as ndi

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from blocks import BLOCKS, REC

SR = 22050
HOP = 256
FPS = SR / HOP


def load(path):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-f', 'f32le', '-ac', '1', '-ar', str(SR), '-'],
                         check=True, capture_output=True).stdout
    return np.frombuffer(raw, dtype=np.float32).copy()


def runs(mask):
    d = np.diff(np.r_[0, mask.astype(int), 0])
    return list(zip(np.where(d == 1)[0], np.where(d == -1)[0]))


def local_std_cents(f0, voiced, w):
    c = np.where(voiced, 1200 * np.log2(np.nan_to_num(f0, nan=100.0) / 100.0), np.nan)
    out = np.full(len(c), np.nan)
    h = w // 2
    for i in range(len(c)):
        seg = c[max(0, i - h):i + h + 1]
        seg = seg[np.isfinite(seg)]
        if len(seg) >= max(3, w // 3):
            out[i] = np.std(seg)
    return out


def main():
    voc, mix, out = sys.argv[1], sys.argv[2], sys.argv[3]
    v = load(voc)
    m = load(mix)
    n = min(len(v), len(m))
    v, m = v[:n], m[:n]
    rv = librosa.feature.rms(y=v, frame_length=1024, hop_length=HOP)[0]
    rm = librosa.feature.rms(y=m, frame_length=1024, hop_length=HOP)[0]
    dbv, dbm = 20 * np.log10(rv + 1e-9), 20 * np.log10(rm + 1e-9)
    ref = np.percentile(dbv, 97)
    act = (dbv > ref - 30) & (dbv - dbm > -24)
    act = ndi.binary_closing(ndi.median_filter(act.astype(int), 5).astype(bool), structure=np.ones(int(0.25 * FPS)))

    fL, vL, pL = librosa.pyin(v, fmin=60, fmax=130, sr=SR, frame_length=4096, hop_length=HOP, resolution=0.05)
    fH, vH, pH = librosa.pyin(v, fmin=140, fmax=1000, sr=SR, frame_length=2048, hop_length=HOP, resolution=0.05)
    L = min(len(fL), len(fH), len(act))
    fL, vL, pL, fH, vH, pH, act, dbv, dbm = fL[:L], vL[:L], pL[:L], fH[:L], vH[:L], pH[:L], act[:L], dbv[:L], dbm[:L]
    stdL = local_std_cents(fL, vL, int(0.3 * FPS))
    stdH = local_std_cents(fH, vH, int(0.3 * FPS))

    bot = act & vL & (pL > 0.45) & ~(vH & (pH > 0.35)) & (np.nan_to_num(stdL, nan=999) < 35)
    main_ = act & vH & (pH > 0.35)
    # smooth to syllable scale
    bot = ndi.median_filter(bot.astype(int), 9).astype(bool)
    main_ = ndi.median_filter(main_.astype(int), 9).astype(bool) & ~bot
    # segments: activity runs, each labelled by majority of voiced labels inside
    segs = []
    for a, b in runs(act):
        nb, nm = bot[a:b].sum(), main_[a:b].sum()
        if b - a < int(0.15 * FPS):
            continue
        # split long runs at label changes (>=0.4 s) to keep call-and-response inside one phrase
        lab = np.where(bot[a:b], 1, np.where(main_[a:b], 2, 0))
        # fill unlabeled frames from neighbours
        idx = np.where(lab > 0)[0]
        if len(idx) == 0:
            segs.append((a / FPS, b / FPS, 'unvoiced'))
            continue
        filled = lab[idx[np.clip(np.searchsorted(idx, np.arange(len(lab))), 0, len(idx) - 1)]]
        filled = ndi.median_filter(filled, int(0.4 * FPS) | 1)
        for ra, rb in runs(filled == 1):
            segs.append(((a + ra) / FPS, (a + rb) / FPS, 'bot'))
        for ra, rb in runs(filled == 2):
            segs.append(((a + ra) / FPS, (a + rb) / FPS, 'main'))
    segs.sort()
    segs = [s for s in segs if s[1] - s[0] >= 0.2]

    def stats(mask, f0):
        f = f0[mask & np.isfinite(f0)]
        if len(f) == 0:
            return {}
        c = 1200 * np.log2(f / 440) + 6900
        return {'f0_median_hz': float(np.median(f)), 'f0_p10_hz': float(np.percentile(f, 10)), 'f0_p90_hz': float(np.percentile(f, 90)),
                'note_median': librosa.midi_to_note(float(np.median(c)) / 100), 'range_semitones_p10_p90': float((np.percentile(c, 90) - np.percentile(c, 10)) / 100)}

    bot_sec = sum(b - a for a, b, l in segs if l == 'bot')
    main_sec = sum(b - a for a, b, l in segs if l == 'main')
    summary = {
        'bot': {**stats(bot, fL), 'seconds': round(bot_sec, 1), 'pitch_flatness_cents_std_0.3s': float(np.nanmedian(stdL[bot]))},
        'main': {**stats(main_, fH), 'seconds': round(main_sec, 1), 'pitch_flatness_cents_std_0.3s': float(np.nanmedian(stdH[main_]))},
    }
    # per block
    bt = [t for _, t in BLOCKS]
    ends = bt[1:] + [REC[1][1]]
    ends[37] = REC[0][1]  # block 38 ends with recording 1
    per_block = []
    for (num, t0), t1 in zip(BLOCKS, ends):
        sb = sum(max(0, min(b, t1) - max(a, t0)) for a, b, l in segs if l == 'bot')
        sm = sum(max(0, min(b, t1) - max(a, t0)) for a, b, l in segs if l == 'main')
        per_block.append({'block': num, 't0': round(t0, 2), 't1': round(t1, 2), 'bot_s': round(sb, 2), 'main_s': round(sm, 2)})
    res = {'summary': summary, 'segments': [(round(a, 2), round(b, 2), l) for a, b, l in segs], 'per_block': per_block}
    json.dump(res, open(os.path.join(out, 'voice_map_v2.json'), 'w'), indent=1)
    np.savez(os.path.join(out, 'voice_frames2.npz'), fL=fL, pL=pL, vL=vL, fH=fH, pH=pH, vH=vH, act=act, bot=bot, main=main_, stdL=stdL, stdH=stdH)
    print(json.dumps(summary, indent=1))
    print('bot segments:', [(f'{int(a // 60)}:{a % 60:04.1f}', round(b - a, 1)) for a, b, l in segs if l == 'bot'])
    print('blocks with bot >= 0.5 s:', [(p['block'], p['bot_s'], p['main_s']) for p in per_block if p['bot_s'] >= 0.5])


if __name__ == '__main__':
    main()
