"""MDX-Net vocal separation (UVR-MDX-NET-Voc_FT) with onnxruntime + numpy STFT.

Mirrors UVR's SeperateMDX.demix/run_model: torch.stft semantics (center, reflect,
periodic Hann), channel order (c0re, c0im, c1re, c1im), first 3 bins zeroed,
denoise = average of f(x) and -f(-x), Hann-window overlap-add, compensate.

usage: python3 -I separate.py MIX.(mp3|wav) OUT_DIR [--no-denoise] [--seconds N]
"""
import sys, time, subprocess, os
import numpy as np
import onnxruntime as ort
import soundfile as sf

MODEL = os.environ.get('UVR_MODEL', 'models/UVR-MDX-NET-Voc_FT.onnx')
N_FFT, HOP, DIM_F, DIM_T = 7680, 1024, 3072, 256
COMPENSATE = 1.021
OVERLAP = 0.25
SR = 44100
TRIM = N_FFT // 2
CHUNK = HOP * (DIM_T - 1)
N_BINS = N_FFT // 2 + 1
WIN = (0.5 - 0.5 * np.cos(2 * np.pi * np.arange(N_FFT) / N_FFT)).astype(np.float32)  # periodic Hann


def load(path):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-f', 'f32le', '-ac', '2', '-ar', str(SR), '-'],
                         check=True, capture_output=True).stdout
    return np.frombuffer(raw, dtype=np.float32).reshape(-1, 2).T.copy()


def stft(x):  # x [C, N] -> [C, bins, frames]
    p = N_FFT // 2
    xp = np.pad(x, ((0, 0), (p, p)), mode='reflect')
    frames = 1 + (xp.shape[1] - N_FFT) // HOP
    idx = np.arange(N_FFT)[None, :] + HOP * np.arange(frames)[:, None]
    return np.fft.rfft(xp[:, idx] * WIN, axis=-1).transpose(0, 2, 1)


def istft(X, length):  # X [C, bins, frames]
    fr = np.fft.irfft(X.transpose(0, 2, 1), n=N_FFT, axis=-1).astype(np.float32) * WIN
    frames = fr.shape[1]
    total = N_FFT + HOP * (frames - 1)
    y = np.zeros((X.shape[0], total), np.float32)
    ws = np.zeros(total, np.float32)
    w2 = WIN ** 2
    for t in range(frames):
        y[:, t * HOP:t * HOP + N_FFT] += fr[:, t]
        ws[t * HOP:t * HOP + N_FFT] += w2
    y /= np.where(ws > 1e-11, ws, 1.0)
    p = N_FFT // 2
    return y[:, p:p + length]


def to_model(X):  # [2, bins, frames] complex -> [1, 4, DIM_F, DIM_T]
    m = np.stack([X[0].real, X[0].imag, X[1].real, X[1].imag])[:, :DIM_F, :]
    return m[None].astype(np.float32)


def from_model(m):  # [1, 4, DIM_F, DIM_T] -> [2, bins, frames]
    m = m[0]
    pad = np.zeros((4, N_BINS - DIM_F, m.shape[-1]), np.float32)
    m = np.concatenate([m, pad], axis=1)
    return np.stack([m[0] + 1j * m[1], m[2] + 1j * m[3]])


def main():
    mix_path, out_dir = sys.argv[1], sys.argv[2]
    denoise = '--no-denoise' not in sys.argv
    secs = None
    if '--seconds' in sys.argv:
        secs = float(sys.argv[sys.argv.index('--seconds') + 1])
    os.makedirs(out_dir, exist_ok=True)
    so = ort.SessionOptions()
    so.intra_op_num_threads = os.cpu_count()
    sess = ort.InferenceSession(MODEL, so, providers=['CPUExecutionProvider'])
    run = lambda spec: sess.run(None, {'input': spec})[0]

    mix = load(mix_path)
    if secs:
        mix = mix[:, :int(secs * SR)]
    n = mix.shape[1]
    gen = CHUNK - 2 * TRIM
    pad = gen + TRIM - (n % gen)
    mixture = np.concatenate([np.zeros((2, TRIM), np.float32), mix, np.zeros((2, pad), np.float32)], 1)
    step = int((1 - OVERLAP) * CHUNK)
    result = np.zeros_like(mixture)
    divider = np.zeros_like(mixture)
    starts = list(range(0, mixture.shape[1], step))
    t0 = time.time()
    for k, i in enumerate(starts):
        end = min(i + CHUNK, mixture.shape[1])
        actual = end - i
        win = np.hanning(actual).astype(np.float32)
        part = mixture[:, i:end]
        if actual < CHUNK:
            part = np.concatenate([part, np.zeros((2, CHUNK - actual), np.float32)], 1)
        spek = to_model(stft(part))
        spek[:, :, :3, :] = 0
        pred = (-run(-spek) * 0.5 + run(spek) * 0.5) if denoise else run(spek)
        wav = istft(from_model(pred), CHUNK)
        result[:, i:end] += wav[:, :actual] * win
        divider[:, i:end] += win
        if k % 5 == 0 or k == len(starts) - 1:
            el = time.time() - t0
            print(f'chunk {k + 1}/{len(starts)}  {el:.0f}s elapsed, ~{el / (k + 1) * (len(starts) - k - 1):.0f}s left', flush=True)
    voc = (result / np.where(divider > 0, divider, 1.0))[:, TRIM:TRIM + n] * COMPENSATE
    inst = mix - voc
    sf.write(os.path.join(out_dir, 'vocals.wav'), voc.T, SR, subtype='FLOAT')
    sf.write(os.path.join(out_dir, 'instrumental.wav'), inst.T, SR, subtype='FLOAT')
    rms = lambda a: 20 * np.log10(np.sqrt(np.mean(a ** 2)) + 1e-12)
    print(f'DONE  mix {rms(mix):.1f} dB  vocals {rms(voc):.1f} dB  inst {rms(inst):.1f} dB  in {time.time() - t0:.0f}s')


if __name__ == '__main__':
    main()
