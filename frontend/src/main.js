import * as Cesium from "cesium";

Cesium.Ion.defaultAccessToken = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJub25jZSI6InA2anh4Z2k4OTNWMU5abk8iLCJqdGkiOiJjNzU0NzE1Yi03YzUxLTQ5NmYtOGI0Zi05Zjc2NTk1Y2FhN2QiLCJpZCI6NTA3MjU1LCJpc3MiOiJodHRwczovL2FwaS5jZXNpdW0uY29tIiwiYXVkIjoidW5kZWZpbmVkX2RlZmF1bHQiLCJpYXQiOjE3OTAzMTcxOTF9.iOCGQY34RC0Rsh1n_kkxoqwTJNpscRF3kXYDl2Suuic";

const API = "http://127.0.0.1:8000";

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