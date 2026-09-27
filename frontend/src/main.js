import * as Cesium from "cesium";
import "cesium/Build/Cesium/Widgets/widgets.css";
import concaveman from "concaveman";

function chaikinSmooth(points, iterations) {
  let pts = points;
  for (let it = 0; it < iterations; it++) {
    const next = [];
    for (let i = 0; i < pts.length; i++) {
      const p0 = pts[i];
      const p1 = pts[(i + 1) % pts.length];
      next.push([p0[0] * 0.8 + p1[0] * 0.2, p0[1] * 0.8 + p1[1] * 0.2]);
      next.push([p0[0] * 0.2 + p1[0] * 0.8, p0[1] * 0.2 + p1[1] * 0.8]);
    }
    pts = next;
  }
  return pts;
}

const viewer = new Cesium.Viewer("app", {
  terrain: Cesium.Terrain.fromWorldTerrain(),
  baseLayer: new Cesium.ImageryLayer(
    new Cesium.UrlTemplateImageryProvider({
      url: "https://tile.opentopomap.org/{z}/{x}/{y}.png",
      maximumLevel: 17,
    })
  ),
  baseLayerPicker: false,
  geocoder: false,
  animation: false,
  timeline: false,
  homeButton: false,
  sceneModePicker: false,
  navigationHelpButton: false,
  fullscreenButton: false,
});

viewer.scene.globe.enableLighting = true;
viewer.scene.globe.depthTestAgainstTerrain = true;
viewer.scene.verticalExaggeration = 2.0;

const baseImageryLayer = viewer.imageryLayers.get(0);
baseImageryLayer.saturation = 1.3;
baseImageryLayer.contrast = 1.15;

viewer.cesiumWidget.creditContainer.style.display = "none";
const credit = document.createElement("div");
credit.innerHTML = '@ powered by <img src="/cesium-icon.png" style="height:12px;vertical-align:middle;margin:0 4px;"> CESIUM ION services';
credit.style.position = "absolute";
credit.style.bottom = "6px";
credit.style.left = "10px";
credit.style.color = "rgba(255,255,255,0.75)";
credit.style.fontSize = "11px";
credit.style.fontFamily = "sans-serif";
credit.style.zIndex = "1000";
document.getElementById("app").appendChild(credit);

const themeBtn = document.getElementById("theme-toggle");
let isLight = false;
themeBtn.addEventListener("click", () => {
  isLight = !isLight;
  document.body.classList.toggle("light-theme", isLight);
  themeBtn.textContent = isLight ? "LIGHT" : "DARK";
});

// --- Cauvery mainstem path (approximate route through known waypoints) ---
// Real, verified coordinates at each named point; straight-line segments
// between them, NOT a surveyed river centerline. Prototype approximation.
const CAUVERY_PATH = [
  { lon: 75.5000, lat: 12.3833 },
  { lon: 75.9500, lat: 12.4500 },
  { lon: 76.5722, lat: 12.4247 },
  { lon: 76.9000, lat: 12.2167 },
  { lon: 77.7667, lat: 12.1167 },
  { lon: 77.8000, lat: 11.8000 },
  { lon: 77.7172, lat: 11.3410 },
  { lon: 78.7047, lat: 10.7905 },
  { lon: 78.8180, lat: 10.8300 },
  { lon: 79.1378, lat: 10.7870 },
  { lon: 79.8500, lat: 11.1500 },
];

