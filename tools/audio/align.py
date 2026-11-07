"""Find where each screen recording sits inside the full track.

Cross-correlates onset-strength envelopes (robust to level/EQ), then refines
with raw-waveform correlation around the coarse lag.
usage: python3 -I align.py TRACK REC1 REC2 OUT_JSON
"""
import sys, json, subprocess
import numpy as np
import librosa

SR = 22050
HOP = 256


def load(path):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-vn', '-f', 'f32le', '-ac', '1', '-ar', str(SR), '-'],
                         check=True, capture_output=True).stdout
    y = np.frombuffer(raw, dtype=np.float32).copy()
    return y / (np.max(np.abs(y)) + 1e-9)


def env(y):
    e = librosa.onset.onset_strength(y=y, sr=SR, hop_length=HOP)
    e = e - e.mean()
    return e / (e.std() + 1e-9)


def xcorr_lag(a, b):
    """lag L (in samples of the arrays) such that b[n] ~ a[n + L]"""
    n = len(a) + len(b)
    nfft = 1 << (n - 1).bit_length()
    c = np.fft.irfft(np.fft.rfft(a, nfft) * np.conj(np.fft.rfft(b, nfft)), nfft)
    c = np.concatenate([c[-(len(b) - 1):], c[:len(a)]])  # lags -(len(b)-1) .. len(a)-1
    lags = np.arange(-(len(b) - 1), len(a))
    i = int(np.argmax(c))
    srt = np.sort(c)
    return int(lags[i]), float(c[i] / (np.sqrt(np.sum(a ** 2) * np.sum(b ** 2)) + 1e-9)), float(c[i] / (srt[-50] + 1e-9))


def main():
    track, recs, out = sys.argv[1], sys.argv[2:-1], sys.argv[-1]
    yt = load(track)
    et = env(yt)
    res = {'track_seconds': len(yt) / SR, 'recordings': []}
    for r in recs:
        yr = load(r)
        er = env(yr)
        lag, corr, peak_ratio = xcorr_lag(et, er)
        coarse = lag * HOP
        # refine on raw audio: a 20 s window from the middle of the recording
        mid = len(yr) // 2
        seg = yr[mid - 10 * SR: mid + 10 * SR]
        lo = max(0, coarse + mid - 10 * SR - SR // 2)
        hi = min(len(yt), coarse + mid + 10 * SR + SR // 2)
        win = yt[lo:hi]
        c = np.correlate(win, seg, mode='valid')
        fine = lo + int(np.argmax(np.abs(c))) - (mid - 10 * SR)
        rec_len = len(yr) / SR
        res['recordings'].append({
            'file': r, 'rec_seconds': round(rec_len, 3),
            'offset_seconds': round(fine / SR, 3),
            'coarse_offset_seconds': round(coarse / SR, 3),
            'envelope_corr': round(corr, 3), 'peak_vs_50th': round(peak_ratio, 2),
            'covers_track': [round(fine / SR, 2), round(fine / SR + rec_len, 2)]})
        print(res['recordings'][-1], flush=True)
    json.dump(res, open(out, 'w'), indent=1)


if __name__ == '__main__':
    main()
