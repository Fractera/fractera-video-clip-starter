"""Fractera Lego Motion — synthesized score + SFX for test 01 (S01–S03), locked to the scene's event times.
numpy only. Writes out/test01_audio.wav (48 kHz stereo). Loudness is normalized later by ffmpeg loudnorm."""
import numpy as np, wave

SR, DUR = 48000, 16.0
N = int(SR * DUR)
mix = np.zeros((N, 2))
rev_send = np.zeros((N, 2))
rng = np.random.default_rng(7)
BPM = 108.0
BEAT = 60.0 / BPM

def midi(m): return 440.0 * 2 ** ((m - 69) / 12)

def place(sig, t0, gain=1.0, pan=0.0, rev=0.0):
    """Add a mono signal at time t0 (s) with equal-power pan (-1 left … +1 right) and a reverb send."""
    i0 = int(t0 * SR)
    if i0 >= N or i0 + len(sig) <= 0: return
    s = sig
    if i0 < 0: s, i0 = s[-i0:], 0
    s = s[: N - i0] * gain
    l, r = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
    mix[i0:i0 + len(s), 0] += s * l; mix[i0:i0 + len(s), 1] += s * r
    if rev: rev_send[i0:i0 + len(s), 0] += s * l * rev; rev_send[i0:i0 + len(s), 1] += s * r * rev

def tt(d): return np.arange(int(d * SR)) / SR

def tone(f, d, partials=((1, 1.0),), decay=1.0, attack=0.004):
    t = tt(d); env = np.minimum(1, t / attack) * np.exp(-t / decay)
    return env * sum(a * np.sin(2 * np.pi * f * k * t) for k, a in partials)

def band_noise(d, lo, hi, decay=None, attack=0.002, sweep=None):
    """Noise through an FFT band-pass; optional exponential decay; optional sweep=(lo2,hi2) via crossfade of two bands."""
    n = int(d * SR); x = rng.standard_normal(n)
    def bp(lo_, hi_):
        X = np.fft.rfft(x); f = np.fft.rfftfreq(n, 1 / SR)
        X[(f < lo_) | (f > hi_)] = 0; y = np.fft.irfft(X, n); return y / (np.abs(y).max() + 1e-9)
    y = bp(lo, hi)
    if sweep: k = np.linspace(0, 1, n); y = y * (1 - k) + bp(*sweep) * k
    t = np.arange(n) / SR
    env = np.minimum(1, t / attack) * (np.exp(-t / decay) if decay else np.sin(np.pi * np.clip(t / d, 0, 1)))
    return y * env

def marimba(f, d=0.9): return tone(f, d, ((1, 1.0), (4.0, 0.35), (9.2, 0.08)), decay=0.28, attack=0.002)
def pluck(f, d=1.6): return tone(f, d, ((1, 1.0), (2, 0.28), (3, 0.12), (5.01, 0.05)), decay=0.65, attack=0.003)
def click(f=3200, d=0.03, g=1.0): return tone(f, d, ((1, 1.0), (1.7, 0.5)), decay=0.006, attack=0.0005) * g
def thud(f=70, d=0.35): t = tt(d); return np.sin(2 * np.pi * (f + 60 * np.exp(-t * 30)) * t) * np.exp(-t / 0.09)
def chirp(f0, f1, d=0.12):
    t = tt(d); ph = 2 * np.pi * np.cumsum(f0 + (f1 - f0) * (t / d)) / SR
    return (np.sin(ph) + 0.25 * np.sin(2 * ph)) * np.sin(np.pi * t / d) ** 0.7

# ─────────────── SCORE ───────────────
# Origin (0–5.6 s): sparse glassy plucks, A-minor pentatonic, rising.
for i, m in enumerate([69, 76, 72, 79, 76, 81, 79, 84, 81]):
    place(pluck(midi(m)), 0.35 + i * BEAT, gain=0.11, pan=0.5 - i * 0.1, rev=0.6)
# Materialization shimmer (5.55–6.25): high partials gliding up.
t = tt(0.75); sh = sum(np.sin(2 * np.pi * (f * (1 + 0.5 * t / 0.75)) * t) for f in (1760, 2217, 2637, 3520))
place(sh * np.sin(np.pi * t / 0.75) ** 2 * (0.6 + 0.4 * np.sin(2 * np.pi * 14 * t)), 5.55, gain=0.035, rev=0.8)
# One bass hit when the materialized toy lands (6.05 s).
place(tone(midi(33), 1.4, ((1, 1.0), (2, 0.3)), decay=0.5), 6.05, gain=0.5, rev=0.2)
# Easy (7.2–16 s): marimba groove at 108 BPM; claps and bass join after the snap (9.45 s).
motif = [76, 79, 81, 79, 76, None, 74, 72, 74, 76, 79, 76, 74, None, 72, None]  # 8ths, 2 bars
start = 7.25
k = 0
while start + k * BEAT / 2 < DUR - 0.3:
    m = motif[k % len(motif)]
    tk = start + k * BEAT / 2
    quiet = tk < 9.45
    if m: place(marimba(midi(m)), tk, gain=0.09 if quiet else 0.16, pan=0.15 * np.sin(k), rev=0.35)
    k += 1