const DAMS = {
  harangi: {
    label: "Harangi Dam", lon: 75.9056, lat: 12.4917,
    type: "Tributary (Harangi River)", capacityKm3: 0.24, heightM: 50,
    info: "Kodagu, Karnataka. Masonry dam, 164ft height, built 1969-1982. Irrigation supply.",
  },
  hemavathi: {
    label: "Hemavathi Dam", lon: 76.2300, lat: 12.9300,
    type: "Tributary (Hemavathi River)", capacityKm3: 1.05, heightM: 45,
    info: "Gorur, Hassan district, Karnataka. Built 1979. Drinking water & irrigation supply.",
  },
  krs: {
    label: "Krishna Raja Sagara (KRS) Dam", lon: 76.5722, lat: 12.4247,
    type: "Mainstem", capacityKm3: 1.37, heightM: 40,
    info: "Mandya, Karnataka. Gravity dam, 39.8m height, built 1911-1932. Supplies Bengaluru & Mysuru drinking water.",
  },
  kabini: {
    label: "Kabini Dam", lon: 76.3528, lat: 11.9735,
    type: "Tributary (Kabini River)", capacityKm3: 0.55, heightM: 51,
    info: "Beechanahalli, Mysore district, Karnataka. Built 1974. Height 166ft.",
  },
  bhavanisagar: {
    label: "Bhavanisagar Dam", lon: 77.0734, lat: 11.4423,
    type: "Tributary (Bhavani River)", capacityKm3: 0.93, heightM: 34,
    info: "Erode district, Tamil Nadu. One of world's largest earthen dams, built 1955.",
  },
  mettur: {
    label: "Mettur Dam", lon: 77.8000, lat: 11.8000,
    type: "Mainstem", capacityKm3: 2.64, heightM: 37, zoomHeight: 6000, breachZoomHeight: 4500, inundationDensity: 6,
    info: "Salem, Tamil Nadu. Largest dam in South India, 120ft height, built 1934. Real flood alert issued June 2025 to 10 downstream districts.",
  },
  kallanai: {
    label: "Kallanai (Grand Anicut)", lon: 78.8180, lat: 10.8300,
    type: "Mainstem", capacityKm3: 0.01, heightM: 4,
    info: "Tiruchirappalli, Tamil Nadu. Built ~100 CE by Chola king Karikalan. Oldest water-diversion structure in the world still active.",
  },
};

function nearestPathIndex(lon, lat) {
  let best = 0, bestDist = Infinity;
  CAUVERY_PATH.forEach((p, i) => {
    const d = (p.lon - lon) ** 2 + (p.lat - lat) ** 2;
    if (d < bestDist) { bestDist = d; best = i; }
  });
  return best;
}

let breached = false;
let currentInterval = null;
const breachBtn = document.getElementById("breach-btn");
const statusText = document.getElementById("status-text");
const riverInfo = document.getElementById("river-info");
const damSelect = document.getElementById("dam-select");

