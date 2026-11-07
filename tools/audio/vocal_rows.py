import sys, os, numpy as np, librosa, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); from blocks import BLOCKS, REC
path, t_from, t_to, out = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), sys.argv[4]
ROW = 30.0
y, sr = librosa.load(path, sr=22050, mono=True, offset=t_from, duration=t_to - t_from)
S = librosa.amplitude_to_db(np.abs(librosa.stft(y, n_fft=2048, hop_length=256)), ref=np.max)
freqs = librosa.fft_frequencies(sr=sr, n_fft=2048)
nrows = int(np.ceil((t_to - t_from) / ROW))
fig, ax = plt.subplots(nrows, 1, figsize=(16, 2.6 * nrows))
for r in range(nrows):
    a = t_from + r * ROW; b = min(t_to, a + ROW)
    i0, i1 = int((a - t_from) * sr / 256), int((b - t_from) * sr / 256)
    ax[r].pcolormesh(t_from + np.arange(i0, min(i1, S.shape[1])) * 256 / sr, freqs, S[:, i0:min(i1, S.shape[1])], vmin=-75, vmax=0, cmap='magma', shading='auto', rasterized=True)
    ax[r].set_yscale('log'); ax[r].set_ylim(90, 6000); ax[r].set_xlim(a, a + ROW)
    ax[r].set_xticks(np.arange(np.ceil(a), b + 0.01, 1)); ax[r].tick_params(labelsize=6)
    ax[r].set_xticklabels([f'{int(t // 60)}:{int(t % 60):02d}' if int(t) % 5 == 0 else '' for t in np.arange(np.ceil(a), b + 0.01, 1)])
    for n, t in BLOCKS:
        if a <= t < b:
            ax[r].axvline(t, color='cyan', lw=1); ax[r].text(t + 0.1, 4500, str(n), color='cyan', fontsize=9, weight='bold')
    for ra, rb in REC:
        if rb < a or ra > b: continue
    if not any(ra <= a + 1 and b - 1 <= rb for ra, rb in REC):
        ax[r].text(a + 0.2, 120, 'no video in recordings for part of this row', color='w', fontsize=7)
plt.tight_layout(); plt.savefig(out, dpi=62)
