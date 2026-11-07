"""Song structure: constant-tempo beat grid, downbeat phase, key, loudness,
bar-level self-similarity, novelty boundaries, repeat labels.

usage: python3 -I structure.py TRACK OUT_DIR
writes OUT_DIR/structure.json, OUT_DIR/ssm.png, OUT_DIR/bars_features.npz
"""
import sys, os, json, subprocess, re
import numpy as np
import librosa
import scipy.ndimage as ndi
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

SR = 22050
HOP = 256


def load(path):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-f', 'f32le', '-ac', '1', '-ar', str(SR), '-'],
                         check=True, capture_output=True).stdout
    return np.frombuffer(raw, dtype=np.float32).copy()


def ebur128(path):
    p = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', path, '-af', 'ebur128=framelog=info', '-f', 'null', '-'],
                       capture_output=True, text=True)
    t, M, S = [], [], []
    for line in p.stderr.splitlines():
        m = re.search(r't:\s*([\d.]+)\s+TARGET.*?M:\s*(-?[\d.]+|-inf)\s+S:\s*(-?[\d.]+|-inf)', line)
        if m:
            t.append(float(m.group(1)))
            M.append(float(m.group(2)) if m.group(2) != '-inf' else -70.0)
            S.append(float(m.group(3)) if m.group(3) != '-inf' else -70.0)
    integ = re.findall(r'I:\s*(-?[\d.]+) LUFS', p.stderr)
    lra = re.findall(r'LRA:\s*([\d.]+) LU', p.stderr)
    return np.array(t), np.array(M), np.array(S), float(integ[-1]) if integ else None, float(lra[-1]) if lra else None


def fit_grid(oenv, fps, lo=100, hi=140, step=0.005):
    """constant-tempo grid: BPM whose phase-folding of the onset envelope is sharpest"""
    n = np.arange(len(oenv))
    best = None
    for bpm in np.arange(lo, hi, step):
        P = 60.0 / bpm * fps
        ph = (n % P) / P
        h, _ = np.histogram(ph, bins=64, range=(0, 1), weights=oenv)
        h = ndi.uniform_filter1d(h, 3, mode='wrap')
        score = h.max() / (h.mean() + 1e-9)
        if best is None or score > best[0]:
            best = (score, bpm, (np.argmax(h) + 0.5) / 64 * P / fps)
    return best  # score, bpm, t0 (seconds of first grid point inside one period)


def local_drift(oenv, fps, beats, win=16, search=0.06):
    """per window of `win` beats: shift (s) that best aligns the grid locally"""
    out = []
    shifts = np.arange(-search, search + 1e-9, 1.0 / fps)
    for i in range(0, len(beats) - win, win // 2):
        b = beats[i:i + win]
        sc = [np.sum(np.interp((b + s) * fps, np.arange(len(oenv)), oenv)) for s in shifts]
        out.append((float(b[0]), float(shifts[int(np.argmax(sc))]), float(np.max(sc) / (np.mean(sc) + 1e-9))))
    return out


KS_MAJ = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
KS_MIN = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17])
NOTES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']


def key_estimate(chroma_mean):
    res = []
    for k in range(12):
        res.append((np.corrcoef(chroma_mean, np.roll(KS_MAJ, k))[0, 1], NOTES[k] + ' major'))
        res.append((np.corrcoef(chroma_mean, np.roll(KS_MIN, k))[0, 1], NOTES[k] + ' minor'))
    res.sort(reverse=True)
    return res[:4]


def foote(S, w):
    g = np.exp(-0.5 * (np.linspace(-2, 2, 2 * w) ** 2))
    K = np.outer(g, g) * np.outer(np.r_[-np.ones(w), np.ones(w)], np.r_[-np.ones(w), np.ones(w)])
    n = len(S)
    Sp = np.pad(S, w, mode='edge')
    nov = np.array([np.sum(Sp[i:i + 2 * w, i:i + 2 * w] * K) for i in range(n)])
    nov = np.maximum(nov, 0)
    return nov / (nov.max() + 1e-9)