function loadDam(key) {
  if (currentInterval) {
    clearInterval(currentInterval);
    currentInterval = null;
  }
  viewer.entities.removeAll();
  breached = false;
  breachBtn.disabled = false;

  const dam = DAMS[key];
  riverInfo.innerHTML = `<strong>${dam.type}</strong><br>${dam.info}`;

  viewer.entities.add({
    id: "river-line",
    polyline: {
      positions: Cesium.Cartesian3.fromDegreesArray(CAUVERY_PATH.flatMap((p) => [p.lon, p.lat])),
      width: 6,
      material: new Cesium.PolylineGlowMaterialProperty({
        color: Cesium.Color.fromCssColorString("#3fa9f5"),
        glowPower: 0.25,
        taperPower: 0.9,
      }),
      clampToGround: true,
    },
  });

  viewer.entities.add({
    id: "river-label",
    position: Cesium.Cartesian3.fromDegrees(CAUVERY_PATH[5].lon, CAUVERY_PATH[5].lat),
    label: {
      text: "Cauvery River",
      font: "16px sans-serif",
      fillColor: Cesium.Color.WHITE,
      outlineColor: Cesium.Color.BLACK,
      outlineWidth: 2,
      style: Cesium.LabelStyle.FILL_AND_OUTLINE,
      verticalOrigin: Cesium.VerticalOrigin.BOTTOM,
      pixelOffset: new Cesium.Cartesian2(0, -10),
    },
  });

  const confluenceIndex = nearestPathIndex(dam.lon, dam.lat);

  const confluencePoint = CAUVERY_PATH[confluenceIndex];
  if (dam.type.startsWith("Tributary")) {
    viewer.entities.add({
      id: "tributary-line",
      polyline: {
        positions: Cesium.Cartesian3.fromDegreesArray([
          dam.lon, dam.lat,
          confluencePoint.lon, confluencePoint.lat,
        ]),
        width: 4,
        material: new Cesium.PolylineDashMaterialProperty({
          color: Cesium.Color.fromCssColorString("#7fd4f0"),
          dashLength: 12,
        }),
        clampToGround: true,
      },
    });
  }


  viewer.entities.add({
    id: "dam-marker",
    position: Cesium.Cartesian3.fromDegrees(dam.lon, dam.lat),
    point: {
      pixelSize: 16,
      color: Cesium.Color.RED,
      outlineColor: Cesium.Color.WHITE,
      outlineWidth: 3,
      heightReference: Cesium.HeightReference.CLAMP_TO_GROUND,
    },
    label: {
      text: dam.label,
      font: "bold 14px sans-serif",
      fillColor: Cesium.Color.WHITE,
      outlineColor: Cesium.Color.BLACK,
      outlineWidth: 3,
      style: Cesium.LabelStyle.FILL_AND_OUTLINE,
      verticalOrigin: Cesium.VerticalOrigin.BOTTOM,
      pixelOffset: new Cesium.Cartesian2(0, -20),
      heightReference: Cesium.HeightReference.CLAMP_TO_GROUND,
    },
  });

  viewer.entities.add({
    id: "lake",
    position: Cesium.Cartesian3.fromDegrees(dam.lon, dam.lat),
    ellipse: {
      semiMinorAxis: 900,
      semiMajorAxis: 1500,
      material: Cesium.Color.fromCssColorString("#3fa9f5").withAlpha(0.55),
      heightReference: Cesium.HeightReference.CLAMP_TO_GROUND,
    },
  });

  statusText.textContent = `Status: ${dam.label} reservoir at normal level`;
  breachBtn.textContent = "Simulate Dam Break";

  viewer.camera.flyTo({
    destination: Cesium.Cartesian3.fromDegrees(dam.lon, dam.lat - 0.07, dam.zoomHeight || 12000),
    orientation: { heading: 0.0, pitch: Cesium.Math.toRadians(-40), roll: 0.0 },
    duration: 1.5,
  });

  breachBtn.onclick = async () => {
    if (breached) return;
    breached = true;

    viewer.entities.removeById("lake");
    breachBtn.disabled = true;
    breachBtn.textContent = "Breach Triggered";
    statusText.textContent = `Status: ${dam.label} breached, sampling real terrain...`;

    const damCarto = Cesium.Cartographic.fromDegrees(dam.lon, dam.lat);
    let damElevation = 0;
    try {
      const [sampledDam] = await Cesium.sampleTerrainMostDetailed(viewer.terrainProvider, [damCarto]);
      damElevation = sampledDam.height;
    } catch (e) {
      damElevation = 0;
    }

    const boxHalfWidth = 0.09 + dam.capacityKm3 * 0.018;
    const boxHalfHeight = 0.11 + dam.capacityKm3 * 0.018;
    const gridRes = 22;
    const latStep = (boxHalfHeight * 2) / (gridRes - 1);
    const lonStep = (boxHalfWidth * 2) / (gridRes - 1);

    const cellLon = (col) => dam.lon - boxHalfWidth + col * lonStep;
    const cellLat = (row) => dam.lat - boxHalfHeight * 1.5 + row * latStep;

    const flatPoints = [];
    for (let row = 0; row < gridRes; row++) {
      for (let col = 0; col < gridRes; col++) {
        flatPoints.push({ lon: cellLon(col), lat: cellLat(row), row, col });
      }
    }

    statusText.textContent = `Status: ${dam.label} breached, sampling ${flatPoints.length} terrain points...`;

    const cartoGrid = flatPoints.map((p) => Cesium.Cartographic.fromDegrees(p.lon, p.lat));
    let sampledGrid;
    try {
      sampledGrid = await Cesium.sampleTerrainMostDetailed(viewer.terrainProvider, cartoGrid);
    } catch (e) {
      sampledGrid = cartoGrid.map(() => ({ height: damElevation + 999 }));
    }

    const heightAt = (row, col) => {
      if (row < 0 || row >= gridRes || col < 0 || col >= gridRes) return Infinity;
      return sampledGrid[row * gridRes + col].height;
    };

    // Find grid cell nearest the dam to start the flood-fill from
    let startRow = 0, startCol = 0, bestDist = Infinity;
    flatPoints.forEach((p) => {
      const d = (p.lon - dam.lon) ** 2 + (p.lat - dam.lat) ** 2;
      if (d < bestDist) { bestDist = d; startRow = p.row; startCol = p.col; }
    });

    statusText.textContent = `Status: ${dam.label} breached, running flood-fill on connected low terrain...`;

    // BFS flood-fill: water only spreads through terrain that is BOTH low enough
    // AND reachable step-by-step from the dam - it cannot jump across a ridge.
    const maxTolerance = (dam.heightM || 30) * 0.6;
    const visited = new Array(gridRes * gridRes).fill(false);
    const depthMap = new Array(gridRes * gridRes).fill(0);
    const queue = [{ row: startRow, col: startCol, step: 0 }];
    visited[startRow * gridRes + startCol] = true;

    const maxSteps = gridRes * 1.3;
    let qi = 0;
    while (qi < queue.length) {
      const { row, col, step } = queue[qi++];
      const tolerance = maxTolerance * Math.max(1 - step / maxSteps, 0.15);
      const floodLevel = damElevation + tolerance;

      [[1,0],[-1,0],[0,1],[0,-1]].forEach(([dr, dc]) => {
        const nr = row + dr, nc = col + dc;
        if (nr < 0 || nr >= gridRes || nc < 0 || nc >= gridRes) return;
        const idx = nr * gridRes + nc;
        if (visited[idx]) return;

        const h = heightAt(nr, nc);
        const depth = floodLevel - h;
        if (depth > 0.5) {
          visited[idx] = true;
          depthMap[idx] = depth;
          queue.push({ row: nr, col: nc, step: step + 1 });
        }
      });
    }

    const floodPoints = [];
    let totalDepthAll = 0;
    for (let row = 0; row < gridRes; row++) {
      for (let col = 0; col < gridRes; col++) {
        const idx = row * gridRes + col;
        if (!visited[idx] || (row === startRow && col === startCol)) continue;
        floodPoints.push([cellLon(col), cellLat(row)]);
        totalDepthAll += depthMap[idx];
      }
    }

    if (floodPoints.length < 4) {
      statusText.textContent = `Status: ${dam.label} breach, no significant connected low-lying area found`;
    } else {
      // Concave hull traces ONE clean, non-self-intersecting boundary around
      // all flood-fill points (no overlapping circles, no bowtie glitches).
      const hull = concaveman(floodPoints, 2.0, 0);
      const smoothed = chaikinSmooth(hull, 3);

      const positions = Cesium.Cartesian3.fromDegreesArray(smoothed.flatMap((p) => [p[0], p[1]]));
      const avgDepth = totalDepthAll / floodPoints.length;
      const depthNorm = Math.min(avgDepth / 20, 1);
      const fillColor = Cesium.Color.lerp(
        Cesium.Color.fromCssColorString("#ffcc80"),
        Cesium.Color.fromCssColorString("#7f0000"),
        depthNorm,
        new Cesium.Color()
      );

      viewer.entities.add({
        id: "flood-polygon",
        polygon: {
          hierarchy: positions,
          material: fillColor.withAlpha(0.62),
          heightReference: Cesium.HeightReference.CLAMP_TO_GROUND,
        },
      });

      statusText.textContent = `Status: ${dam.label} breach, flood-fill polygon covers ${floodPoints.length} connected terrain cells (avg depth ~${avgDepth.toFixed(1)}m, elevation proxy - not full hydrodynamic solve)`;
    }

    viewer.camera.flyTo({
      destination: Cesium.Cartesian3.fromDegrees(dam.lon, dam.lat - boxHalfHeight, dam.breachZoomHeight || dam.zoomHeight || 12000),
      orientation: { heading: 0.0, pitch: Cesium.Math.toRadians(-45), roll: 0.0 },
      duration: 1.5,
    });
  };
}