b = 0
while 9.45 + b * BEAT < DUR - 0.2:
    tb = 9.45 + b * BEAT
    root = [45, 45, 41, 43][(b // 4) % 4]
    place(tone(midi(root), 0.5, ((1, 1.0), (2, 0.4), (3, 0.15)), decay=0.22), tb, gain=0.28)
    if b % 2 == 1: place(band_noise(0.16, 900, 5200, decay=0.035), tb, gain=0.12, pan=0.1, rev=0.3)   # clap on 2 & 4
    place(band_noise(0.05, 6000, 14000, decay=0.012), tb + BEAT / 2, gain=0.05, pan=-0.2)          # off-beat hat
    b += 1

# ─────────────── SFX (event-locked to scene.js times) ───────────────
for i in range(9):                                    # parts fly in from the right (0.3 + i·0.07)
    place(band_noise(0.55, 300, 2500, sweep=(900, 6000)), 0.3 + i * 0.07, gain=0.10, pan=0.8 - i * 0.06, rev=0.3)
for i in range(4):                                    # callouts A, C, E, B: dot pop + typed letters
    T0 = 1.9 + i * 0.12
    place(chirp(1200, 1800, 0.05), T0, gain=0.08, pan=0.4, rev=0.2)
    for c in range(7): place(click(2600 + 300 * (c % 3), g=0.5), T0 + 0.48 + c * 0.045, gain=0.10, pan=0.45)
for i in range(9):                                    # parts snap home (3.85 + …)
    place(click(1900 + 120 * i, 0.04), 3.85 + (0 if i == 0 else 0.04 + i * 0.025) + 0.2, gain=0.22, rev=0.15)
t = tt(0.75); place(np.sin(2 * np.pi * (180 + 60 * t) * t) * 0.3 * np.sin(np.pi * t / 0.75), 4.47, gain=0.10)  # servo turn
place(chirp(300, 700, 0.22), 5.42, gain=0.10, rev=0.3)                        # spring take-off
place(thud(65), 6.05, gain=0.55); place(band_noise(0.5, 200, 1800, decay=0.12), 6.05, gain=0.08, rev=0.4)  # landing + dust
place(chirp(900, 1400, 0.07), 7.2, gain=0.08, pan=-0.7)                        # terminal panel in
for c in range(22): place(click(2400 + 200 * (c % 4), g=0.6), 7.65 + c * (0.95 / 22), gain=0.11, pan=-0.6)  # typing
for j in range(5): place(click(1500, 0.02), 8.8 + j * 0.15, gain=0.05, pan=-0.6)       # processing ticks
place(tone(midi(88), 0.6, ((1, 1.0), (2, 0.2)), decay=0.18) + tone(midi(95), 0.6, decay=0.15), 9.5, gain=0.07, pan=-0.6, rev=0.4)  # success
place(band_noise(1.4, 250, 2200, sweep=(500, 3500)), 7.75, gain=0.07, pan=0.6, rev=0.3)      # cursor carries the brick in
place(click(4200, 0.03), 9.32, gain=0.12, pan=0.3)                              # cursor press
place(click(2600, 0.05), 9.45, gain=0.45); place(thud(90, 0.3), 9.45, gain=0.42)  # SNAP
place(band_noise(0.6, 400, 3000, decay=0.15), 9.46, gain=0.10, rev=0.4)         # dust puff
place(chirp(880, 1320, 0.09), 9.76, gain=0.10, rev=0.3); place(chirp(1100, 1650, 0.1), 9.87, gain=0.10, rev=0.3)  # happy two-tone
place(chirp(250, 520, 0.18), 9.8, gain=0.07)                                    # hop
place(band_noise(0.22, 1500, 7000, decay=0.06), 10.0, gain=0.10, pan=0.4); place(chirp(700, 1500, 0.06), 10.05, gain=0.08, pan=0.4)  # flag pops
place(chirp(1200, 1800, 0.05), 10.15, gain=0.08, pan=0.55)                      # callout F
for c in range(10): place(click(2600 + 300 * (c % 3), g=0.5), 10.63 + c * 0.036, gain=0.10, pan=0.55)
for i in range(4): place(tone(midi(67 + i * 2), 0.25, ((1, 1.0), (3, 0.2)), decay=0.05), 10.6 + i * 0.14 + 0.18, gain=0.12, rev=0.3)  # caption words land

# ─────────────── reverb (exponential noise IR), master ───────────────
ir_len = int(1.6 * SR); tir = np.arange(ir_len) / SR
ir = rng.standard_normal((ir_len, 2)) * np.exp(-tir / 0.45)[:, None]; ir[:int(0.012 * SR)] = 0; ir /= np.sqrt((ir ** 2).sum(0))
L = 1 << int(np.ceil(np.log2(N + ir_len)))
wet = np.stack([np.fft.irfft(np.fft.rfft(rev_send[:, c], L) * np.fft.rfft(ir[:, c], L), L)[:N] for c in range(2)], 1)
out = mix + 0.35 * wet
fade = np.ones(N); nf = int(0.6 * SR); fade[-nf:] = np.linspace(1, 0, nf) ** 2; out *= fade[:, None]
out = np.tanh(out * 1.3) / np.tanh(1.3)
out /= max(1e-9, np.abs(out).max() / 0.9)
pcm = (out * 32767).astype(np.int16)
with wave.open('out/test01_audio.wav', 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print('audio written', pcm.shape, 'peak', np.abs(out).max(), 'rms dBFS', 20 * np.log10(np.sqrt((out ** 2).mean()) + 1e-9))
