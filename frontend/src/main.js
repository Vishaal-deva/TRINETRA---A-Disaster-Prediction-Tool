import * as Cesium from "cesium";

Cesium.Ion.defaultAccessToken = import.meta.env.VITE_CESIUM_ION_TOKEN;

const API = import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8000";

const viewer = new Cesium.Viewer("app", {
  terrain: Cesium.Terrain.fromWorldTerrain(),
  baseLayer: new Cesium.ImageryLayer(
    new Cesium.UrlTemplateImageryProvider({
      url: "https://tile.openstreetmap.org/{z}/{x}/{y}.png",
      maximumLevel: 19,
    })
  ),
  baseLayerPicker: false,
  geocoder: false,
});

const res = await fetch(`${API}/api/river-path`);
const { points } = await res.json();

viewer.entities.add({
  polyline: {
    positions: Cesium.Cartesian3.fromDegreesArray(points.flatMap(p => [p.lon, p.lat])),
    width: 4,
    material: Cesium.Color.CYAN,
    clampToGround: true,
  },
});
viewer.zoomTo(viewer.entities);