damSelect.addEventListener("change", (e) => loadDam(e.target.value));
loadDam("mettur");


















const cauveryNaturalBlocks = [
  {
    id: "shivanasamudra-gorge",
    name: "Shivanasamudra Gorge",
    lon: 77.1770,
    lat: 12.3000,
    note: "Twin falls (Gaganachukki 90m / Bharachukki 69m) - river splits around an island and drops through a rocky segmented gorge.",
  },
  {
    id: "mekedatu-gorge",
    name: "Mekedatu Gorge",
    lon: 77.44866,
    lat: 12.25818,
    note: "River narrows from about 150m wide at the Sangama confluence to about 10m through a granite gorge - the sharpest natural constriction on the river.",
  },
  {
    id: "hogenakkal-falls",
    name: "Hogenakkal Falls",
    lon: 77.77385,
    lat: 12.1182,
    note: "Series of closely-spaced falls (up to 20m drop) cutting through rocky terrain before the river widens into the plains.",
  },
];

cauveryNaturalBlocks.forEach((block) => {
  viewer.entities.add({
    id: `natural-block-${block.id}`,
    position: Cesium.Cartesian3.fromDegrees(block.lon, block.lat),
    point: {
      pixelSize: 14,
      color: Cesium.Color.ORANGE,
      outlineColor: Cesium.Color.WHITE,
      outlineWidth: 2,
      heightReference: Cesium.HeightReference.CLAMP_TO_GROUND,
    },
    label: {
      text: block.name,
      font: "14px sans-serif",
      fillColor: Cesium.Color.ORANGE,
      outlineColor: Cesium.Color.BLACK,
      outlineWidth: 3,
      style: Cesium.LabelStyle.FILL_AND_OUTLINE,
      verticalOrigin: Cesium.VerticalOrigin.BOTTOM,
      pixelOffset: new Cesium.Cartesian2(0, -16),
      heightReference: Cesium.HeightReference.CLAMP_TO_GROUND,
    },
    description: block.note,
  });

  viewer.entities.add({
    id: `natural-block-zone-${block.id}`,
    position: Cesium.Cartesian3.fromDegrees(block.lon, block.lat),
    ellipse: {
      semiMinorAxis: 800,
      semiMajorAxis: 800,
      material: Cesium.Color.ORANGE.withAlpha(0.25),
      outline: true,
      outlineColor: Cesium.Color.ORANGE,
      heightReference: Cesium.HeightReference.CLAMP_TO_GROUND,
    },
  });
});

