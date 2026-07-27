import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";
import { RoomEnvironment } from "three/addons/environments/RoomEnvironment.js";
import { STLLoader } from "three/addons/loaders/STLLoader.js";

const canvas = document.querySelector("#viewport");
const loading = document.querySelector("#loading");
const status = document.querySelector("#status");
const partsContainer = document.querySelector("#parts");

const renderer = new THREE.WebGLRenderer({
  canvas,
  antialias: true,
  alpha: true,
  powerPreference: "high-performance",
});
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.48;
renderer.localClippingEnabled = true;

const scene = new THREE.Scene();
scene.fog = new THREE.FogExp2(0x08131b, 0.00125);
const environmentGenerator = new THREE.PMREMGenerator(renderer);
scene.environment = environmentGenerator.fromScene(
  new RoomEnvironment(),
  0.04,
).texture;
environmentGenerator.dispose();

const camera = new THREE.PerspectiveCamera(35, 1, 1, 3000);
camera.up.set(0, 0, 1);
camera.position.set(470, -520, 360);

const controls = new OrbitControls(camera, renderer.domElement);
controls.target.set(0, 0, 125);
controls.enableDamping = true;
controls.dampingFactor = 0.065;
controls.minDistance = 290;
controls.maxDistance = 1150;
controls.autoRotateSpeed = 1.2;
controls.zoomToCursor = true;
controls.update();

scene.add(new THREE.HemisphereLight(0xd7f3ff, 0x26333d, 3.25));
scene.add(new THREE.AmbientLight(0xffffff, 1.35));

const key = new THREE.DirectionalLight(0xffffff, 4.0);
key.position.set(360, -260, 560);
scene.add(key);

const fill = new THREE.DirectionalLight(0x76cce9, 2.1);
fill.position.set(-400, -100, 260);
scene.add(fill);

const rim = new THREE.DirectionalLight(0xffc77e, 2.4);
rim.position.set(120, 450, 380);
scene.add(rim);

const ground = new THREE.Mesh(
  new THREE.CircleGeometry(330, 96),
  new THREE.MeshStandardMaterial({
    color: 0x0b1820,
    metalness: 0.15,
    roughness: 0.78,
    transparent: true,
    opacity: 0.78,
  }),
);
ground.position.z = -23;
scene.add(ground);

const grid = new THREE.GridHelper(650, 13, 0x315568, 0x1b303c);
grid.rotation.x = Math.PI / 2;
grid.position.z = -22.5;
grid.material.transparent = true;
grid.material.opacity = 0.34;
scene.add(grid);

const model = new THREE.Group();
scene.add(model);

const clippingPlane = new THREE.Plane(new THREE.Vector3(-1, 0, 0), 0);
let cutawayEnabled = true;
let dimensionsEnabled = true;

const partDefinitions = [
  { id: "chamber", label: "Камера", color: 0x5f6b73, metalness: 0.86, roughness: 0.28, cut: true },
  { id: "drain_cap", label: "Дренаж", color: 0xc18a36, metalness: 0.8, roughness: 0.3, cut: true },
  { id: "pan", label: "Чаша", color: 0xb9c9cf, metalness: 0.9, roughness: 0.19, cut: true },
  { id: "lid", label: "Крышка", color: 0x98a4aa, metalness: 0.86, roughness: 0.25, cut: true },
  { id: "gasket", label: "Прокладка", color: 0xc44b30, metalness: 0.05, roughness: 0.7, cut: true },
  { id: "lock_ring", label: "Замок", color: 0x7d8890, metalness: 0.88, roughness: 0.27, cut: true },
  { id: "seal", label: "Уплотнение", color: 0x28343b, metalness: 0.3, roughness: 0.5, cut: true },
  { id: "splash", label: "Экран", color: 0x478ba7, metalness: 0.72, roughness: 0.3, cut: true },
  { id: "spindle", label: "Вал", color: 0xcbd5d9, metalness: 0.94, roughness: 0.17, cut: false },
  { id: "mixer", label: "Мешалка", color: 0xd6e1e4, metalness: 0.96, roughness: 0.14, cut: false },
  { id: "ports", label: "Штуцеры", color: 0x819097, metalness: 0.82, roughness: 0.3, cut: false },
  { id: "motor", label: "Привод", color: 0x243440, metalness: 0.7, roughness: 0.35, cut: false },
];

