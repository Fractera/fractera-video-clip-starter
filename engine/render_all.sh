#!/bin/bash
# Пробный ролик test 01 (S01–S03, 16 с): видео двумя кусками → склейка → звук → out/test01.mp4
set -e
cd "$(dirname "$0")"
node render.mjs video 0 8 out/partA.mp4 30 2>&1 | grep -v 'GL Driver'
node render.mjs video 8 16 out/partB.mp4 30 2>&1 | grep -v 'GL Driver'
printf "file 'partA.mp4'\nfile 'partB.mp4'\n" > out/list.txt
ffmpeg -y -loglevel error -f concat -safe 0 -i out/list.txt -c copy out/test01_video.tmp.mp4 && mv out/test01_video.tmp.mp4 out/test01_video.mp4
python3 audio.py
ffmpeg -y -loglevel error -i out/test01_video.mp4 -i out/test01_audio.wav -map 0:v -map 1:a -c:v copy \
  -af loudnorm=I=-14:TP=-1:LRA=11 -ar 48000 -c:a aac -b:a 192k -shortest out/test01.mp4
echo ALL_DONE
