# fractera-video-clip-starter

Стартер музыкального клипа FRACTERA: всё, что сделано на этапе разбора образца, навыки конвейера «образец + бриф → новый клип» и 3D-движок рендера. Работа идёт по навыку `.claude/skills/reference-to-clip`; состояние проекта — в `JOURNAL.md`, правила для Claude — в `CLAUDE.md`.

## Что внутри

- `reference/` — образец: лёгкая копия клипа на шкале трека (дыры без записи подписаны) и мастер-трек.
- `library/` — 58 блоков образца: короткий клип со звуком и кадр-паспорт на каждый; `raw/` — сырые, `ready/` — с чертежом. Каталог с описаниями — `library/README.md`.
- `analysis/` — замеры трека: сетка, разделы, громкость, два голоса (карта `analysis/song/song_map.png`), листы кадров.
- `tools/` — скрипты замеров и нарезки.
- `engine/` — движок 3D-рендера и пробный ролик.
- `docs/` — ссылки на живые документы в claude.ai и их копии (ТЗ на трек, библиотека блоков, 3D-спека).
- `.claude/skills/` — навыки конвейера и наборы правил.

## Быстрый старт

```bash
# замеры трека (подробно — tools/audio/README.md)
pip install librosa soundfile onnxruntime scikit-learn matplotlib
python3 tools/audio/structure.py reference/lgtm-track.mp3 analysis/song

# движок (подробно — engine/README.md)
cd engine && npm ci && npm i --no-save playwright && npx playwright install chromium
node render.mjs frames 1.2 5.0 9.5
```

Исходные записи образца (174 и 116 МБ) в репозиторий не входят: GitHub не принимает файлы больше 100 МБ. Они у Романа. Репозиторий приватный: в нём материалы чужого клипа для внутреннего разбора.