def main():
    track, out = sys.argv[1], sys.argv[2]
    os.makedirs(out, exist_ok=True)
    y = load(track)
    dur = len(y) / SR
    yh, yp = librosa.effects.hpss(y)
    fps = SR / HOP
    oenv = librosa.onset.onset_strength(y=yp, sr=SR, hop_length=HOP, aggregate=np.median)
    oenv = oenv / (oenv.max() + 1e-9)

    score, bpm, t0 = fit_grid(oenv, fps)
    T = 60.0 / bpm
    k0 = -int(np.floor(t0 / T))
    beats = t0 + T * np.arange(k0, int((dur - t0) / T) + 1)
    beats = beats[(beats >= 0) & (beats < dur)]
    drift = local_drift(oenv, fps, beats)
    tempo_lib = float(np.atleast_1d(librosa.feature.tempo(onset_envelope=oenv, sr=SR, hop_length=HOP, start_bpm=118))[0])

    # per-beat features for downbeat phase
    S_mel = librosa.feature.melspectrogram(y=yp, sr=SR, hop_length=HOP, n_mels=64, fmax=11000)
    mel_f = librosa.mel_frequencies(n_mels=64, fmax=11000)
    lowband = np.log1p(S_mel[mel_f < 150].sum(0))
    hiband = np.log1p(S_mel[(mel_f > 1500) & (mel_f < 8000)].sum(0))
    kick = np.maximum(0, np.diff(lowband, prepend=lowband[0]))
    snare = np.maximum(0, np.diff(hiband, prepend=hiband[0]))
    chroma = librosa.feature.chroma_cqt(y=yh, sr=SR, hop_length=HOP * 2)
    cfps = SR / (HOP * 2)

    def at(sig, f, t, w=0.05):
        i0, i1 = int((t - w) * f), int((t + w) * f) + 1
        return float(sig[max(0, i0):max(1, i1)].max())

    bk = np.array([at(kick, fps, t) for t in beats])
    bs = np.array([at(snare, fps, t) for t in beats])
    cn = []
    for t in beats:
        a = chroma[:, max(0, int((t - T) * cfps)):int(t * cfps)].mean(1)
        b = chroma[:, int(t * cfps):int((t + T) * cfps)].mean(1)
        cn.append(1 - np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-9))
    cn = np.nan_to_num(np.array(cn))
    phase_stats = []
    for ph in range(4):
        m = (np.arange(len(beats)) % 4) == ph
        phase_stats.append({'phase': ph, 'kick': float(bk[m].mean()), 'snare': float(bs[m].mean()), 'chroma_change': float(cn[m].mean())})
    # downbeat: chord changes land on 1; kick on 1 (and 3), snare on 2 and 4
    sc = [ps['chroma_change'] / (np.mean(cn) + 1e-9) + 0.5 * (ps['kick'] / (bk.mean() + 1e-9)) - 0.5 * (ps['snare'] / (bs.mean() + 1e-9)) for ps in phase_stats]
    down = int(np.argmax(sc))
    bars = beats[down::4]

    # bar-level features
    mfcc = librosa.feature.mfcc(y=y, sr=SR, hop_length=HOP * 2, n_mfcc=20)
    rms = librosa.feature.rms(y=y, hop_length=HOP * 2)[0]
    cent = librosa.feature.spectral_centroid(y=y, sr=SR, hop_length=HOP * 2)[0]
    feats = []
    edges = list(bars) + [min(dur, bars[-1] + 4 * T)]
    for a, b in zip(edges[:-1], edges[1:]):
        i0, i1 = int(a * cfps), max(int(a * cfps) + 1, int(b * cfps))
        c = chroma[:, i0:i1].mean(1)
        feats.append(np.r_[c / (np.linalg.norm(c) + 1e-9), mfcc[1:, i0:i1].mean(1), np.log(rms[i0:i1].mean() + 1e-6), cent[i0:i1].mean()])
    F = np.array(feats)
    Fc = F[:, :12]
    Ft = (F[:, 12:] - F[:, 12:].mean(0)) / (F[:, 12:].std(0) + 1e-9)
    # time-delay embedding (2 bars) for repetition structure
    def emb(X):
        return np.hstack([X, np.vstack([X[1:], X[-1:]])])
    def cos_ssm(X):
        Xn = X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-9)
        return Xn @ Xn.T
    S_chroma = cos_ssm(emb(Fc - Fc.mean(0)))
    S_timbre = cos_ssm(emb(Ft))
    S = 0.5 * S_chroma + 0.5 * S_timbre
    nov4 = foote(S, 4)
    nov8 = foote(S, 8)
    nov = 0.5 * nov4 + 0.5 * nov8
    pk = [i for i in range(1, len(nov) - 1) if nov[i] >= nov[i - 1] and nov[i] >= nov[i + 1] and nov[i] > 0.18]
    # min spacing 4 bars, keep stronger
    pk.sort(key=lambda i: -nov[i])
    keep = []
    for i in pk:
        if all(abs(i - j) >= 4 for j in keep):
            keep.append(i)
    keep.sort()

    t_lu, M, Sst, I, LRA = ebur128(track)
    chroma_mean = librosa.feature.chroma_cqt(y=yh, sr=SR, hop_length=2048).mean(1)
    key = key_estimate(chroma_mean)

    res = {
        'duration': dur, 'bpm': round(bpm, 3), 'beat_period': round(T, 5), 'grid_t0': round(float(beats[0]), 4),
        'grid_score': round(float(score), 3), 'librosa_tempo': round(tempo_lib, 2),
        'drift_windows_ms': [(round(a, 2), round(s * 1000, 1), round(q, 2)) for a, s, q in drift],
        'downbeat_phase': down, 'phase_stats': phase_stats, 'phase_scores': [round(float(x), 3) for x in sc],
        'first_downbeat': round(float(bars[0]), 4), 'n_bars': len(bars), 'bar_seconds': round(4 * T, 4),
        'boundary_bars': keep, 'boundary_times': [round(float(bars[i]), 2) for i in keep],
        'novelty': [round(float(x), 3) for x in nov],
        'key_top': [(round(float(c), 3), k) for c, k in key],
        'loudness_integrated_lufs': I, 'lra': LRA,
        'beats': [round(float(b), 4) for b in beats], 'bars': [round(float(b), 4) for b in bars],
    }
    json.dump(res, open(os.path.join(out, 'structure.json'), 'w'), indent=1)
    np.savez(os.path.join(out, 'bars_features.npz'), F=F, S=S, S_chroma=S_chroma, S_timbre=S_timbre, bars=bars, nov=nov,
             t_lu=t_lu, M=M, Sst=Sst)

    fig, ax = plt.subplots(3, 1, figsize=(14, 16), gridspec_kw={'height_ratios': [10, 2, 2]})
    ext = [bars[0], edges[-1], edges[-1], bars[0]]
    ax[0].imshow(S, cmap='magma', extent=ext, aspect='auto', vmin=np.percentile(S, 5), vmax=np.percentile(S, 99))
    for i in keep:
        ax[0].axvline(bars[i], color='c', lw=0.6)
        ax[0].axhline(bars[i], color='c', lw=0.6)
    ax[0].set_title(f'bar-level self-similarity  ·  {bpm:.2f} BPM  ·  bar {4 * T:.3f}s  ·  boundaries (cyan)')
    ax[1].plot(bars, nov, 'k')
    for i in keep:
        ax[1].axvline(bars[i], color='c', lw=0.8)
        ax[1].text(bars[i], 1.02, f'{int(bars[i] // 60)}:{bars[i] % 60:04.1f}', fontsize=7, rotation=90, va='bottom')
    ax[1].set_xlim(0, dur)
    ax[2].plot(t_lu, Sst, lw=0.8, label='short-term LUFS')
    ax[2].plot(t_lu, M, lw=0.3, alpha=0.5, label='momentary')
    ax[2].set_ylim(-45, -5)
    ax[2].set_xlim(0, dur)
    ax[2].legend(fontsize=7)
    for a in ax[1:]:
        a.set_xticks(np.arange(0, dur, 10))
        a.tick_params(labelsize=7)
        a.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(out, 'ssm.png'), dpi=70)
    print(json.dumps({k: res[k] for k in ['bpm', 'beat_period', 'grid_t0', 'grid_score', 'librosa_tempo', 'downbeat_phase', 'phase_scores', 'first_downbeat', 'n_bars', 'boundary_times', 'key_top', 'loudness_integrated_lufs', 'lra']}, indent=0))
    print('drift ms (start, shift, sharpness):', res['drift_windows_ms'][:40])


if __name__ == '__main__':
    main()
