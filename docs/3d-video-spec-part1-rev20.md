# STACK OVERFLOW — 3D Video Spec (Part 1)

Nov 7, 2026 · @Róman Bolshiyanov

## Overview

An 82-second 3D fragment: a user stacks ten feature bricks on the Claude figure until the tower sways like a snake and falls. The camera then reveals 24 agents who met the same end.

- **Idea:** stacking features works for small builds. Big, reliable products need an architect; without one, even the best coding agent falls.
- **Hero:** the coral Claude figure from the 13 element landings (step 669), made physical.
- **Format:** 16:9 master, 3840×2160, 24 fps, 82 s, 15 shots; a vertical 9:16 cut from the same plates.
- **Look:** premium 3D animation with toy-scale macro realism, on the landings' dark blueprint stage.
- **Text:** English only, no voice-over. Brick labels and the flag live in the 3D scene; every other text is a HUD layer added in post.
- **Place in the series:** Part 1 of 2. A split screen at the start and the end sets up Part 2, "02 · ARCHITECT IT".

| Act | Time | What happens | Feeling |
| --- | --- | --- | --- |
| 0 · Origin | 0:00–0:10 | The figure assembles, turns, jumps and becomes physical; the screen splits | Curiosity |
| 1 · Easy | 0:10–0:25 | The user's cursor places LANDING, BLOG, AUTH | Joy |
| 2 · Weight | 0:25–0:42 | DATABASE, SHOP, DASHBOARD fall from above; push-in to the face; the zigzag starts | Unease |
| 3 · Overload | 0:42–1:00 | Four more bricks, the snake sway, the fall | Panic |
| 4 · Aftermath | 1:00–1:22 | A field of 24 agents; small builds still stand; the lesson; the split returns | Quiet, then a hint of hope |

## Production pipeline

Generate clean 3D plates shot by shot with image-to-video, then add all overlays in post. No video model holds text, counts and one character across 82 s by itself.

1. **Lock the hero.** Capture the final frame of the landing animation in 4K (any element landing), plus front, ¾ and side views. Turn them into a turnaround and an expression sheet (section 5). Approve before any video.
2. **Lock the bricks.** One reference sheet with all ten bricks in stack order, labels to camera (section 6).
3. **Keyframes.** For every shot, make a first and a last frame from the references. On continuous cuts, the last frame of shot N is the first frame of shot N+1.
4. **Animate.** Image-to-video with first/last-frame control, one shot per generation, 3–10 s. Chain two generations for S10 and S14. Make 3–4 takes per shot.
5. **Assemble each prompt** in this order: STYLE + AGENT + BRICKS (only those in frame) + the shot prompt + NEGATIVE (section 12).
6. **Text inside the scene.** Ask the model only for brick labels and the flag. If they smear, generate them blank and add the text in post with planar tracking.
7. **HUD and captions.** Build them in After Effects, Remotion or Motion Canvas from section 9. S01 can be rendered straight from the landing's React figure with Remotion, pixel-identical to the site.
8. **Physics fallback.** If S11–S12 still look fake after four takes, simulate them in Blender (rigid bodies, breakable constraints) and render in the same look.
9. **Crowd.** S14 needs 20+ agents. If the model miscounts, generate 3–4 plates of 6–8 agents and composite them in depth.
10. **Sound and grade** per sections 11 and 4.

## Narrative and on-screen copy

Five beats carry the idea. Every on-screen line is short, original English, and none repeats the brief's wording.

| Beat | What the viewer should feel (never on screen) | On screen | In at |
| --- | --- | --- | --- |
| Ease | A first site is a toy now | One prompt. A website. | 0:12.5 |
| Ease | The second feature is just as easy | Another prompt. A blog. | 0:17 |
| Ease | Nothing hurts yet | So far, so easy. | 0:22 |
| Weight | Each feature adds load to the base | But every feature has weight. | 0:29 |
| Weight | Load calls for structure, i.e. an architect | And weight needs structure. | 0:34.5 |
| Overload | The user prompts faster and faster | More. Faster. Just one more. | 0:43 |
| Overload | Nobody designed the whole | Nobody drew the plan. | 0:50 |
| Fall | The system breaks | FATAL: STACK OVERFLOW | 0:58 |
| Lesson | Small builds survive; big ones need design | Small builds stand. Big ones need a plan. | 1:09 |
| Lesson | The agent was never the problem | It was never the agent. | 1:15 |
| Lesson | The missing architecture was | It was the missing architecture. | 1:17.5 |
| Hook | There is another way (Part 2) | 02 · ARCHITECT IT — next | 1:20 |

