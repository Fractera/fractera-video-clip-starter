// Fractera Lego Motion — engine + test 01 (S01–S03: assembly → materialization → LANDING).
// Everything is a pure function of time t (seconds): window.renderAt(t) draws one frame.
import * as THREE from 'three';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js';

try {
const W = 1920, H = 1080, FEET = -1.35, D2R = Math.PI / 180;

// ───────────────────────── math & easing (landing curves kept 1:1)
const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const lerp = (a, b, k) => a + (b - a) * k;
const prog = (t, a, b) => clamp((t - a) / (b - a));
function bezier(x1, y1, x2, y2) {
  const cx = 3 * x1, bx = 3 * (x2 - x1) - cx, ax = 1 - cx - bx;
  const cy = 3 * y1, by = 3 * (y2 - y1) - cy, ay = 1 - cy - by;
  const sx = u => ((ax * u + bx) * u + cx) * u, sy = u => ((ay * u + by) * u + cy) * u, dx = u => (3 * ax * u + 2 * bx) * u + cx;
  return x => {
    if (x <= 0) return 0; if (x >= 1) return 1;
    let lo = 0, hi = 1, u = x;
    for (let i = 0; i < 40; i++) { const v = sx(u); if (Math.abs(v - x) < 1e-6) break; if (v < x) lo = u; else hi = u; u = (lo + hi) / 2; }
    return sy(u);
  };
}
const ease = {
  flyIn: bezier(.16, 1, .3, 1), spring: bezier(.34, 1.56, .64, 1), turn: bezier(.65, 0, .35, 1), line: bezier(.22, 1, .36, 1),
  out3: x => 1 - (1 - x) ** 3, in2: x => x * x, in3: x => x ** 3, io: x => (1 - Math.cos(Math.PI * x)) / 2,
  back: x => { const c1 = 1.70158, c3 = c1 + 1; return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2; },
};
const bell = x => Math.sin(Math.PI * clamp(x));
function rng(seed) { let a = seed >>> 0; return () => { a = (a + 0x6D2B79F5) >>> 0; let t = Math.imul(a ^ (a >>> 15), 1 | a); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; }

// ───────────────────────── fonts first (canvas labels need them)
await Promise.all([
  document.fonts.load('800 150px Inter'), document.fonts.load('600 40px Inter'),
  document.fonts.load('700 27px "JetBrains Mono"'), document.fonts.load('400 22px "JetBrains Mono"'),
]);
await document.fonts.ready;

// ───────────────────────── renderer, scene, post
const renderer = new THREE.WebGLRenderer({ antialias: false, preserveDrawingBuffer: true, powerPreference: 'high-performance' });
renderer.setPixelRatio(1); renderer.setSize(W, H);
renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFShadowMap;
renderer.toneMapping = THREE.NeutralToneMapping; renderer.toneMappingExposure = 1.0;
document.getElementById('stage').appendChild(renderer.domElement);

const scene = new THREE.Scene();
const BG = new THREE.Color('#0e1320');
scene.background = BG;
const pmrem = new THREE.PMREMGenerator(renderer);
scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;
scene.environmentIntensity = 0;

const camera = new THREE.PerspectiveCamera(30, W / H, 0.1, 200);
const rt = new THREE.WebGLRenderTarget(W, H, { type: THREE.HalfFloatType, samples: 4 });
const composer = new EffectComposer(renderer, rt);
composer.setPixelRatio(1); composer.setSize(W, H);
composer.addPass(new RenderPass(scene, camera));
const bloom = new UnrealBloomPass(new THREE.Vector2(W / 2, H / 2), 0.0, 0.42, 1.1);
composer.addPass(bloom);
composer.addPass(new OutputPass());

// ───────────────────────── textures
function canvasTex(w, h, draw, srgb = true) {
  const c = document.createElement('canvas'); c.width = w; c.height = h;
  const g = c.getContext('2d'); draw(g, w, h);
  const t = new THREE.CanvasTexture(c); if (srgb) t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8; return t;
}
// The landing's hatch: repeating-linear-gradient(135deg, white 8% 1.5px / 6px) → "/" stripes every 0.0625 units.
function hatchTex(hex, alpha, fw, fh) {
  const t = canvasTex(256, 256, (g, w, h) => {
    g.fillStyle = hex; g.fillRect(0, 0, w, h);
    g.strokeStyle = `rgba(255,255,255,${alpha})`; g.lineWidth = 4;
    for (let i = -w; i < 2 * w; i += 16) { g.beginPath(); g.moveTo(i, 0); g.lineTo(i - h, h); g.stroke(); }
  });
  t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(fw, fh); return t;
}
const dotTex = canvasTex(64, 64, (g, w) => {
  const r = g.createRadialGradient(w / 2, w / 2, 0, w / 2, w / 2, w / 2);
  r.addColorStop(0, 'rgba(255,255,255,1)'); r.addColorStop(0.35, 'rgba(255,255,255,.55)'); r.addColorStop(1, 'rgba(255,255,255,0)');
  g.fillStyle = r; g.fillRect(0, 0, w, w);
}, false);

// ───────────────────────── palette (Fractera Lego Motion tokens)
const CORAL = { front: '#d9694f', back: '#c25a43', side: '#b9533c', top: '#e98a70', bottom: '#8f3f2e' };
const DARK = { front: '#0b0f17', back: '#0b0f17', side: '#111827', top: '#1e293b', bottom: '#0b0f17' };

// ───────────────────────── the agent (geometry from figure-parts.tsx, px/100, y up)
const figMats = [];
const edgeMat = new THREE.LineBasicMaterial({ color: '#e2e8f0', transparent: true, opacity: 0.6 });
function faceMat(hex, fw, fh, dark) {
  const map = hatchTex(hex, dark ? 0.05 : 0.11, fw, fh);
  const m = new THREE.MeshStandardMaterial({ map, emissive: 0xffffff, emissiveMap: map, emissiveIntensity: 1,
    roughness: dark ? 0.2 : 0.6, metalness: 0, bumpMap: map, bumpScale: 0 });
  figMats.push(m); return m;
}
function cuboid([w, h, d], dark) {
  const c = dark ? DARK : CORAL;
  const geo = new THREE.BoxGeometry(w, h, d);
  const mats = [faceMat(c.side, d, h, dark), faceMat(c.side, d, h, dark), faceMat(c.top, w, d, dark),
                faceMat(c.bottom, w, d, dark), faceMat(c.front, w, h, dark), faceMat(c.back, w, h, dark)];
  const mesh = new THREE.Mesh(geo, mats); mesh.castShadow = true; mesh.receiveShadow = true;
  mesh.add(new THREE.LineSegments(new THREE.EdgesGeometry(geo), edgeMat));
  return mesh;
}
const PARTS = [
  { id: 'body',  size: [2.1, 1.3, 1.2],    pos: [0, 0, 0],            explode: [0, 0.06, 0],        from: [7.2, 1.9, 0],    spin: [50, 70] },
  { id: 'eyeL',  size: [0.26, 0.46, 0.08], pos: [-0.52, 0.14, 0.63],  explode: [-0.14, 0.46, 0.96], from: [4.6, 4.2, 0],    spin: [-80, 40], dark: true },
  { id: 'eyeR',  size: [0.26, 0.46, 0.08], pos: [0.52, 0.14, 0.63],   explode: [0.14, 0.46, 0.96],  from: [6.8, 3.2, 0],    spin: [-60, 70], dark: true },
  { id: 'armL',  size: [0.62, 0.22, 0.26], pos: [-1.36, -0.14, 0],    explode: [-0.54, 0.14, 0],    from: [8.2, -0.5, 0],   spin: [0, -120], rotZ: -18 },
  { id: 'armR',  size: [0.62, 0.22, 0.26], pos: [1.36, -0.14, 0],     explode: [0.54, 0.14, 0],     from: [8.4, -0.3, 0],   spin: [0, -120], rotZ: 18 },
  { id: 'legBL', size: [0.26, 0.7, 0.26],  pos: [-0.26, -1.0, -0.38], explode: [-0.18, 0.05, -0.2], from: [6.4, 0.9, 0.6],  spin: [90, 0] },
  { id: 'legBR', size: [0.26, 0.7, 0.26],  pos: [0.26, -1.0, -0.38],  explode: [0.18, 0.05, -0.2],  from: [6.8, 0.7, 0.4],  spin: [90, 0] },
  { id: 'legFL', size: [0.26, 0.7, 0.26],  pos: [-0.72, -1.0, 0.38],  explode: [-0.18, 0.05, 0.2],  from: [5.9, 1.1, 1.0],  spin: [100, 0] },
  { id: 'legFR', size: [0.26, 0.7, 0.26],  pos: [0.72, -1.0, 0.38],   explode: [0.18, 0.05, 0.2],   from: [6.2, 0.8, 1.2],  spin: [100, 0] },
];
const fig = new THREE.Group(); scene.add(fig);
const turn = new THREE.Group(); fig.add(turn);
const bounce = new THREE.Group(); bounce.position.y = FEET; turn.add(bounce); // scale origin = feet
const parts = {};
PARTS.forEach((p, i) => {
  const wrap = new THREE.Group(); wrap.position.set(p.pos[0], p.pos[1] - FEET, p.pos[2]); wrap.rotation.z = (p.rotZ || 0) * D2R;
  const inner = new THREE.Group(); wrap.add(inner);
  const mesh = cuboid(p.size, p.dark); inner.add(mesh);
  bounce.add(wrap); parts[p.id] = { ...p, i, wrap, inner, mesh };
});
// Happy eyes: ∩ arcs that replace the slots.
const eyeDark = new THREE.MeshStandardMaterial({ color: '#0b0f17', roughness: 0.22, metalness: 0, emissive: '#0b0f17', emissiveIntensity: 1 });
figMats.push(eyeDark);
function arcGeo() {
  const s = new THREE.Shape(); s.absarc(0, 0, 0.17, 0, Math.PI, false); s.absarc(0, 0, 0.085, Math.PI, 0, true); s.closePath();
  const g = new THREE.ExtrudeGeometry(s, { depth: 0.08, bevelEnabled: false, curveSegments: 24 }); g.translate(0, -0.06, -0.04); return g;
}
const arcs = ['eyeL', 'eyeR'].map(id => { const m = new THREE.Mesh(arcGeo(), eyeDark); m.scale.setScalar(0.001); m.castShadow = true; parts[id].inner.add(m); return m; });

// Flag "I'M OK" held by the right arm (pivot at the arm's outer end, in bounce space).
const flagTex = canvasTex(620, 380, (g, w, h) => {
  g.fillStyle = '#e9edf2'; g.fillRect(0, 0, w, h);
  g.strokeStyle = 'rgba(15,23,42,.18)'; g.lineWidth = 8; g.strokeRect(4, 4, w - 8, h - 8);
  g.fillStyle = '#1f2937'; g.font = '800 150px Inter'; g.textAlign = 'center'; g.textBaseline = 'middle'; g.letterSpacing = '4px';
  g.fillText("I'M OK", w / 2 + 2, h / 2 + 10);
});
const flag = new THREE.Group(); flag.position.set(1.64, 1.27 + 0.02, 0.06); flag.scale.setScalar(0.001); bounce.add(flag);
const pole = new THREE.Mesh(new THREE.CylinderGeometry(0.018, 0.018, 0.95, 12).translate(0, 0.475, 0),
  new THREE.MeshStandardMaterial({ color: '#e5e7eb', roughness: 0.35 })); pole.castShadow = true; flag.add(pole);
const clothGeo = new THREE.PlaneGeometry(0.62, 0.38, 28, 10); clothGeo.translate(0.31, 0, 0);
const cloth0 = clothGeo.attributes.position.array.slice();
const cloth = new THREE.Mesh(clothGeo, new THREE.MeshStandardMaterial({ map: flagTex, roughness: 0.75, side: THREE.DoubleSide, emissive: 0xffffff, emissiveMap: flagTex, emissiveIntensity: 0.03 }));
cloth.position.set(0.012, 0.95 - 0.19, 0); cloth.castShadow = true; flag.add(cloth);

// ───────────────────────── stage: blueprint grid floor + shadows
const floorMat = new THREE.ShaderMaterial({
  uniforms: { uBase: { value: BG.clone() }, uLine: { value: new THREE.Color('#94a3b8') }, uAlpha: { value: 0.16 }, uSpacing: { value: 0.4 },
              uFade: { value: 8.5 }, uWarm: { value: 0 }, uGlow: { value: 0 } },
  vertexShader: 'varying vec3 vW; void main(){ vec4 w = modelMatrix * vec4(position,1.0); vW = w.xyz; gl_Position = projectionMatrix * viewMatrix * w; }',
  fragmentShader: `uniform vec3 uBase; uniform vec3 uLine; uniform float uAlpha; uniform float uSpacing; uniform float uFade; uniform float uWarm; uniform float uGlow; varying vec3 vW;
    void main(){ vec2 p = vW.xz / uSpacing; vec2 g = abs(fract(p - 0.5) - 0.5) / fwidth(p); float line = 1.0 - min(min(g.x, g.y), 1.0);
      float d = length(vW.xz); float fade = 1.0 - smoothstep(uFade * 0.25, uFade, d);
      vec3 lc = mix(uLine, vec3(0.95, 0.70, 0.50), uWarm);
      float pool = exp(-d * d / 7.0) * uGlow;  // soft warm light pool under the agent when lit
      vec3 col = uBase + lc * line * uAlpha * fade + vec3(0.050, 0.030, 0.020) * pool;
      gl_FragColor = vec4(col, 1.0); }`,
});
const floor = new THREE.Mesh(new THREE.PlaneGeometry(90, 90), floorMat); floor.rotation.x = -Math.PI / 2; floor.position.y = FEET; scene.add(floor);
const shadowMat = new THREE.ShadowMaterial({ color: 0x000000, opacity: 0 });
const shadowPlane = new THREE.Mesh(new THREE.PlaneGeometry(40, 40), shadowMat); shadowPlane.rotation.x = -Math.PI / 2; shadowPlane.position.y = FEET + 0.002; shadowPlane.receiveShadow = true; scene.add(shadowPlane);
const flatShadowTex = canvasTex(600, 360, (g, w, h) => {
  for (let y = 0; y < h; y += 9) { g.fillStyle = 'rgba(226,232,240,0.34)'; g.fillRect(0, y, w, 2); }
  g.globalCompositeOperation = 'destination-in'; g.save(); g.scale(1, h / w);
  const r = g.createRadialGradient(w / 2, w / 2, 0, w / 2, w / 2, w / 2); r.addColorStop(0, '#000'); r.addColorStop(0.42, '#000'); r.addColorStop(1, 'rgba(0,0,0,0)');
  g.fillStyle = r; g.fillRect(0, 0, w, w); g.restore();
});
const flatShadow = new THREE.Mesh(new THREE.PlaneGeometry(3.0, 1.8), new THREE.MeshBasicMaterial({ map: flatShadowTex, transparent: true, depthWrite: false }));
flatShadow.rotation.x = -Math.PI / 2; flatShadow.position.y = FEET + 0.004; scene.add(flatShadow);

// ───────────────────────── light (off in the blueprint phase, on after materialization)
const key = new THREE.DirectionalLight('#ffd6ae', 0); key.position.set(-4.5, 7.5, 6); key.castShadow = true;
key.shadow.mapSize.set(2048, 2048); Object.assign(key.shadow.camera, { left: -6, right: 6, top: 6, bottom: -6, near: 1, far: 30 });
key.shadow.bias = -0.0004; key.shadow.normalBias = 0.02; key.shadow.radius = 5; key.shadow.blurSamples = 12; scene.add(key, key.target);
const fill = new THREE.HemisphereLight('#9fd3e0', '#0e1320', 0); scene.add(fill);
const rim = new THREE.DirectionalLight('#9cc2ff', 0); rim.position.set(6, 3.5, -6); scene.add(rim);

// ───────────────────────── feature brick: LANDING
function brickMat(hex) { return new THREE.MeshPhysicalMaterial({ color: hex, roughness: 0.3, metalness: 0, clearcoat: 0.6, clearcoatRoughness: 0.22 }); }
function makeBrick({ w, h, d, color, labelTex }) {
  const g = new THREE.Group(); const mat = brickMat(color);
  const body = new THREE.Mesh(new RoundedBoxGeometry(w, h, d, 4, 0.05), mat); body.castShadow = body.receiveShadow = true; g.add(body);
  const nx = Math.round(w / 0.4), nz = Math.round(d / 0.4);
  const studs = new THREE.InstancedMesh(new THREE.CylinderGeometry(0.12, 0.12, 0.1, 28), mat, nx * nz);
  const m4 = new THREE.Matrix4(); let k = 0;
  for (let i = 0; i < nx; i++) for (let j = 0; j < nz; j++) { m4.makeTranslation(-w / 2 + 0.2 + i * 0.4, h / 2 + 0.05, -d / 2 + 0.2 + j * 0.4); studs.setMatrixAt(k++, m4); }
  studs.castShadow = true; g.add(studs);
  if (labelTex) {
    const decal = new THREE.Mesh(new THREE.PlaneGeometry(w * 0.92, h * 0.8),
      new THREE.MeshPhysicalMaterial({ map: labelTex, transparent: true, roughness: 0.3, clearcoat: 0.6, polygonOffset: true, polygonOffsetFactor: -2 }));
    decal.position.set(0, 0, d / 2 + 0.003); g.add(decal);
  }
  return g;
}
const landingTex = canvasTex(1104, 240, (g, w, h) => {
  const x0 = 24, y0 = 34, bw = 236, bh = 172;
  g.strokeStyle = '#1f2937'; g.lineWidth = 11; g.beginPath(); g.roundRect(x0, y0, bw, bh, 20); g.stroke();
  g.fillStyle = '#1f2937'; g.fillRect(x0, y0 + 42, bw, 9);
  [0, 1, 2].forEach(i => { g.beginPath(); g.arc(x0 + 28 + i * 25, y0 + 22, 7.5, 0, Math.PI * 2); g.fill(); });
  g.fillStyle = '#374151'; g.beginPath(); g.roundRect(x0 + 26, y0 + 70, bw - 52, 46, 9); g.fill();
  g.fillStyle = '#9ca3af'; g.beginPath(); g.roundRect(x0 + 26, y0 + 128, bw - 110, 18, 7); g.fill();
  g.font = '800 156px Inter'; g.letterSpacing = '10px'; g.fillStyle = '#1f2937'; g.textBaseline = 'middle'; g.fillText('LANDING', 300, h / 2 + 10);
});
const LANDING = { w: 2.4, h: 0.6, d: 1.2 };
const landing = makeBrick({ ...LANDING, color: '#ebe3d3', labelTex: landingTex });
landing.visible = false; bounce.add(landing);
const LANDING_REST = 1.35 + 0.65 + LANDING.h / 2; // bounce space: feet→body top→half brick

// ───────────────────────── the user's cursor (3D pointer)
function cursorShape() {
  const s = new THREE.Shape(); const P = [[0, 0], [0, -1.0], [0.24, -0.78], [0.40, -1.14], [0.56, -1.07], [0.40, -0.72], [0.70, -0.72]];
  s.moveTo(...P[0]); for (const p of P.slice(1)) s.lineTo(...p); s.closePath(); return s;
}
const cursor = new THREE.Group();
const cWhite = new THREE.Mesh(new THREE.ExtrudeGeometry(cursorShape(), { depth: 0.1, bevelEnabled: true, bevelThickness: 0.03, bevelSize: 0.03, bevelSegments: 3 }),
  new THREE.MeshPhysicalMaterial({ color: '#e8ecf1', roughness: 0.2, clearcoat: 1, clearcoatRoughness: 0.08 }));
const cRim = new THREE.Mesh(new THREE.ExtrudeGeometry(cursorShape(), { depth: 0.06, bevelEnabled: true, bevelThickness: 0.02, bevelSize: 0.08, bevelSegments: 2 }),
  new THREE.MeshStandardMaterial({ color: '#0b0f17', roughness: 0.4 }));
cRim.position.z = -0.05; cWhite.castShadow = true; cursor.add(cRim, cWhite); cursor.scale.setScalar(0.8); cursor.visible = false; scene.add(cursor);

// ───────────────────────── particles: impact dust + ambient motes
function burst(n, seed, color) {
  const r = rng(seed), geo = new THREE.BufferGeometry();
  const pos = new Float32Array(n * 3), col = new Float32Array(n * 3);
  geo.setAttribute('position', new THREE.BufferAttribute(pos, 3)); geo.setAttribute('color', new THREE.BufferAttribute(col, 3));
  const P = Array.from({ length: n }, () => ({ a: r() * Math.PI * 2, v: 0.8 + r() * 1.5, up: 0.15 + r() * 0.7, life: 0.55 + r() * 0.55, j: r() }));
  const mat = new THREE.PointsMaterial({ size: 0.075, map: dotTex, vertexColors: true, transparent: true, depthWrite: false, blending: THREE.AdditiveBlending });
  const pts = new THREE.Points(geo, mat); pts.frustumCulled = false; scene.add(pts);
  const c = new THREE.Color(color);
  return { update(t, t0, cx, cy, cz, rx, rz) {
    const tau = t - t0;
    P.forEach((p, i) => {
      const alive = tau >= 0 && tau < p.life, k = alive ? 1 - tau / p.life : 0, dist = p.v * tau * (1 - 0.45 * tau);
      pos[i * 3] = cx + Math.cos(p.a) * (rx + dist); pos[i * 3 + 1] = cy + p.up * tau - 0.9 * tau * tau + p.j * 0.05; pos[i * 3 + 2] = cz + Math.sin(p.a) * (rz + dist * 0.8);
      const a = alive ? Math.pow(k, 1.6) * 0.9 : 0; col[i * 3] = c.r * a; col[i * 3 + 1] = c.g * a; col[i * 3 + 2] = c.b * a;
    });
    geo.attributes.position.needsUpdate = true; geo.attributes.color.needsUpdate = true;
  } };
}
const dustTop = burst(90, 7, '#ffd9b8');
const dustFloor = burst(70, 11, '#cfe3ff');
const MOTES = 220, mr = rng(3), moteGeo = new THREE.BufferGeometry();
const motePos = new Float32Array(MOTES * 3), moteCol = new Float32Array(MOTES * 3);
const mote0 = Array.from({ length: MOTES }, () => [mr() * 14 - 7, mr() * 5.5 - 1.3, mr() * 8 - 5, mr() * 6.28, 0.3 + mr() * 0.7]);
moteGeo.setAttribute('position', new THREE.BufferAttribute(motePos, 3)); moteGeo.setAttribute('color', new THREE.BufferAttribute(moteCol, 3));
const motes = new THREE.Points(moteGeo, new THREE.PointsMaterial({ size: 0.035, map: dotTex, vertexColors: true, transparent: true, depthWrite: false, blending: THREE.AdditiveBlending }));
motes.frustumCulled = false; scene.add(motes);

// ───────────────────────── HUD (screen-space DOM, driven by the same t)
const NS = 'http://www.w3.org/2000/svg', svg = document.getElementById('lines'), labelsEl = document.getElementById('labels');
function mkCallout(name, note, x, y) {
  const line = document.createElementNS(NS, 'polyline'); line.setAttribute('fill', 'none'); line.setAttribute('stroke', '#e2e8f0');
  line.setAttribute('stroke-opacity', '0.85'); line.setAttribute('stroke-width', '1.8');
  const dot = document.createElementNS(NS, 'circle'); dot.setAttribute('fill', '#e2e8f0'); svg.append(line, dot);
  const el = document.createElement('div'); el.className = 'lbl'; el.style.left = x + 'px'; el.style.top = y + 'px';
  const n = document.createElement('div'); n.className = 'n'; const tt = document.createElement('div'); tt.className = 't'; tt.textContent = note;
  el.append(n, tt); labelsEl.append(el); return { name, x, y, line, dot, el, n, tt };
}
const intro = [
  { c: mkCallout('A  BODY', '×1 · the Claude Code agent', 1250, 236), part: 'body', at: [0, 0.42, 0.61] },
  { c: mkCallout('C  ARMS', '×2 · write code, hand back a commit', 1250, 376), part: 'armR', at: [0, 0, 0.14] },
  { c: mkCallout('E  MOUTH', '×0 · no chatter — tokens saved', 1250, 516), part: 'body', at: [0, -0.38, 0.61] },
  { c: mkCallout('B  LEGS', '×4 · carry whatever you stack', 1250, 656), part: 'legFR', at: [0, 0, 0.14] },
];
const calloutF = mkCallout('F  LANDING', 'live in 60 seconds', 1452, 182);
const v3 = new THREE.Vector3();
function toScreen(obj, x, y, z) { v3.set(x, y, z); obj.localToWorld(v3); v3.project(camera); return [(v3.x + 1) / 2 * W, (1 - v3.y) / 2 * H]; }
function drawCallout(c, t, P, T0, fadeAt) {
  const pts = [P, [c.x - 46, c.y + 18], [c.x - 12, c.y + 18]];
  const len = Math.hypot(pts[1][0] - P[0], pts[1][1] - P[1]) + 36;
  const dp = ease.back(prog(t, T0, T0 + 0.26)), lp = ease.line(prog(t, T0 + 0.12, T0 + 0.58));
  const np = prog(t, T0 + 0.48, T0 + 0.84), tp = prog(t, T0 + 0.72, T0 + 1.04);
  const fade = fadeAt ? 1 - prog(t, fadeAt, fadeAt + 0.28) : 1;
  c.line.setAttribute('points', pts.map(p => p.map(v => v.toFixed(1)).join(',')).join(' '));
  c.line.setAttribute('stroke-dasharray', len.toFixed(1)); c.line.setAttribute('stroke-dashoffset', (len * (1 - lp)).toFixed(1));
  c.line.style.opacity = lp > 0 ? fade : 0;
  c.dot.setAttribute('cx', P[0].toFixed(1)); c.dot.setAttribute('cy', P[1].toFixed(1)); c.dot.setAttribute('r', (4.6 * Math.max(0, dp)).toFixed(2));
  c.dot.style.opacity = dp > 0 ? fade : 0;
  const nChars = Math.floor(np * (c.name.length + 0.999)), typing = np > 0 && np < 1;
  c.n.textContent = c.name.slice(0, nChars) + (typing ? '▌' : '');
  c.el.style.opacity = fade; c.tt.style.opacity = (0.78 * tp).toFixed(3); c.tt.style.transform = `translateY(${(6 * (1 - tp)).toFixed(1)}px)`;
}
const termEl = document.getElementById('term'), termBd = document.getElementById('termbd'), spinEl = document.getElementById('spin');
const PROMPT = 'make me a landing page';
function drawTerminal(t) {
  const a = ease.out3(prog(t, 7.2, 7.6));
  termEl.style.opacity = a.toFixed(3); termEl.style.transform = `translateX(${(-44 * (1 - a)).toFixed(1)}px)`; termEl.style.filter = a < 1 ? `blur(${(8 * (1 - a)).toFixed(1)}px)` : 'none';
  const n = Math.floor(prog(t, 7.65, 8.6) * (PROMPT.length + 0.999)), typing = t >= 7.65 && t < 8.75;
  let html = `<div><span class="pr">&gt;</span> ${PROMPT.slice(0, n)}${typing && Math.floor(t * 3.5) % 2 === 0 ? '▌' : ''}</div>`;
  const thinking = t >= 8.75 && t < 9.5;
  if (thinking) html += `<div class="sk" style="background-position:${(200 - ((t - 8.75) * 260) % 220).toFixed(0)}% 0"></div>`;
  if (t >= 9.5) { const k = prog(t, 9.5, 9.7); html += `<div class="ok" style="opacity:${k.toFixed(2)}">✓ live · 58 s</div>`; }
  termBd.innerHTML = html;
  spinEl.style.opacity = thinking ? 1 : 0; spinEl.style.transform = `rotate(${(t * 540) % 360}deg)`;
}
const capEl = document.getElementById('cap'); const CAP = ['One', 'prompt.', 'A', 'website.'];
capEl.innerHTML = CAP.map(w => `<span>${w}</span>`).join(''); const capSpans = [...capEl.children];
function drawCaption(t) {
  capSpans.forEach((s, i) => {
    const p = prog(t, 10.6 + i * 0.14, 10.6 + i * 0.14 + 0.5);
    s.style.opacity = clamp(p * 3).toFixed(3); s.style.transform = `translateY(${(-70 * (1 - ease.back(p))).toFixed(1)}px)`;
  });
}
const partEl = document.getElementById('part');
const grain = document.getElementById('grain'), gctx = grain.getContext('2d'), gimg = gctx.createImageData(960, 540);
function drawGrain(t) {
  const r = rng(Math.floor(t * 30) + 1), d = gimg.data;
  for (let i = 0; i < d.length; i += 4) { const v = (r() * 255) | 0; d[i] = d[i + 1] = d[i + 2] = v; d[i + 3] = 255; }
  gctx.putImageData(gimg, 0, 0);
}

// ───────────────────────── timeline
const JUMP = [[0, 0, 1, 1], [0.2, 0, 1.08, 0.8], [0.48, 0.86, 0.95, 1.08], [0.56, 0.92, 1, 1], [0.8, 0, 1.07, 0.86], [0.91, 0.1, 0.98, 1.03], [1, 0, 1, 1]];
const JUMP_EASE = [ease.io, ease.out3, ease.io, ease.in2, ease.out3, ease.io];
function jumpAt(u) {
  if (u <= 0 || u >= 1) return [0, 1, 1];
  for (let i = 0; i < JUMP.length - 1; i++) { const a = JUMP[i], b = JUMP[i + 1]; if (u <= b[0]) { const k = JUMP_EASE[i]((u - a[0]) / (b[0] - a[0])); return [lerp(a[1], b[1], k), lerp(a[2], b[2], k), lerp(a[3], b[3], k)]; } }
  return [0, 1, 1];
}
const SHADE = [[0, 1, 1], [0.2, 1.1, 1], [0.56, 0.62, 0.45], [0.8, 1.08, 1], [1, 1, 1]];
function shadeAt(u) {
  if (u <= 0 || u >= 1) return [1, 1];
  for (let i = 0; i < SHADE.length - 1; i++) { const a = SHADE[i], b = SHADE[i + 1]; if (u <= b[0]) { const k = ease.io((u - a[0]) / (b[0] - a[0])); return [lerp(a[1], b[1], k), lerp(a[2], b[2], k)]; } }
  return [1, 1];
}
const T = { flyStart: 0.3, snap: 3.85, turn0: 4.47, turn1: 5.25, jump0: 5.25, jump1: 6.25, lit0: 5.6, lit1: 6.2, brick0: 7.6, drop: 9.3, hit: 9.45 };
const camA0 = new THREE.Vector3(2.7, 1.65, 11.2), camA1 = new THREE.Vector3(1.25, 1.3, 10.4), tgtA = new THREE.Vector3(1.8, -0.1, 0);
const camB = new THREE.Vector3(2.6, 0.95, 9.2), tgtB = new THREE.Vector3(0.15, -0.12, 0);
const camB2 = new THREE.Vector3(3.05, 1.05, 9.0);
const camC = new THREE.Vector3(1.9, 0.9, 8.6), tgtC = new THREE.Vector3(0.1, -0.1, 0);
const cp = new THREE.Vector3(), ct = new THREE.Vector3(), tmp = new THREE.Vector3();

function renderAt(t) {
  // materialization: blueprint drawing → physical toy
  const L = ease.io(prog(t, T.lit0, T.lit1));
  for (const m of figMats) { m.emissiveIntensity = lerp(1, m === eyeDark ? 0.0 : 0.09, L); if (m.bumpMap) m.bumpScale = 1.2 * L; }
  edgeMat.opacity = lerp(0.6, 0.2, L);
  key.intensity = 1.75 * L; fill.intensity = 0.5 * L; rim.intensity = 1.7 * L; scene.environmentIntensity = 0.3 * L;
  shadowMat.opacity = 0.55 * L; floorMat.uniforms.uWarm.value = 0.18 * L; floorMat.uniforms.uGlow.value = 0.7 * L;
  bloom.strength = 0.22 * L;

  // S01 · parts fly in from the right, hang apart, snap home with a spring
  PARTS.forEach((p, i) => {
    const P = parts[p.id], s0 = T.flyStart + i * 0.07;
    const e1 = ease.flyIn(prog(t, s0, s0 + 0.95));
    const sStart = T.snap + (p.id === 'body' ? 0 : 0.04 + i * 0.025), e2 = ease.spring(prog(t, sStart, sStart + 0.62));
    tmp.set(...p.from).lerp(v3.set(...p.explode), e1);
    P.inner.position.set(lerp(tmp.x, 0, e2), lerp(tmp.y, 0, e2), lerp(tmp.z, 0, e2));
    P.inner.rotation.set(lerp(p.spin[0], 0, e1) * D2R, lerp(p.spin[1], 0, e1) * D2R, 0);
    P.inner.scale.setScalar(lerp(0.55, 1, e1));
    P.inner.visible = t >= s0;
  });
  turn.rotation.y = lerp(34, 0, ease.turn(prog(t, T.turn0, T.turn1))) * D2R;

  // squat-jump (landing keyframes) + snap squash + hop + idle breathing
  let [dy, sx, sy] = jumpAt(prog(t, T.jump0, T.jump1));
  if (t >= T.hit) { const u = t - T.hit, s = 0.06 * Math.exp(-u * 9) * Math.cos(u * 22); sy *= 1 - s; sx *= 1 + s * 0.5; }
  const hu = prog(t, 9.78, 10.4); if (hu > 0 && hu < 1) { const [hy, hx, hs] = jumpAt(hu); dy += hy * 0.36; sx *= 1 + (hx - 1) * 0.6; sy *= 1 + (hs - 1) * 0.6; }
  if (t > 7.0) sy *= 1 + 0.006 * Math.sin((t - 7.0) * 2.4);
  bounce.position.y = FEET + dy; bounce.scale.set(sx, sy, sx);
  const [ss, so] = shadeAt(prog(t, T.jump0, T.jump1));
  flatShadow.scale.set(ss, ss, 1); flatShadow.material.opacity = so * (1 - L);

  // eyes: blink, then slots → happy arcs
  const blink = bell(prog(t, 7.05, 7.25)) * 0.9;
  const close = ease.in2(prog(t, 9.62, 9.74)), open = ease.back(prog(t, 9.74, 9.94));
  ['eyeL', 'eyeR'].forEach((id, i) => {
    const slot = parts[id].mesh; slot.scale.y = Math.max(0.001, (1 - blink) * lerp(1, 0.06, close)); slot.visible = t < 9.74;
    arcs[i].scale.setScalar(t < 9.74 ? 0.001 : Math.max(0.001, lerp(0.06, 1, open)));
  });

  // S03 · the cursor brings LANDING down, hovers, drops; snap
  landing.visible = t >= T.brick0;
  const kDesc = ease.out3(prog(t, T.brick0, 9.0)), kHover = ease.io(prog(t, 9.0, T.drop)), kDrop = ease.in2(prog(t, T.drop, T.hit));
  let by = LANDING_REST + lerp(5.6, 0.55, kDesc); by = lerp(by, LANDING_REST + 0.24, kHover); by = lerp(by, LANDING_REST, kDrop);
  const sway = (1 - kDesc) * 0.16 * Math.sin((t - T.brick0) * 2.3) + (1 - kHover) * kDesc * 0.03 * Math.sin(t * 9);
  const bx = lerp(2.6, 0, ease.out3(prog(t, T.brick0, 9.1)));
  landing.position.set(t < T.hit ? bx + sway : 0, by, 0); landing.rotation.z = t < T.hit ? sway * 0.25 : 0;
  scene.updateMatrixWorld(true);
  cursor.visible = t >= T.brick0 && t < 10.6;
  if (cursor.visible) {
    landing.localToWorld(tmp.set(LANDING.w / 2 - 0.05, LANDING.h / 2 + 0.02, LANDING.d / 2 - 0.05));
    const out = ease.in3(prog(t, 9.55, 10.5));
    cursor.position.set(tmp.x + 0.02 + out * 1.6, tmp.y + out * 3.4, tmp.z + 0.1);
    cursor.rotation.set(0, -0.25, 0.1 - out * 0.4);
    const press = bell(prog(t, T.drop - 0.05, T.hit + 0.1)) * 0.12; cursor.scale.set(0.8 * (1 + press * 0.3), 0.8 * (1 - press), 0.8);
  }
  dustTop.update(t, T.hit, 0, 0.66, 0, LANDING.w / 2, LANDING.d / 2);
  dustFloor.update(t, T.jump0 + 0.8, 0, FEET + 0.03, 0, 1.0, 0.7);

  // flag pops up and waves
  const fp = ease.back(prog(t, 10.0, 10.42)); flag.scale.setScalar(Math.max(0.001, fp));
  const ca = clothGeo.attributes.position.array;
  for (let i = 0; i < ca.length; i += 3) { const x = cloth0[i], y = cloth0[i + 1]; ca[i + 2] = Math.sin(x * 7.5 - t * 8) * 0.05 * (x / 0.62) + Math.sin(y * 9 + t * 5) * 0.008 * (x / 0.62); }
  clothGeo.attributes.position.needsUpdate = true; clothGeo.computeVertexNormals();

  // ambient motes (only in the physical world)
  for (let i = 0; i < MOTES; i++) {
    const m = mote0[i], y = ((m[1] + 1.3 + t * 0.06 * m[4]) % 5.5) - 1.3;
    motePos[i * 3] = m[0] + Math.sin(t * 0.3 * m[4] + m[3]) * 0.25; motePos[i * 3 + 1] = y; motePos[i * 3 + 2] = m[2] + Math.cos(t * 0.25 + m[3]) * 0.2;
    const a = L * 0.32 * (0.55 + 0.45 * Math.sin(t * 1.7 * m[4] + m[3])); moteCol[i * 3] = a; moteCol[i * 3 + 1] = a * 0.88; moteCol[i * 3 + 2] = a * 0.78;
  }
  moteGeo.attributes.position.needsUpdate = true; moteGeo.attributes.color.needsUpdate = true;

  // camera: slow arc (S01) → recentre after the jump → greet the brick → slow push-in
  cp.copy(camA0).lerp(camA1, ease.io(prog(t, 0, 6.1))); ct.copy(tgtA);
  const kB = ease.turn(prog(t, 6.1, 7.7)); cp.lerp(camB, kB); ct.lerp(tgtB, kB);
  cp.lerp(camB2, ease.io(prog(t, 7.7, 10.6)) * (1 - prog(t, 10.6, 16)));
  const kC = ease.io(prog(t, 10.6, 16)); cp.lerp(camC, kC); ct.lerp(tgtC, kC);
  ct.y += 0.22 * bell(prog(t, 7.4, 9.6));
  camera.position.copy(cp); camera.lookAt(ct); camera.updateMatrixWorld();
  scene.updateMatrixWorld(true);

  // HUD
  intro.forEach(({ c, part, at }, i) => drawCallout(c, t, toScreen(parts[part].inner, ...at), 1.9 + i * 0.12, T.snap));
  drawCallout(calloutF, t, toScreen(landing, LANDING.w / 2 - 0.25, 0.05, LANDING.d / 2 + 0.01), 10.15, null);
  drawTerminal(t); drawCaption(t);
  partEl.style.opacity = ease.out3(prog(t, 6.7, 7.2)).toFixed(3);
  drawGrain(t);

  composer.render();
}

window.renderAt = renderAt;
renderer.compile(scene, camera);
renderAt(0);
window.__ready = true;
} catch (e) { window.__error = String(e && e.stack || e); console.error(e); }