// --- Right-side legend/info panel: dams vs natural blockages (matches sidebar theme) ---
(function () {
  const panel = document.createElement("div");
  panel.id = "block-legend-panel";
  panel.style.cssText = `
    position: fixed;
    top: 76px;
    right: 16px;
    width: 250px;
    max-height: 70vh;
    overflow-y: auto;
    background: rgba(13, 27, 42, 0.94);
    color: #d7dee5;
    font-family: sans-serif;
    font-size: 13px;
    border-radius: 6px;
    padding: 14px 16px;
    z-index: 999;
    box-shadow: 0 2px 12px rgba(0,0,0,0.5);
    border: 1px solid rgba(45, 212, 191, 0.25);
  `;

  const damColor = "#e53935";
  const blockColor = "#ff9800";
  const headerStyle = "font-size:11px; letter-spacing:0.08em; color:#8fa3b3; margin-bottom:8px; text-transform:uppercase;";

  panel.innerHTML = `
    <div style="${headerStyle}">Legend</div>
    <div style="display:flex; align-items:center; margin-bottom:6px;">
      <span style="width:11px; height:11px; border-radius:50%; background:${damColor}; display:inline-block; margin-right:8px;"></span>
      Dam
    </div>
    <div style="display:flex; align-items:center; margin-bottom:14px;">
      <span style="width:11px; height:11px; border-radius:50%; background:${blockColor}; display:inline-block; margin-right:8px;"></span>
      Natural blockage / constriction
    </div>
    <div style="${headerStyle}">Cauvery Natural Blockages</div>
    <div id="block-legend-list"></div>
  `;

  document.body.appendChild(panel);

  const list = document.getElementById("block-legend-list");
  cauveryNaturalBlocks.forEach((block) => {
    const item = document.createElement("div");
    item.textContent = block.name;
    item.title = block.note;
    item.style.cssText = `
      padding: 6px 8px;
      margin-bottom: 5px;
      border-radius: 4px;
      cursor: pointer;
      background: rgba(255,152,0,0.10);
      border-left: 2px solid ${blockColor};
      font-size: 12.5px;
    `;
    item.addEventListener("mouseenter", () => { item.style.background = "rgba(255,152,0,0.24)"; });
    item.addEventListener("mouseleave", () => { item.style.background = "rgba(255,152,0,0.10)"; });
    item.addEventListener("click", () => {
      viewer.camera.flyTo({
        destination: Cesium.Cartesian3.fromDegrees(block.lon, block.lat, 3000),
        orientation: { heading: 0.0, pitch: Cesium.Math.toRadians(-45), roll: 0.0 },
        duration: 1.5,
      });
    });
    list.appendChild(item);
  });
})();
