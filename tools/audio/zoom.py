import sys, numpy as np, librosa, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
path = sys.argv[1]; out = sys.argv[2]; segs = [tuple(map(float, s.split('-'))) for s in sys.argv[3:]]
fig, ax = plt.subplots(len(segs), 1, figsize=(14, 2.7 * len(segs)))
for k, (a, b) in enumerate(segs):
    y, sr = librosa.load(path, sr=22050, mono=True, offset=a, duration=b - a)
    S = librosa.amplitude_to_db(np.abs(librosa.stft(y, n_fft=4096, hop_length=128)), ref=np.max)
    fr = librosa.fft_frequencies(sr=sr, n_fft=4096); t = a + np.arange(S.shape[1]) * 128 / sr
    m = fr <= 3000
    ax[k].pcolormesh(t, fr[m], S[m], vmin=-70, vmax=0, cmap='magma', shading='auto', rasterized=True)
    f0, vf, vp = librosa.pyin(y, fmin=70, fmax=900, sr=sr, frame_length=2048, hop_length=128, resolution=0.02)
    tf = a + np.arange(len(f0)) * 128 / sr
    ax[k].plot(tf, f0, color='cyan', lw=0.8)
    ax[k].set_title(f'{int(a//60)}:{a%60:04.1f} - {int(b//60)}:{b%60:04.1f}', fontsize=9); ax[k].set_ylim(60, 3000)
    ax[k].tick_params(labelsize=7)
plt.tight_layout(); plt.savefig(out, dpi=62)