const meshes = new Map();
const materials = [];
const loader = new STLLoader();

function makeMaterial(definition) {
  const material = new THREE.MeshStandardMaterial({
    color: definition.color,
    metalness: definition.metalness,
    roughness: definition.roughness,
    side: THREE.DoubleSide,
    clippingPlanes: definition.cut && cutawayEnabled ? [clippingPlane] : [],
  });
  material.userData.cuttable = definition.cut;
  materials.push(material);
  return material;
}

function loadStl(definition) {
  return new Promise((resolve, reject) => {
    loader.load(
      `./models/hda1_${definition.id}.stl`,
      (geometry) => {
        geometry.computeVertexNormals();
        const mesh = new THREE.Mesh(geometry, makeMaterial(definition));
        mesh.name = definition.id;
        mesh.castShadow = false;
        mesh.receiveShadow = false;
        model.add(mesh);
        meshes.set(definition.id, mesh);
        resolve(mesh);
      },
      undefined,
      reject,
    );
  });
}

function addPartToggle(definition) {
  const label = document.createElement("label");
  label.className = "part-toggle";
  label.style.setProperty("--swatch", `#${definition.color.toString(16).padStart(6, "0")}`);
  label.innerHTML = `
    <input type="checkbox" checked data-part="${definition.id}">
    <span class="swatch"></span>
    <span>${definition.label}</span>
  `;
  label.querySelector("input").addEventListener("change", (event) => {
    const mesh = meshes.get(event.target.dataset.part);
    if (mesh) mesh.visible = event.target.checked;
    if (event.target.dataset.part === "ports") reliefValve.visible = event.target.checked;
  });
  partsContainer.append(label);
}

partDefinitions.forEach(addPartToggle);

function cylinderBetweenAxis(radius, length, material, axis = "z") {
  const geometry = new THREE.CylinderGeometry(radius, radius, length, 32);
  const mesh = new THREE.Mesh(geometry, material);
  if (axis === "x") mesh.rotation.z = Math.PI / 2;
  if (axis === "z") mesh.rotation.x = Math.PI / 2;
  return mesh;
}

// Recognisable schematic safety valve placed over the original red radial port.
const reliefValve = new THREE.Group();
reliefValve.name = "relief-valve-visual";
const reliefRed = new THREE.MeshStandardMaterial({
  color: 0xd93632,
  metalness: 0.42,
  roughness: 0.29,
});
const darkMetal = new THREE.MeshStandardMaterial({
  color: 0x303a40,
  metalness: 0.8,
  roughness: 0.32,
});

const valveInlet = cylinderBetweenAxis(10, 28, reliefRed, "x");
valveInlet.position.set(131, 38, 113);
reliefValve.add(valveInlet);

const valveBonnet = cylinderBetweenAxis(7, 28, reliefRed, "z");
valveBonnet.position.set(141, 38, 130);
reliefValve.add(valveBonnet);

const valveCap = cylinderBetweenAxis(11, 6, darkMetal, "z");
valveCap.position.set(141, 38, 146);
reliefValve.add(valveCap);

const valveOutlet = cylinderBetweenAxis(6, 22, reliefRed, "y");
valveOutlet.position.set(141, 50, 127);
reliefValve.add(valveOutlet);
model.add(reliefValve);

function makeLabel(text, color = "#dff7ff") {
  const labelCanvas = document.createElement("canvas");
  labelCanvas.width = 640;
  labelCanvas.height = 160;
  const ctx = labelCanvas.getContext("2d");
  ctx.clearRect(0, 0, labelCanvas.width, labelCanvas.height);
  ctx.fillStyle = "rgba(4, 13, 19, 0.88)";
  ctx.strokeStyle = "rgba(116, 216, 205, 0.8)";
  ctx.lineWidth = 5;
  ctx.beginPath();
  ctx.roundRect(8, 8, 624, 144, 24);
  ctx.fill();
  ctx.stroke();
  ctx.fillStyle = color;
  ctx.font = "700 72px Segoe UI, Arial";
  ctx.textAlign = "center";
  ctx.textBaseline = "middle";
  ctx.fillText(text, 320, 82);

  const texture = new THREE.CanvasTexture(labelCanvas);
  texture.colorSpace = THREE.SRGBColorSpace;
  const sprite = new THREE.Sprite(
    new THREE.SpriteMaterial({
      map: texture,
      transparent: true,
      depthTest: false,
      toneMapped: false,
    }),
  );
  sprite.renderOrder = 10;
  sprite.scale.set(92, 23, 1);
  return sprite;
}