**Intro callouts (S01, the landing's style).** A, C and E reuse the landing copy; B gets a new note that foreshadows the story.

- `A  BODY` — ×1 · the Claude Code agent
- `C  ARMS` — ×2 · write code, hand back a commit
- `E  MOUTH` — ×0 · no chatter — tokens saved
- `B  LEGS` — ×4 · carry whatever you stack

**Brick callouts.** One per brick, continuing the landing's letters and alternating sides. The notes slide from confident to sloppy.

| Letter | Brick | Note | Side |
| --- | --- | --- | --- |
| F | LANDING | live in 60 seconds | right |
| G | BLOG | one more prompt | left |
| H | AUTH | sign-up works (mostly) | right |
| I | DATABASE | schema: later | left |
| J | SHOP | payments, taxes, refunds | right |
| K | DASHBOARD | 14 charts, 0 tests | left |
| L | ACCOUNT | roles? copy-pasted | right |
| M | SUBSCRIPTIONS | webhooks everywhere | left |
| N | REDIS | cache the problem | right |
| O | REFERRALS | touches everything | left |

**Other fixed lines**

- Split labels: `01 · STACK IT` (left), `02 · ARCHITECT IT` (right).
- Flag: `I'M OK` → `I'M OK?` → `I'M OK` again, planted beside the fallen agent.
- Counter in S14: `24 AGENTS · 24 TOWERS · 0 BLUEPRINTS`.
- Terminal log, toasts and metrics: section 9.

## Visual style bible

Premium 3D animation with toy-scale macro realism, staged on the dark blueprint floor of the Fractera landings.

- **Render:** physically based, ray-traced look; macro lenses; shallow depth of field; 24 fps with 180° shutter blur; light film grain; no outlines.
- **Stage:** an endless deep-navy floor with a thin slate grid (cells ≈ 0.2 agent widths), fading to black with distance. Soft volumetric haze and dust motes in the light.
- **Agent material:** matte coral plastic, fine diagonal hatching embossed on every face, thin light edge lines: the landing drawing made physical.
- **Brick material:** glossy injection-molded plastic, micro-scratches, a slight glow at the edges, printed labels; plain studs, no logos.
- **Contrast rule:** saturated glossy bricks against the dark stage; the coral agent is the only warm matte object.

| Token | Hex | Use |
| --- | --- | --- |
| Stage | #0E1320 | floor and background |
| Grid | #94A3B8 at 18% | floor lines |
| Line | #E2E8F0 | callout lines, labels, the agent's edge lines |
| Agent coral | #D9694F / #E98A70 / #B9533C | body front / top / sides |
| Eye | #0B0F17 | eye slots |
| Architecture blue | #2563EB | reserved for the final glow and Part 2 |
| OK | #22C55E | HUD success |
| Warning | #F59E0B | HUD warnings |
| Error | #EF4444 | HUD errors, alarm light |

**Color script**

| Act | Key light | Ambient and accents | Air |
| --- | --- | --- | --- |
| 0 · Origin | flat, then a soft top light at materialization | navy and slate grid | clear |
| 1 · Easy | warm 3,200 K from top-left, soft | gentle teal fill, warm glow in the grid | light dust |
| 2 · Weight | neutral 5,000 K, harder shadows | cooler fill, more contrast | thin haze |
| 3 · Overload | low-key cold cyan | red alarm pulse at 1 Hz from the left; a white flash on every impact | dense haze |
| 4 · Aftermath | cool moonlight | warm rim on dust and the gold brick | settling dust, depth fog |
| Hook | near black | #2563EB glow along the grid | clear |

## Hero: the Claude figure

The hero is the landing figure made physical: a wide coral box with two slot eyes, two stub arms, four stub legs and no mouth. Geometry comes from `figure-parts.tsx`; units are body widths (AW). The whole agent stands 0.95 AW tall, which this spec calls one agent-height (AH).

| Part | Count | W × H × D (AW) | Placement | Rules |
| --- | --- | --- | --- | --- |
| Body | 1 | 1.00 × 0.62 × 0.57 | center | flat top: the bricks rest here |
| Eyes | 2 | 0.12 × 0.22 × 0.04 | upper front face, ±0.25 from center | dark glossy slots, slightly proud of the face |
| Arms | 2 | 0.30 × 0.10 × 0.12 | out of the sides, just below mid-height | stubby bars angled 18° up and out |
| Legs | 4 | 0.12 × 0.33 × 0.12 | front pair wide (±0.34), back pair narrow (±0.12) | short and square |
| Mouth | 0 | — | — | never add one |

**Motion.** A springy, weighty toy. It squashes to 1.08 × 0.80 before a jump and stretches to 0.95 × 1.08 at take-off, as on the landing. Under load the squash grows and recovery slows.

**Expressions: eyes only.** The slots morph smoothly between states and stay dark and glossy. Emotion only ever declines.

| State | Trigger | Eyes | Body | Flag |
| --- | --- | --- | --- | --- |
| E0 | Assembly | tall slots | springy jump | — |
| E1 | LANDING | upward arcs, smiling | hop, arms up | pops up: I'M OK, waving |
| E2 | BLOG | lower, shorter arcs | small nod | smaller wave |
| E3 | AUTH | flat, slightly shorter slots | still | raised, no wave |
| E4 | DATABASE, face close-up | tops tilt inward (worried), a blue sweat drop | knees bend | droops |
| E5 | SHOP to REFERRALS | squeezed thin, trembling | short wobbly steps | flips to I'M OK? |
| E6 | Snake sway | dizzy spirals | wide zigzag | shakes |
| E7 | Fallen | X X | on its side | flung, lands upright: I'M OK |

**The flag gag.** A tiny white flag on a thin stick, held by the right arm. It never admits a problem: the agent keeps reporting that it is fine. After the fall the flag plants itself upright beside the agent; in S14 every fallen agent has one.

**Voice.** No speech. Tiny servo chirps: a happy two-tone (E1), a descending "uh-oh" (E4), a strained hum (E5–E6), a power-down whine as the eyes go X X (E7).

**Never:** studs, clothes, logos, a mouth, extra limbs, or a change of color or proportions between shots.

**S01 timing, copied from the landing.** Parts fly in from the right, spinning (0.95 s, 70 ms stagger) · callout lines draw and labels type (≈ 1.5 s) · parts snap home with a spring (0.62 s) · clockwise turn to camera (0.78 s) · squat and jump (1.0 s).

## Brick catalogue

Ten feature bricks, each a different toy shape and color, grow bigger and more awkward as they climb. The finished tower stands about 8 agent-heights.

| # | Callout | Label | Color | Shape | W × H (AW × AH) | Seating | Arrives |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | F | LANDING | warm white #F5F1E8 | flat plate with a tiny printed browser window | 1.15 × 0.30 | dead center | cursor, gentle |
| 2 | G | BLOG | teal #14B8A6 | three slightly fanned page plates, printed text lines | 1.00 × 0.50 | centered | cursor |
| 3 | H | AUTH | violet #8B5CF6 | brick with an embossed keyhole | 0.90 × 0.60 | rotated 2° | cursor, tossed |
| 4 | I | DATABASE | silver metallic #A8B3C1 | round stack of three grooved discs | Ø 0.90 × 0.90 | slight overhang | falls from above |
| 5 | J | SHOP | yellow #FACC15 | brick with a red-and-white striped awning | 1.00 × 0.80 | half a stud off-center, visible gap | falls |
| 6 | K | DASHBOARD | graphite #374151, glowing green print | wide slope with mini charts on its face | 1.30 × 0.90 | overhangs both sides | falls |
| 7 | L | ACCOUNT | lime #84CC16 | brick with a tiny door and a person emboss | 0.80 × 0.90 | tilted 4° | falls, faster |
| 8 | M | SUBSCRIPTIONS | magenta #EC4899 | arch, hollow underneath, loop-arrow emboss | 1.10 × 1.10 | held on with grey duct tape | falls, faster |
| 9 | N | REDIS | glossy cherry red #DC2626 | dense cube with a lightning-bolt emboss | 0.75 × 0.75 | pushed to one side | falls, fastest |
| 10 | O | REFERRALS | gold chrome | Y-shaped connector with three ring arms | 1.60 × 1.20 | top-heavy crown | falls, last |

- **Tower height after each brick (AH):** 0.3 · 0.8 · 1.4 · 2.3 · 3.1 · 4.0 · 4.9 · 6.0 · 6.75 · 7.95.
- **Labels:** bold condensed uppercase sans, printed on the front face; white on dark bricks, graphite on light ones. In hero frames the label faces camera.
- **Generic bricks only:** plain studs, no logos. Never write a toy maker's brand name in a prompt or on screen.
- **Silhouettes:** every brick must read by shape and color alone, even without its label.
- **Optional detail (S10):** small unlabeled grey 1×1 shims wedged into gaps, tech debt you can see.

## Physics and animation bible

Every failure must look earned: weight piles up, seating gets sloppier, the base compensates, and the tower breaks at its weakest joint.

- **Scale:** toy-scale physics: light, quick, bouncy plastic. Crisp impacts, no floatiness outside slow motion.
- **Load:** each impact squashes the body more, from 4% for LANDING to 12% for REFERRALS. The legs splay a little further and recover a little slower every time.
- **Seating decay:** bricks 1–3 snap clean; 4 overhangs; 5 lands off-center with a gap; 6 overhangs both sides; 7 tilts; 8 is taped; 9 sits off-axis; 10 is top-heavy.
- **Zigzag:** begins after brick 6 as small corrective steps. The path widens as the tower grows; steps shorten; legs tremble.
- **Snake sway:** the tower is ten weakly joined segments on a moving base. Each segment lags the one below by 3–5 frames, so an S-wave climbs to the top. Amplitude grows with height; the top swings up to 1.5 AW.
- **Joints:** hairline gaps open on the stretched side and close on the compressed side; loose parts rattle.
- **Failure:** at the widest swing, the tape on SUBSCRIPTIONS peels and the tower buckles there. The top four bricks whip over in an arc and separate mid-air; the lower stack collapses sideways a beat later.
- **The agent falls:** its legs give way; it tips forward and lands on its side, face to camera; the eyes switch to X X.
- **Debris:** bricks bounce 2–3 times with damping, small parts skitter, dust puffs off the grid. Everything settles within about 1.5 s of real time.
- **Speed ramp:** 100% → 20% as the tape peels; hold through the fall; back to 100% on the last bounce.
- **HUD physics:** at the moment of failure, panels and callout labels come unpinned and fall off-screen with the same gravity, turning slightly.

## Camera bible

Calm, motion-controlled moves in Acts 0–1; tighter and nervous in Acts 2–3; slow and wide in Act 4. One move per shot.

- **Lenses (full-frame):** 35 mm for wides, 50 mm for mediums, 100 mm macro for the face. f/2.8 look; a tilt-shift miniature feel in S14.
- **Height:** the agent's eye level for most of Acts 1–3, a toy's point of view. Low angles on the tall tower.
- **Moves by act:**
  - Acts 0–1: smooth dolly and slow orbit.
  - Act 2: slow push-in to the face (S07), fast pull-back and crane up (S08), tracking with the zigzag (S09).
  - Act 3: whip pans and micro-shake on impacts (S10), a locked long-lens side profile for the sway (S11), a slow-motion low angle for the fall (S12).
  - Act 4: ground-level macro (S13), one continuous crane up and back (S14), a tilt to top-down (S15).
- **Framing for vertical:** keep the agent inside the central 9:16 zone in every shot; the HUD lives in the outer thirds.
- **Cuts:** never inside a generated shot. All cuts are editorial, on music beats.

## HUD and motion-graphics layer

A glass-panel HUD pops in alternately left and right, grows from calm to chaos with the tower, and finally falls off the screen with it.

**Design system**

- **Panels:** dark glass rgba(14,19,32,0.55), 24 px backdrop blur, 1 px border rgba(226,232,240,0.14), 16 px radius, a small mono header such as `AGENT://SESSION`.
- **Type:** Inter 700–800 for captions, tight tracking; JetBrains Mono for the terminal, callouts and metrics.
- **Callouts:** exactly the landing style. A 1 px #E2E8F0 polyline runs from a 3 px dot on the brick to a label; the label types in with a stepped reveal (letter and NAME bold, 0.12 em tracking; the note below at 78% opacity).
- **Motion:** panels enter from their own edge (40 px slide, fade, blur to sharp, 12 frames, ease-out) and leave in 8 frames. In Act 3, entrances drop to 6 frames with overshoot, and panels jitter.
- **Loaders:** skeleton shimmer lines before any text types in; a thinking spinner in the terminal header while each brick arrives; an `Installing 1,284 packages…` bar under the status card in Act 2.
- **Density:** at most 2 panels in Act 1, 3 in Act 2, no limit in Act 3, none during the fall's silence, one counter in Act 4.
- **Safe zone:** never over the agent's face or the brick in motion.
- **Sound:** each panel gets a soft UI blip, panned to its side.

**Components**

1. **Terminal** (top-left): the prompt log below.
2. **Status card** (top-right): PROMPTS, CONTEXT, STABILITY, BUILD; values in the metrics table.
3. **Dependency graph** (bottom-left, Acts 2–3): one node per brick in its color; edges grow from 2 to about 40 and cross into a hairball.
4. **Toast stack** (bottom-right, Acts 2–3): toasts pile up and tilt like the tower. Merge conflict · auth.ts / Deprecated packages ×3 / Hotfix applied / 112 type errors / Memory leak · /dashboard / Webhook timeout · payments / Rollback failed.
5. **Build bar** (bottom-center): `Building app…` 12% → 47% → 83% → 99%, stuck at 99% and flickering, then `ERROR`.
6. **Height ruler** (right edge): grows with the tower. A red dashed line at 5 AH reads `LIMIT · NO ARCHITECTURE`; crossing it flashes `UNSUPPORTED HEIGHT`.
7. **Brick callouts F–O:** one per brick, alternating sides. From J on, the lines cross; by O they are a tangle.
8. **Captions** (center, lower third): 72–96 px at 1080p. Words drop in one by one like bricks, with a small bounce. Act 3 captions stack misaligned and wobble.
9. **Alert:** `FATAL: STACK OVERFLOW`, a red panel that slams to center with RGB split and 2 frames of datamosh.
10. **Glitch:** 2–8 px RGB split and scanline shifts for 2–4 frames on every Act 3 impact; a red vignette pulse while stability is under 30%.
11. **Counter** (top-right, Act 4): `24 AGENTS · 24 TOWERS · 0 BLUEPRINTS`, typed.

**Terminal log** (one exchange per brick; the user's prompt, then the agent's reply)

```text
> make me a landing page
✓ live · 58 s
> add a blog
✓ done
> add sign-up and login
✓ done
> connect a database
✓ done · 2 warnings
> add a shop with payments
⚠ done · 9 warnings
> admin dashboard, quick
⚠ patched · 3 tests skipped
> user accounts with roles
⚠ refactoring 41 files…
> subscriptions. today.
✗ 27 tests failing
> it's slow. add redis
✗ circular dependency: auth ↔ shop
> referral program, ship tonight
✗ FATAL: stack overflow
```

**Metrics after each brick**

| After | Prompts | Context | Stability | Build |
| --- | --- | --- | --- | --- |
| LANDING | 1 | 6% | 100% | PASSING |
| BLOG | 2 | 11% | 98% | PASSING |
| AUTH | 5 | 19% | 95% | PASSING |
| DATABASE | 9 | 34% | 86% | PASSING |
| SHOP | 17 | 48% | 74% | WARNINGS |
| DASHBOARD | 30 | 61% | 61% | WARNINGS |
| ACCOUNT | 52 | 72% | 41% | WARNINGS |
| SUBSCRIPTIONS | 88 | 85% | 21% | FAILING |
| REDIS | 140 | 100% | 12% | FAILING |
| REFERRALS | 230 | OVERFLOW | 3% → 0% | FAILING |

**HUD timeline**

| Time | Side | Event |
| --- | --- | --- |
| 0:01–0:05 | right | Intro callouts A, C, E, B draw and type |
| 0:07 | split | Glowing seam; `01 · STACK IT` left; `02 · ARCHITECT IT` right, dim, with a loading ring and a lock |
| 0:11 | left | Terminal opens with a spinner: make me a landing page → ✓ live · 58 s |
| 0:12.5 | right | Callout F; caption "One prompt. A website." |
| 0:17 | left | Callout G; terminal: add a blog ✓; caption "Another prompt. A blog." |
| 0:18 | right | Status card enters |
| 0:22 | right | Callout H; caption "So far, so easy." |
| 0:26 | left | Callout I; terminal: connect a database ✓ · 2 warnings |
| 0:29 | right | First toast; CONTEXT 34%; caption "But every feature has weight." |
| 0:33.5 | right | Callout J; BUILD turns WARNINGS |
| 0:34.5 | left | Callout K (first crossing line); dependency graph enters; caption "And weight needs structure." |
| 0:36 | right | Packages bar; toasts 2–3 |
| 0:38 | right | Height ruler appears with the LIMIT line above the tower |
| 0:42.8 | right | Callout L |
| 0:43 | center | Caption "More. Faster. Just one more."; the terminal scrolls fast |
| 0:44.6 | left | Callout M; the tower crosses LIMIT → `UNSUPPORTED HEIGHT`; red vignette |
| 0:46.2 | right | Callout N; CONTEXT 100% |
| 0:47.6 | left | Callout O; CONTEXT OVERFLOW; build bar stuck at 99% |
| 0:50 | center | Caption "Nobody drew the plan."; every panel wobbles with the sway |
| 0:56.5 | all | Panels and labels fall off-screen |
| 0:58 | center | `FATAL: STACK OVERFLOW`; glitch; then a clean, silent frame |
| 1:06 | top-right | Counter types |
| 1:09 | center | "Small builds stand. Big ones need a plan." |
| 1:15 | center | "It was never the agent." |
| 1:17.5 | center | "It was the missing architecture." |
| 1:20 | split | The right half returns: `02 · ARCHITECT IT — next`; black at 1:22 |

## Shot list and prompts

Fifteen shots, 82 s in total. Each prompt below is the shot-specific part; wrap it in the global blocks from section 12 as each shot's Blocks line says.

**Beat sheet**

| Shot | In | Brick (callout) | Tower (AH) | Eyes | Flag |
| --- | --- | --- | --- | --- | --- |
| S01 | 0:00 | — | 0 | E0 | — |
| S02 | 0:06 | — | 0 | E0 | — |
| S03 | 0:10 | LANDING (F) | 0.3 | E1 smiling | I'M OK, waving |
| S04 | 0:16 | BLOG (G) | 0.8 | E2 | smaller wave |
| S05 | 0:21 | AUTH (H) | 1.4 | E3 flat | still |
| S06 | 0:25 | DATABASE (I) | 2.3 | E3 → E4 | droops |
| S07 | 0:28 | — (face) | 2.3 | E4 worried, sweat | — |
| S08 | 0:33 | SHOP (J), DASHBOARD (K) | 4.0 | E4 → E5 | droops |
| S09 | 0:37 | — (zigzag) | 4.0 | E5 squeezed | I'M OK? |
| S10 | 0:42 | ACCOUNT (L), SUBSCRIPTIONS (M), REDIS (N), REFERRALS (O) | 7.95 | E5 | shakes |
| S11 | 0:49 | — (sway) | 7.95 | E6 spirals | shakes |
| S12 | 0:55 | — (fall) | 7.95 → 0 | E7 X X | flung |
| S13 | 1:00 | — | 0 | E7 | I'M OK, planted |
| S14 | 1:04 | the crowd | — | mixed | a field of flags |
| S15 | 1:14 | — | — | — | — |

### S01 · Assembly · 0:00–0:06 (6 s)

- **We see:** the landing's blueprint scene. Flat hatched coral parts on the navy grid.
- **Action:** parts fly in from the right, spinning; they hang apart while callouts A, C, E, B draw; they snap together; the figure turns clockwise to camera, squats and jumps.
- **Camera:** locked, slight perspective, as on the landing.
- **Sound:** whooshes, typing ticks, clicks as parts join, a soft spring on the jump.
- **Best source:** render the landing component with Remotion. Use the prompt only as a fallback.
- **Blocks:** STYLE, AGENT, NEGATIVE (drop "no flat 2D look").

```text
Flat technical-illustration look, no realistic lighting yet. The coral parts of the hero fly in from the right edge of frame, spinning: the wide body, two dark eye slots, two stub arms, four stub legs. They stop slightly apart in an exploded view. Thin light-grey lines with small dots draw out from the body, arms and legs to empty space on the right. The parts snap together with a springy overshoot. Seen from three-quarter right, the figure turns clockwise to face the camera, squats and makes one springy jump; its hatched shadow on the grid shrinks and grows. Locked camera. 6 seconds.
```

### S02 · Materialization and split · 0:06–0:10 (4 s)

- **Action:** at the top of the jump the drawing becomes a physical toy and lands on a real floor.
- **Post:** at 0:07 a glowing vertical seam splits the frame. Left: this plate, warm, `01 · STACK IT`. Right: the blue plate, `02 · ARCHITECT IT`, with a loading ring and a lock. At 0:09 the camera pushes into the left half and the seam slides off the right edge.
- **Sound:** a soft shimmer at the change, a glassy slide for the seam.
- **Blocks:** STYLE, AGENT, NEGATIVE (drop "no flat 2D look").

```text
Starts on the hero at the top of its jump, still in a flat illustration look. In mid-air the figure becomes a real physical object: matte coral plastic, embossed hatching, soft top light, real shadows and depth of field; the grid floor gains a faint sheen and haze. It lands with squash and stretch. The camera slowly dollies back to a medium-wide shot, figure centered. 4 seconds.
```

Right-half plate (also reused in S15):

```text
The hero stands still and centered on the dark grid stage, lit in cool blue (#2563EB), seen through frosted glass, with a gentle idle breathing motion. No bricks. Locked camera. 4 seconds.
```

### S03 · LANDING · 0:10–0:16 (6 s)

- **Action:** the user's cursor sets the first brick down; the agent is delighted.
- **Agent:** E1. Hop, arms up, the flag pops up.
- **HUD:** terminal opens (left), callout F (right), caption "One prompt. A website."
- **Sound:** soft UI whoosh, a crisp snap, a happy two-tone chirp, marimba enters.
- **Blocks:** STYLE, AGENT, BRICKS (LANDING), NEGATIVE.

```text
Medium shot at the figure's eye level, warm soft light from top-left. A large glossy white 3D UI cursor shaped like a grab-hand icon descends from above, carrying a flat warm-white toy brick plate with plain studs and the printed word LANDING. It lowers the plate onto the flat top of the coral figure and lets go: a crisp snap, a tiny bounce, a puff of glowing dust. The figure's dark slot eyes curve into happy upward arcs, it hops once, and a tiny white flag on a thin stick pops up in its right arm, reading I'M OK, waving cheerfully. The cursor rises out of frame. Slow push-in. 6 seconds.
```

### S04 · BLOG · 0:16–0:21 (5 s)

- **Agent:** E2. Still happy, a little less.
- **HUD:** callout G (left), terminal line, status card enters (right), caption "Another prompt. A blog."
- **Sound:** snap, a smaller chirp.
- **Blocks:** STYLE, AGENT, BRICKS (LANDING, BLOG), NEGATIVE.

```text
Same setup and light. The white grab-cursor returns from above carrying a teal toy brick made of three slightly fanned thin plates with printed text lines and the word BLOG. It sets it on top of the LANDING plate: snap. The figure is still happy, but its eye arcs are lower and shorter, and its flag waves smaller. Gentle 10-degree orbit to the right. 5 seconds.
```

### S05 · AUTH · 0:21–0:25 (4 s)

- **Agent:** E3. Eyes flat; the flag stops waving.
- **HUD:** callout H (right), caption "So far, so easy."
- **Sound:** a quicker whoosh, a snap, music adds a bass note.
- **Blocks:** STYLE, AGENT, BRICKS (LANDING, BLOG, AUTH), NEGATIVE.

```text
Same setup, a little faster. The cursor swoops in and tosses a violet brick with an embossed keyhole and the word AUTH onto the stack; it lands rotated two degrees. The figure's eyes become flat, slightly shorter slots; it holds the flag still. The cursor leaves quickly. Camera holds the medium shot. 4 seconds.
```

### S06 · DATABASE · 0:25–0:28 (3 s)

- **Change:** no cursor any more; from here bricks fall from the sky.
- **Agent:** E3 → E4. Knees bend; the flag droops.
- **HUD:** callout I (left), terminal: 2 warnings.
- **Sound:** a falling whistle, a heavy plastic thud, light cools.
- **Blocks:** STYLE, AGENT, BRICKS (LANDING, BLOG, AUTH, DATABASE), NEGATIVE.

```text
Medium-wide low angle, light turning cooler. A heavy silver metallic round brick, a stack of three grooved discs with the word DATABASE, drops fast from above out of a thin streak of light and slams onto the stack. The figure's body squashes, its four legs bend outward, and a ring of dust bursts across the grid floor. Camera shake on impact. 3 seconds.
```

### S07 · The face · 0:28–0:33 (5 s)

- **Agent:** E4. Worried tilt, a sweat drop.
- **HUD:** one toast, CONTEXT 34%, caption "But every feature has weight."
- **Sound:** music drops to low heartbeat thumps; a descending "uh-oh" chirp.
- **Blocks:** STYLE, AGENT, NEGATIVE.

```text
Slow push-in to an extreme close-up of the figure's face: the coral front with its two glossy dark slot eyes. Reflected in the eyes, more colored bricks approach from above. A small glossy blue drop of sweat slides down the coral face. The eye slots tilt inward at the top, worried. Very shallow depth of field; rack focus from the eyes to the reflection and back. 5 seconds.
```

### S08 · SHOP and DASHBOARD · 0:33–0:37 (4 s)

- **Agent:** E4 → E5.
- **HUD:** callouts J (right) and K (left), the first crossing line; dependency graph; BUILD turns WARNINGS; caption "And weight needs structure."
- **Sound:** two whistles, two impacts, hi-hats join.
- **Blocks:** STYLE, AGENT, BRICKS (LANDING to DASHBOARD), NEGATIVE.

```text
Fast pull-back and crane up from the face to a wide shot of the four-brick stack on the figure's back. From the dark sky, a yellow brick with a red-and-white striped awning (SHOP) and a wide graphite slope brick with glowing green mini charts (DASHBOARD) hurtle down with motion trails and slam onto the stack one after the other. SHOP lands half a stud off-center with a visible gap; DASHBOARD overhangs both sides. Camera shake on each impact, haze in the air. 4 seconds.
```

### S09 · The zigzag begins · 0:37–0:42 (5 s)

- **Agent:** E5. Squeezed, trembling eyes; the flag now reads I'M OK?
- **HUD:** packages bar, toasts stacking (right), height ruler with the LIMIT line.
- **Sound:** creaks, faster pulse, tempo creeps up.
- **Blocks:** STYLE, AGENT, BRICKS (LANDING to DASHBOARD), NEGATIVE.

```text
Wide shot at eye level, cooler light. The figure starts walking to keep its balance under the six-brick tower: small steps left, then right, in a widening zigzag across the grid. The tower leans and the figure overcorrects. Its eyes are squeezed into thin trembling slits. The tiny white flag in its arm now reads I'M OK? Camera tracks sideways with the figure. 5 seconds.
```

### S10 · Overload · 0:42–0:49 (7 s, two generations)

- **Impacts:** ACCOUNT 0:42.8 · SUBSCRIPTIONS 0:44.6 · REDIS 0:46.2 · REFERRALS 0:47.6. Each interval shorter than the last.
- **Agent:** E5. Legs trembling, still zigzagging.
- **HUD:** chaos. Callouts L–O tangle; CONTEXT hits OVERFLOW; build bar stuck at 99%; `UNSUPPORTED HEIGHT`; caption "More. Faster. Just one more."
- **Sound:** 140 BPM, four whistles and impacts, glitch zaps, alarm beeps.
- **Blocks:** STYLE, AGENT, BRICKS (all ten), NEGATIVE.

S10a (ACCOUNT, SUBSCRIPTIONS):

```text
Continuous shot with fast whip pans up to the dark sky and back down. Two more bricks plunge from above and slam onto the leaning tower on the coral figure's back: a lime brick with a tiny door (ACCOUNT), then a magenta arch brick with a loop-arrow emboss (SUBSCRIPTIONS), strapped on with a strip of grey duct tape. Red warning light pulses from the left, a white flash on each impact, dense haze. The figure keeps zigzagging, legs trembling. 3.5 seconds.
```

S10b (REDIS, REFERRALS), first frame = last frame of S10a:

```text
The same continuous shot, faster. A glossy cherry-red cube with a lightning bolt (REDIS) plunges down and slams onto the tower, then a wide gold-chrome Y-shaped connector with three ring arms (REFERRALS) crowns the top. The tower now stands about eight times the figure's height and leans visibly. Red pulses, white flashes, dust in the haze. Camera ends on a low-angle wide shot of the whole tower. 3.5 seconds.
```

### S11 · The snake sway · 0:49–0:55 (6 s)

- **Agent:** E6. Dizzy spirals, wide zigzag.
- **HUD:** every panel wobbles in sync with the tower; STABILITY 12% → 3%; caption "Nobody drew the plan."
- **Sound:** plastic creaking and ticking joints, a string riser, the alarm.
- **Blocks:** STYLE, AGENT, BRICKS (all ten), NEGATIVE.

```text
Locked wide side-profile shot with a long lens, the whole tower in frame, low-key cold cyan light with a pulsing red rim light. As the coral figure zigzags left and right at the base, the tall stack of ten colored bricks sways like a snake: an S-shaped wave travels from the base to the top, upper bricks lagging behind, joints opening hairline gaps and closing again, the gold piece at the top whipping wide. The figure's eyes turn into dizzy spirals. 6 seconds.
```

### S12 · The fall · 0:55–1:00 (5 s)

- **Agent:** E7. On its side, X X eyes.
- **HUD:** at 0:56.5 every panel falls off-screen; at 0:58 `FATAL: STACK OVERFLOW` slams in; then a clean, silent frame.
- **Sound:** a tape rip, slowed debris, a power-down whine, then total silence for 0.5 s, then a sub boom.
- **Blocks:** STYLE, AGENT, BRICKS (all ten), NEGATIVE.

```text
Super slow motion, low angle. At the widest swing the grey tape peels off the magenta arch brick and the tower buckles there: the top four bricks whip over in a long arc and separate in mid-air, spinning and catching the light; the lower bricks collapse sideways a beat later. The coral figure's legs give way; it tips forward and lands on its side facing the camera, its eye slots turning into X X. Bricks bounce and scatter across the grid; a glossy red cube bounces toward the lens and stops just in front of it. Speed ramps from real time into slow motion and back on the last bounce. 5 seconds.
```

### S13 · The flag · 1:00–1:04 (4 s)

- **Agent:** E7, still.
- **HUD:** none.
- **Sound:** settling dust, one soft felt-piano note.
- **Blocks:** STYLE, AGENT, BRICKS (scattered), NEGATIVE.

```text
Ground-level macro, quiet, soft moonlit blue light, dust settling. The tiny white flag on its thin stick flutters down from above in slow motion and plants itself upright in a gap of the grid floor, right beside the fallen coral figure, which lies on its side with X-shaped eyes among scattered colored bricks. The flag reads I'M OK. Gentle focus pull from the flag to the figure's face. 4 seconds.
```

### S14 · The field · 1:04–1:14 (10 s, two generations)

- **Crowd (24):** 13 fallen, each with its planted flag; 5 still staggering under tall towers, 3 of which topple during the shot (near, middle, far); 3 standing tall and swaying; 3 small builds with one or two bricks, upright, happy, waving.
- **HUD:** counter `24 AGENTS · 24 TOWERS · 0 BLUEPRINTS` at 1:06; caption "Small builds stand. Big ones need a plan." at 1:09.
- **Sound:** piano, three distant collapses, faint air.
- **Blocks:** STYLE, AGENT, BRICKS (mixed), NEGATIVE.

S14a, first frame = last frame of S13:

```text
One continuous crane move: the camera rises up and back from the fallen coral figure, revealing more identical coral box figures around it on the dark navy grid stage. Most lie fallen on their sides among scattered colorful bricks, each with a tiny white flag planted beside it. Nearby, one figure staggers under a tall swaying tower, which topples during the shot. Moonlit blue light, warm rim light on drifting dust. 5 seconds.
```

S14b, first frame = last frame of S14a:

```text
The crane keeps rising and pulling back, revealing a vast stage with at least twenty identical coral box figures, each with its own tower attempt. Most are fallen beside their flags. Several still stagger under tall swaying towers; two of them topple one after the other, in the middle distance and far away. Three figures carrying only one or two bricks stand upright with happy eyes, waving their flags. Depth fog, tilt-shift miniature look. 5 seconds.
```

### S15 · The lesson and the hook · 1:14–1:22 (8 s)

- **HUD:** "It was never the agent." at 1:15; "It was the missing architecture." at 1:17.5.
- **Post:** at 1:20 the seam returns from the right edge. The right half shows the blue plate from S02, now with thin blue lines drawing a clean frame and grid around the standing figure. Label `02 · ARCHITECT IT — next`. Cut to black at 1:22.
- **Sound:** the piano resolves; a soft low pad swells with the blue glow; one last note on the black.
- **Blocks:** STYLE, BRICKS (scattered), NEGATIVE.

```text
The camera keeps rising and tilts into a straight top-down view over the field of fallen towers, scattered bricks radiating like spilled matchsticks around the small coral figures. Hold. The thin grid lines of the floor brighten in a soft blue (#2563EB) wave that spreads from the center outward, forming a calm, orderly pattern beneath the chaos for one beat, then dim. 8 seconds.
```

## Sound and music

The music mirrors the tower: playful and sparse, then faster and denser, then silent at the fall, then a lone piano.

| Time | Act | Music |
| --- | --- | --- |
| 0:00–0:10 | Origin | soft glassy plucks and a rising shimmer; one bass hit on the jump |
| 0:10–0:25 | Easy | playful marimba and pizzicato at 108 BPM, light claps |
| 0:25–0:42 | Weight | bass and hi-hats join; a minor turn; tempo creeps to 120 BPM |
| 0:42–0:55 | Overload | accelerates to 140 BPM; stuttering synths, a dissonant string riser, ticking |
| 0:55–1:00 | Fall | hard cut to silence, then a sub boom; slowed debris, a distant ring |
| 1:00–1:14 | Aftermath | solo felt piano, sparse, warm reverb |
| 1:14–1:22 | Lesson | the piano resolves; a low pad swells with the blue glow; one last note on the black |

**Sound effects**

- **Assembly:** whooshes for flying parts, small clicks as they join, a subtle spring on the jump; a shimmer at materialization; a glassy slide for the split.
- **Bricks:** a soft UI whoosh for the cursor; a crisp snap for each placement, its pitch lowering as bricks get heavier; a falling whistle and a plastic thud for sky drops.
- **Agent:** servo chirps only: happy two-tone (S03), descending "uh-oh" (S07), strained hum (S09–S11), power-down whine at the fall (S12).
- **Structure:** plastic creaks, ticking joints, a tape rip, layered plastic clatter, tiny skitters.
- **HUD:** soft blips panned to each panel's side; typing ticks; a 1 Hz alarm beep in Act 3; glitch zaps.
- **Air:** low room tone; faint wind in Act 4.

**Mix rules:** no dialogue. Music ducks under impacts. The silence at 0:58 is truly silent for about 0.5 s before the boom. Web master at −14 LUFS.

## Global prompt blocks

Paste these blocks into every generation, in this order, so the hero, the bricks and the look stay identical across all 15 shots.

**STYLE**

```text
Premium 3D animated film, physically based rendering, toy-scale macro photography, shallow depth of field, 24 fps cinematic motion blur, light film grain. Setting: an endless dark navy stage (#0E1320) whose floor is a thin slate-grey square grid fading into black with distance, soft volumetric haze, floating dust motes. Clean, minimal, high-end tech commercial look.
```

**AGENT**

```text
The hero is a small toy robot made of simple blocks. Body: one wide, low, coral-orange box (width 1, height 0.62, depth 0.57), matte plastic, front #D9694F, top lighter #E98A70, sides darker #B9533C, a fine diagonal hatch texture embossed on every face, thin light-grey edge lines. Face: two dark glossy vertical slot eyes (#0B0F17) in the upper half of the front face, set wide apart. No mouth, no nose. Arms: two short stubby rectangular bars sticking out of the body's sides, angled up and outward. Legs: four short square stubby legs under the body, front pair wide, back pair narrow. Flat top, no studs, no logo, no clothes. Exactly 2 eyes, 2 arms, 4 legs. Same proportions and color in every frame.
```

**BRICKS** (keep only the lines for bricks in frame)

```text
Generic interlocking toy construction bricks, glossy injection-molded plastic, plain studs without logos, a bold uppercase label printed on the front face:
LANDING: warm-white flat plate with a tiny printed browser window.
BLOG: teal, three slightly fanned thin plates with printed text lines.
AUTH: violet brick with an embossed keyhole.
DATABASE: silver metallic round stack of three grooved discs.
SHOP: yellow brick with a small red-and-white striped awning.
DASHBOARD: wide graphite slope brick with glowing green mini charts.
ACCOUNT: lime brick with a tiny door and a person emboss.
SUBSCRIPTIONS: magenta arch brick with a loop-arrow emboss, strapped with grey duct tape.
REDIS: glossy cherry-red cube with a lightning-bolt emboss.
REFERRALS: gold-chrome Y-shaped connector with three ring arms.
```

**NEGATIVE**

```text
no brand logos or toy-maker marks, no logos on studs, no humans, no realistic human hands, no mouth on the robot, no extra or missing limbs, no studs on the robot, no text except the specified labels, no subtitles, no watermark, no cartoon outlines, no cel shading, no flat 2D look, no morphing or melting shapes, no proportion changes, no cuts within the shot, no fire, no explosions, no gore
```

For S01 and S02, drop "no flat 2D look" from NEGATIVE.

## Deliverables and QA

Deliver a 4K master with separate clean plates and HUD layers, and pass the checklist below before release.

| Item | Spec |
| --- | --- |
| Master | 3840×2160, 24 fps, 82 s, ProRes 422 HQ plus H.265 |
| Vertical cut | 1080×1920 from the same plates; HUD reflowed to top and bottom |
| Clean plates | every shot without overlays, ProRes 4444 |
| HUD and captions | a separate layer with alpha |
| Audio | music, SFX and mix stems; web master at −14 LUFS |
| References | agent turnaround and expression sheet, brick sheet, first/last keyframes per shot |

**QA checklist**

- [ ] The agent is identical in every shot: coral box, 2 slot eyes, no mouth, 2 stub arms, 4 stub legs.
- [ ] Brick order is exact: LANDING, BLOG, AUTH, DATABASE, SHOP, DASHBOARD, ACCOUNT, SUBSCRIPTIONS, REDIS, REFERRALS; colors never drift.
- [ ] Emotion only declines, E1 to E7, never back.
- [ ] Push-in after brick 4, zigzag from brick 6, fall after brick 10.
- [ ] At least 20 agents are visible in S14, and the small builds are standing.
- [ ] Every caption stays at least 2 s (Act 3 excepted); the HUD never covers the face or the brick in motion.
- [ ] Labels and the flag are readable; anything smeared is replaced in post.
- [ ] The 0.5 s silence before the boom is there.
- [ ] No toy-maker or other third-party marks on screen.
- [ ] Before publishing, the use of the Claude figure and the Claude Code name is checked against Anthropic's brand guidelines.
