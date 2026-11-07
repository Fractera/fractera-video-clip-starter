"""Voice labelling v3: BOT = dense, pitch-flat harmonic comb with ~70-130 Hz spacing.

Cepstral peak in the 70-130 Hz quefrency band vs the 140-600 Hz band (a dense
low comb wins even when odd harmonics are weak), plus flatness of that comb
over 0.3 s. MAIN = remaining voiced vocal activity.

usage: python3 -I voices3.py VOCALS.wav MIX OUT_DIR
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
NFFT = 4096


def load(path):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-f', 'f32le', '-ac', '1', '-ar', str(SR), '-'],
                         check=True, capture_output=True).stdout
    return np.frombuffer(raw, dtype=np.float32).copy()


def runs(mask):
    d = np.diff(np.r_[0, mask.astype(int), 0])
    return list(zip(np.where(d == 1)[0], np.where(d == -1)[0]))


def main():
    voc, mix, out = sys.argv[1], sys.argv[2], sys.argv[3]
    v, m = load(voc), load(mix)
    n = min(len(v), len(m))
    v, m = v[:n], m[:n]
    rv = librosa.feature.rms(y=v, frame_length=1024, hop_length=HOP)[0]
    rm = librosa.feature.rms(y=m, frame_length=1024, hop_length=HOP)[0]
    dbv, dbm = 20 * np.log10(rv + 1e-9), 20 * np.log10(rm + 1e-9)
    ref = np.percentile(dbv, 97)
    act = (dbv > ref - 30) & (dbv - dbm > -24)
    act = ndi.binary_closing(ndi.median_filter(act.astype(int), 5).astype(bool), structure=np.ones(int(0.25 * FPS)))

    X = np.abs(librosa.stft(v, n_fft=NFFT, hop_length=HOP))
    freqs = librosa.fft_frequencies(sr=SR, n_fft=NFFT)
    band = (freqs >= 60) & (freqs <= 5000)
    logX = np.log(X + 1e-6)
    logX[~band] = np.mean(logX[band], 0, keepdims=True).repeat((~band).sum(), 0)
    ceps = np.fft.irfft(logX, n=NFFT, axis=0)  # quefrency in samples
    q = np.arange(NFFT) / SR
    lo = (q >= 1 / 130) & (q <= 1 / 70)
    hi = (q >= 1 / 600) & (q <= 1 / 140)
    cL = ceps[lo].max(0)
    qL = q[lo][ceps[lo].argmax(0)]
    cH = ceps[hi].max(0)
    L = min(len(cL), len(act))
    cL, cH, qL, act, dbv, dbm = cL[:L], cH[:L], qL[:L], act[:L], dbv[:L], dbm[:L]
    f0c = 1 / qL
    cents = 1200 * np.log2(f0c / 100)
    # flatness of the low comb over 0.3 s
    w = int(0.3 * FPS)
    std = np.array([np.std(cents[max(0, i - w // 2):i + w // 2 + 1]) for i in range(L)])
    noise = np.percentile(cL[~act], 90) if (~act).sum() > 100 else 0.02
    botness = (cL - cH)
    bot = act & (cL > noise * 1.3) & (botness > 0) & (std < 25)
    bot = ndi.median_filter(bot.astype(int), 11).astype(bool)
    bot = ndi.binary_closing(bot, structure=np.ones(int(0.35 * FPS)))
    bot = ndi.binary_opening(bot, structure=np.ones(int(0.25 * FPS))) & act

    # MAIN: active, not bot, voiced in a 140-1000 Hz pYIN pass
    fH, vH, pH = librosa.pyin(v, fmin=140, fmax=1000, sr=SR, frame_length=2048, hop_length=HOP, resolution=0.05)
    fH, vH, pH = fH[:L], vH[:L], pH[:L]
    main_ = act & ~bot & vH & (pH > 0.3)
    main_ = ndi.median_filter(main_.astype(int), 9).astype(bool)

    segs = []
    for a, b in runs(act):
        lab = np.where(bot[a:b], 1, np.where(main_[a:b], 2, 0))
        idx = np.where(lab > 0)[0]
        if len(idx) == 0:
            continue
        filled = lab[idx[np.clip(np.searchsorted(idx, np.arange(len(lab))), 0, len(idx) - 1)]]
        filled = ndi.median_filter(filled, int(0.3 * FPS) | 1)
        for ra, rb in runs(filled == 1):
            segs.append(((a + ra) / FPS, (a + rb) / FPS, 'bot'))
        for ra, rb in runs(filled == 2):
            segs.append(((a + ra) / FPS, (a + rb) / FPS, 'main'))
    segs = sorted(s for s in segs if s[1] - s[0] >= 0.2)

    botf = f0c[bot]
    c_main = 1200 * np.log2(fH[main_ & np.isfinite(fH)] / 440) + 6900
    summary = {
        'bot': {'seconds': round(sum(b - a for a, b, l in segs if l == 'bot'), 1),
                'comb_spacing_hz_median': float(np.median(botf)), 'p10': float(np.percentile(botf, 10)), 'p90': float(np.percentile(botf, 90)),
                'note_median': librosa.hz_to_note(float(np.median(botf))), 'flatness_cents_std_0.3s': float(np.median(std[bot]))},
        'main': {'seconds': round(sum(b - a for a, b, l in segs if l == 'main'), 1),
                 'f0_median_hz': float(np.nanmedian(fH[main_])), 'note_median': librosa.midi_to_note(float(np.median(c_main)) / 100),
                 'p10_note': librosa.midi_to_note(float(np.percentile(c_main, 10)) / 100), 'p90_note': librosa.midi_to_note(float(np.percentile(c_main, 90)) / 100)},
        'vocal_activity_seconds': round(float(act.sum() / FPS), 1),
    }
    bt = [t for _, t in BLOCKS]
    ends = bt[1:] + [REC[1][1]]
    ends[37] = REC[0][1]
    per_block = []
    for (num, t0), t1 in zip(BLOCKS, ends):
        sb = sum(max(0, min(b, t1) - max(a, t0)) for a, b, l in segs if l == 'bot')
        sm = sum(max(0, min(b, t1) - max(a, t0)) for a, b, l in segs if l == 'main')
        per_block.append({'block': num, 't0': round(t0, 2), 't1': round(t1, 2), 'bot_s': round(sb, 2), 'main_s': round(sm, 2)})
    json.dump({'summary': summary, 'segments': [(round(a, 2), round(b, 2), l) for a, b, l in segs], 'per_block': per_block},
              open(os.path.join(out, 'voice_map_v3.json'), 'w'), indent=1)
    np.savez(os.path.join(out, 'voice_frames3.npz'), cL=cL, cH=cH, f0c=f0c, std=std, act=act, bot=bot, main=main_, fH=fH)
    print(json.dumps(summary, indent=1))
    print('bot segments:', [(f'{int(a // 60)}:{a % 60:04.1f}', round(b - a, 1)) for a, b, l in segs if l == 'bot'])
    print('blocks with bot >= 0.5 s:', [(p['block'], p['bot_s'], p['main_s']) for p in per_block if p['bot_s'] >= 0.5])


if __name__ == '__main__':
    main()
