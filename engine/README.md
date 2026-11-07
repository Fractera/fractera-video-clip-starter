# engine — движок рендера

Сцена — чистая функция времени: `window.renderAt(t)` рисует кадр 1920×1080 в момент `t` (секунды). Поэтому рендер детерминированный: любой кадр можно перерисовать отдельно, а ролик — рендерить кусками параллельно. По навыку reference-to-clip так делается каждая сцена клипа (шаг 14).

## Файлы

| Файл | Что |
| --- | --- |
| `index.html` | сцена: холст Three.js, SVG-линии выносок, панель терминала, подпись по словам; шрифты Inter и JetBrains Mono из npm |
| `scene.js` | движок и тест 01 — S01–S03: сборка фигурки → материализация → кирпич LANDING (16 с) |
| `render.mjs` | headless Chrome (Playwright, WebGL через SwiftShader) вызывает `renderAt` покадрово и отдаёт JPEG прямо в ffmpeg |
| `audio.py` | синтез музыки и звуков под события сцены (numpy, 108 BPM) → `out/test01_audio.wav` |
| `render_all.sh` | весь тест 01: видео двумя кусками → склейка → звук → `out/test01.mp4` |
| `out/` | `fractera-lego-motion_test01.mp4` — готовый пробный ролик (16 с, 1080p30, звук ≈ −13 LUFS); `sheetA.jpg`, `sheetB.jpg` — листы кадров |

Тест 01 — первая адаптация блока 4 образца (сборка фигурки из деталей), см. `library/README.md`.

## Запуск

```bash
cd engine
npm ci                                   # three и шрифты
# если Playwright в системе нет:
npm i --no-save playwright && npx playwright install chromium

node render.mjs frames 2.0 6.5 10.6      # проверочные кадры → frames/t*.jpg
node render.mjs video 0 8 out/partA.mp4 30
./render_all.sh                          # весь тест 01 → out/test01.mp4
```

Скорость без GPU ≈ 0.9 с на кадр 1080p на 2 ядрах: 16 с ролика (480 кадров) ≈ 7–8 минут. Длинные сцены рендерить кусками в несколько процессов и склеивать (`ffmpeg -f concat -c copy`).

`render.mjs` ищет Playwright сначала в `engine/node_modules`, потом по пути из `PLAYWRIGHT_MJS`, потом в `/opt/npm-tools` (облачная песочница Claude).
