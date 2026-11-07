# FRACTERA — разбор трека LGTM и инструменты замера

Замеры эталонного трека (MP3, 5:05) и скрипты, которыми мы будем проверять наш трек из Suno. Параметры и правила записаны в документе «FRACTERA — ТЗ на трек» (https://claude.ai/artifact/H7yvxc8Qkg5sTGsa4NKcHr).

## Что внутри

| Файл | Что это |
| --- | --- |
| `out/song_map.png` | карта трека: разделы, основной голос и бот, громкость, номера блоков видео |
| `out/ssm.png` | самоподобие тактов (по нему найдены разделы и повторы припевов) |
| `out/structure.json` | темп, доли, такты, границы разделов, громкость, оценка тональности |
| `out/voice_map_final.json` | реплики бота и основного голоса с таймкодами, разбивка по блокам 1–58 |
| `out/voice_map_v2.json`, `out/voice_map_v3.json` | результаты двух детекторов бота до объединения |
| `out/alignment.json` | где записи экрана лежат в треке (0:11.06–2:41.02 и 3:22.22–5:02.73) |
| `out/cuts_vs_beats.json` | жёсткие склейки эталона против сетки долей |
| `tools/` | скрипты, порядок запуска ниже |

## Главные замеры

- 120 BPM, 4/4, такт 2.0 с, 152 такта; первые ~1:16 чуть медленнее (≈ 118.5–119 BPM).
- Громкость −16.1 LUFS, LRA 4.6 LU; интро −22, куплеты ≈ −17.5, припевы −16…−13.5.
- Основной голос: A3–C5, медиана D#4, живой. Бот: около F2 (78–117 Гц), монотон, высота дрожит на 2–4 цента.
- Бот: ≈ 34 с из ≈ 235 с вокала (≈ 14 %), 12 выходов, в припевах его нет.

## Запуск

Нужны Python 3, ffmpeg и `pip install librosa soundfile onnxruntime scikit-learn matplotlib`. Модель отделения вокала (66 МБ) скачивается с GitHub:

```bash
mkdir -p models && curl -L -o models/UVR-MDX-NET-Voc_FT.onnx \
  https://github.com/TRvlvr/model_repo/releases/download/all_public_uvr_models/UVR-MDX-NET-Voc_FT.onnx
```

В `tools/separate.py` путь к модели задан константой `MODEL` — поправь под свою папку.

```bash
python3 tools/separate.py track.mp3 work/full --no-denoise        # вокал и музыка, ~6 мин на 2 ядрах
python3 tools/structure.py track.mp3 out                           # темп, такты, разделы, громкость
python3 tools/voices2.py work/full/vocals.wav track.mp3 out        # бот: низкий pYIN
python3 tools/voices3.py work/full/vocals.wav track.mp3 out        # бот: кепстральная гребёнка
python3 tools/merge_voices.py out                                  # итоговая карта голосов
python3 tools/songmap.py out out/song_map.png                      # картинка
```

`tools/blocks.py` хранит таймкоды 58 блоков эталона; для нашего трека его заменит карта наших блоков. `zoom.py`, `zoomlin.py`, `vocal_rows.py` и `label_rows.py` рисуют спектрограммы, чтобы проверять детектор глазами.

## Ограничения

- Бота под основным голосом детектор не видит. Если наш бот получится выше или с другим эффектом, пороги нужно перенастроить на первой генерации.
- Номера блоков привязаны к времени с точностью ±1 с.
- Песня эталона — только для внутреннего анализа: берём структуру и приёмы, не слова и не мелодию.
