import sys, os, json, numpy as np, librosa, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); from blocks import BLOCKS
path, vm, t_from, t_to, out = sys.argv[1], sys.argv[2], float(sys.argv[3]), float(sys.argv[4]), sys.argv[5]
segs = json.load(open(vm))['segments']
fr2 = np.load(os.path.join(os.path.dirname(os.path.abspath(vm)), 'voice_frames2.npz'))
FPS = 22050 / 256
ROW = 30.0
y, sr = librosa.load(path, sr=22050, mono=True, offset=t_from, duration=t_to - t_from)
S = librosa.amplitude_to_db(np.abs(librosa.stft(y, n_fft=2048, hop_length=256)), ref=np.max)
freqs = librosa.fft_frequencies(sr=sr, n_fft=2048)
nrows = int(np.ceil((t_to - t_from) / ROW))
fig, ax = plt.subplots(nrows, 1, figsize=(16, 2.4 * nrows))
for r in range(nrows):
    a = t_from + r * ROW; b = min(t_to, a + ROW)
    i0, i1 = int((a - t_from) * sr / 256), min(int((b - t_from) * sr / 256), S.shape[1])
    ax[r].pcolormesh(t_from + np.arange(i0, i1) * 256 / sr, freqs, S[:, i0:i1], vmin=-75, vmax=0, cmap='gray_r', shading='auto', rasterized=True)
    ax[r].set_yscale('log'); ax[r].set_ylim(60, 6000); ax[r].set_xlim(a, a + ROW)
    # flat high-band frames (possible tuned/robotic singing above 130 Hz)
    j0, j1 = int(a * FPS), int(b * FPS)
    stdH = fr2['stdH'][j0:j1]; fH = fr2['fH'][j0:j1]; vH = fr2['vH'][j0:j1]
    tt = np.arange(j0, j1) / FPS
    flat = vH & (np.nan_to_num(stdH, nan=999) < 6)
    ax[r].scatter(tt[flat], fH[flat], s=2, color='magenta')
    for s0, s1, l in segs:
        if s1 < a or s0 > b: continue
        ax[r].axvspan(max(s0, a), min(s1, b), ymin=0, ymax=0.08, color={'bot': '#E8643C', 'main': '#3B6FD8'}.get(l, '#999'), alpha=0.9)
    for n, t in BLOCKS:
        if a <= t < b:
            ax[r].axvline(t, color='green', lw=0.8); ax[r].text(t + 0.1, 4300, str(n), color='green', fontsize=9, weight='bold')
    ax[r].set_xticks(np.arange(np.ceil(a), b + 0.01, 1)); ax[r].tick_params(labelsize=6)
    ax[r].set_xticklabels([f'{int(t // 60)}:{int(t % 60):02d}' if int(t) % 5 == 0 else '' for t in np.arange(np.ceil(a), b + 0.01, 1)])
plt.tight_layout(); plt.savefig(out, dpi=60)
