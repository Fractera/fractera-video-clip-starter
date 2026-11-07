import sys, numpy as np, librosa, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
path = sys.argv[1]; out = sys.argv[2]; segs = [tuple(map(float, s.split('-'))) for s in sys.argv[3:]]
fig, ax = plt.subplots(len(segs), 1, figsize=(14, 2.4 * len(segs)))
for k, (a, b) in enumerate(segs):
    y, sr = librosa.load(path, sr=22050, mono=True, offset=a, duration=b - a)
    S = librosa.amplitude_to_db(np.abs(librosa.stft(y, n_fft=8192, hop_length=128)), ref=np.max)
    fr = librosa.fft_frequencies(sr=sr, n_fft=8192); t = a + np.arange(S.shape[1]) * 128 / sr
    m = fr <= 1200
    ax[k].pcolormesh(t, fr[m], S[m], vmin=-60, vmax=0, cmap='magma', shading='auto', rasterized=True)
    for h in range(85, 1200, 85): ax[k].axhline(h, color='cyan', lw=0.3, alpha=0.5)
    ax[k].set_title(f'{int(a//60)}:{a%60:04.1f} - {int(b//60)}:{b%60:04.1f}   (cyan guides every 85 Hz)', fontsize=8); ax[k].tick_params(labelsize=7)
plt.tight_layout(); plt.savefig(out, dpi=62)