const dimensions = new THREE.Group();
dimensions.name = "dimensions";
scene.add(dimensions);

function addDimensionLine(points, labelText, labelPosition) {
  const geometry = new THREE.BufferGeometry().setFromPoints(points);
  const line = new THREE.Line(
    geometry,
    new THREE.LineBasicMaterial({ color: 0x74d8cd, transparent: true, opacity: 0.95 }),
  );
  dimensions.add(line);
  const label = makeLabel(labelText);
  label.position.copy(labelPosition);
  dimensions.add(label);
}

addDimensionLine(
  [
    new THREE.Vector3(-141, -172, -22),
    new THREE.Vector3(-141, -158, -22),
    new THREE.Vector3(141, -158, -22),
    new THREE.Vector3(141, -172, -22),
  ],
  "282 мм",
  new THREE.Vector3(0, -176, -22),
);

addDimensionLine(
  [
    new THREE.Vector3(-172, -141, -22),
    new THREE.Vector3(-158, -141, -22),
    new THREE.Vector3(-158, 141, -22),
    new THREE.Vector3(-172, 141, -22),
  ],
  "282 мм",
  new THREE.Vector3(-178, 0, -22),
);

addDimensionLine(
  [
    new THREE.Vector3(-172, 158, -22),
    new THREE.Vector3(-158, 158, -22),
    new THREE.Vector3(-158, 158, 289),
    new THREE.Vector3(-172, 158, 289),
  ],
  "311 мм",
  new THREE.Vector3(-178, 158, 134),
);

function setPressed(button, pressed) {
  button.classList.toggle("active", pressed);
  button.setAttribute("aria-pressed", String(pressed));
}

document.querySelector("#resetView").addEventListener("click", () => {
  camera.position.set(470, -520, 360);
  controls.target.set(0, 0, 125);
  controls.update();
});

document.querySelector("#toggleRotate").addEventListener("click", (event) => {
  controls.autoRotate = !controls.autoRotate;
  setPressed(event.currentTarget, controls.autoRotate);
});

document.querySelector("#toggleCutaway").addEventListener("click", (event) => {
  cutawayEnabled = !cutawayEnabled;
  materials.forEach((material) => {
    material.clippingPlanes =
      material.userData.cuttable && cutawayEnabled ? [clippingPlane] : [];
    material.needsUpdate = true;
  });
  setPressed(event.currentTarget, cutawayEnabled);
});

document.querySelector("#toggleDimensions").addEventListener("click", (event) => {
  dimensionsEnabled = !dimensionsEnabled;
  dimensions.visible = dimensionsEnabled;
  setPressed(event.currentTarget, dimensionsEnabled);
});

function resizeRenderer() {
  const rect = canvas.getBoundingClientRect();
  const width = Math.max(1, Math.round(rect.width));
  const height = Math.max(1, Math.round(rect.height));
  renderer.setSize(width, height, false);
  camera.aspect = width / height;
  camera.updateProjectionMatrix();
}

const resizeObserver = new ResizeObserver(resizeRenderer);
resizeObserver.observe(canvas);
resizeRenderer();

function animate() {
  controls.update();
  renderer.render(scene, camera);
  requestAnimationFrame(animate);
}

try {
  await Promise.all(partDefinitions.map(loadStl));
  loading.classList.add("hidden");
  status.textContent = "12 STL загружены · геометрия в миллиметрах";
} catch (error) {
  console.error(error);
  loading.innerHTML = "Не удалось загрузить модель. Обновите страницу.";
  status.textContent = "Ошибка загрузки геометрии";
}

animate();
