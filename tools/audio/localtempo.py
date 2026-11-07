import sys, subprocess, numpy as np, librosa, scipy.ndimage as ndi
SR=22050; HOP=256
raw=subprocess.run(['ffmpeg','-v','error','-i',sys.argv[1],'-f','f32le','-ac','1','-ar',str(SR),'-'],check=True,capture_output=True).stdout
y=np.frombuffer(raw,dtype=np.float32).copy()
yh,yp=librosa.effects.hpss(y)
fps=SR/HOP
for name,sig in [('perc',yp),('full',y)]:
    o=librosa.onset.onset_strength(y=sig,sr=SR,hop_length=HOP,aggregate=np.median); o=o/o.max()
    n=np.arange(len(o))
    for a,b in [(0,30),(15,45),(30,60),(45,76),(76,120),(120,160),(200,240),(240,300)]:
        seg=o[int(a*fps):int(b*fps)]; nn=np.arange(len(seg))
        best=None
        for bpm in np.arange(112,128,0.02):
            P=60/bpm*fps; ph=(nn%P)/P
            h,_=np.histogram(ph,bins=48,range=(0,1),weights=seg); h=ndi.uniform_filter1d(h,3,mode='wrap')
            s=h.max()/(h.mean()+1e-9)
            if best is None or s>best[0]: best=(s,bpm,(np.argmax(h)+.5)/48*P/fps + a)
        # phase relative to the global grid (t0=0.0273, T=0.5)
        rel=((best[2]-0.0273+0.25)%0.5)-0.25
        print(f'{name} {a:>3}-{b:<3}s  best {best[1]:.2f} BPM  sharp {best[0]:.2f}  phase vs global grid {rel*1000:+.0f} ms')
