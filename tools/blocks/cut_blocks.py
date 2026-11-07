import subprocess, os, sys, json, shutil
sys.path.insert(0, '/home/claude/song/tools'); from blocks import BLOCKS, REC
OFF = {1: 11.061, 2: 202.216}
SRC = {1: '/home/claude/ref1/src.mp4', 2: '/home/claude/ref2/src.mp4'}
MP3 = '/home/claude/song/src/track.mp3'
PASS = '/home/claude/fractera-motion-analysis/blocks'
slug = {int(n[:2]): n[:-4] for n in os.listdir(PASS) if n.endswith('.jpg') and n[:2].isdigit()}
out = '/home/claude/repo-staging/library/blocks'
index = []
for i, (num, t0) in enumerate(BLOCKS):
    part = 1 if num <= 38 else 2
    t1 = REC[0][1] if num == 38 else REC[1][1] if num == 58 else BLOCKS[i + 1][1]
    a = max(t0 - 1.0, REC[part - 1][0]); b = min(t1 + 1.0, REC[part - 1][1])
    d = os.path.join(out, slug[num]); os.makedirs(d, exist_ok=True)
    cmd = ['ffmpeg', '-v', 'error', '-y', '-ss', f'{a - OFF[part]:.3f}', '-t', f'{b - a:.3f}', '-i', SRC[part],
           '-ss', f'{a:.3f}', '-t', f'{b - a:.3f}', '-i', MP3, '-map', '0:v:0', '-map', '1:a:0',
           '-vf', 'scale=1280:-2,fps=30', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '23', '-pix_fmt', 'yuv420p',
           '-c:a', 'aac', '-b:a', '96k', '-movflags', '+faststart', os.path.join(d, 'clip.mp4')]
    subprocess.run(cmd, check=True)
    shutil.copy(os.path.join(PASS, slug[num] + '.jpg'), os.path.join(d, 'passport.jpg'))
    index.append({'id': slug[num], 'num': num, 'part': part, 't0': round(t0, 2), 't1': round(t1, 2),
                  'clip_window': [round(a, 2), round(b, 2)], 'files': {'clip': 'clip.mp4', 'passport': 'passport.jpg'},
                  'level': 3 if num == 30 else 1, 'note': 'время в секундах мастер-трека; границы блока ±1 с (по листам 1 кадр/с)'})
    print(num, slug[num], round(b - a, 1), 's', flush=True)
json.dump({'schema': 'block-index/1', 'source': 'LGTM reference (screen recordings aligned to the master track)', 'blocks': index},
          open('/home/claude/repo-staging/library/blocks.json', 'w'), ensure_ascii=False, indent=1)
print('BLOCKS_DONE')
