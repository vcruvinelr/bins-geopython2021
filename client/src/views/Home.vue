<template>
  <div class="p-d-flex">
    <div id="map" class="map"></div>
    <div
      class="p-grid p-align-center p-col-2"
      style="margin-top: 390px"
      id="hexBtn"
    >
      <div class="p-mt-2 p-ml-2 hexBtn" style="text-align: center">
        <Card>
          <template #title> Hexagon Bin Drawer </template>
          <template #content>
            <InputNumber
              v-model="hexagonSide"
              suffix="km"
              mode="decimal"
              :minFractionDigits="2"
            />
            <br />
            <br />
            <Button
              :disabled="disableHexagonBtn"
              label="Draw Hexagon"
              @click="drawFeatures()"
            />
          </template>
        </Card>
      </div>
    </div>
  </div>
</template>

<script>
import "ol/ol.css";
import View from "ol/View";
import Map from "ol/Map";
import TileLayer from "ol/layer/Tile";
import { OSM, Vector as VectorSource } from "ol/source";
import axios from "axios";
import { Vector as VectorLayer } from "ol/layer";
import Draw from "ol/interaction/Draw";
import GeoJSON from "ol/format/GeoJSON";
import { useGeographic } from "ol/proj";
import { Control, defaults as defaultControls } from "ol/control";
import Button from "primevue/button";
import Card from "primevue/card";
import InputNumber from "primevue/inputnumber";
import * as turf from "@turf/turf";
import { geojsonType } from "@turf/turf";

export default {
  name: "Home",
  components: { Button, Card, InputNumber },
  data() {
    return {
      visibleBottom: false,
      mainMap: null,
      hexagonSide: null,
      disableHexagonBtn: "disable",
    };
  },
  async mounted() {
    await this.startMap();
    this.getPoints();
    this.generateHexagons();
  },
  watch: {
    hexagonSide: function (value) {
      if (value > 0) {
        this.disableHexagonBtn = null;
      } else {
        this.disableHexagonBtn = "disable";
      }
    },
  },
  methods: {
    startMap() {
      this.mainMap = new Map({
        layers: [
          new TileLayer({
            source: new OSM(),
          }),
        ],
        target: "map",
        renderer: "webgl",
        view: new View({
          projection: "EPSG:4326",
          center: [-42, -21],
          zoom: 8,
        }),
      });
      var controlPanel = new Control({
        element: document.getElementById("hexBtn"),
      });
      this.mainMap.addControl(controlPanel);

      setTimeout(() => {
        this.mainMap.updateSize();
      }, 500);
    },
    drawFeatures() {
      return new Promise(() => {
        useGeographic();

        var drawPolygonSource = new VectorSource({ wrapX: false });
        var drawTool = new Draw({
          source: drawPolygonSource,
          type: "Polygon",
        });
        this.mainMap.addInteraction(drawTool);

        var drawPolygonLayer = new VectorLayer({
          source: drawPolygonSource,
        });
        this.mainMap.addLayer(drawPolygonLayer);

        drawTool.on("drawend", (r) => {
          var geoJsonObj = new GeoJSON();
          var features = JSON.parse(geoJsonObj.writeFeatures([r.feature]));
          var extent = r.feature.getGeometry().getExtent()
          //this.postHexTurf(extent, features)
          this.postGeometry(features);
          this.mainMap.removeInteraction(drawTool);
        });
      }).catch((error) => {
        console.warn(error);
      });
    },
    postGeometry(geometry) {
      var that = this;
      var allObj = [];
      var coords = [];

      axios
        .post("http://localhost:8000/", {
          geometry: geometry,
          size: that.hexagonSide,
        })
        .then((response) => {
          response.data.forEach((r) => {
            allObj.push(r);
          });
          var now = new Date().getTime();
          var format = new GeoJSON();
          allObj.forEach((polygon) => {
            coords.push(
              format.readFeature(polygon, {
                dataProjection: "EPSG:4326",
                featureProjection: "EPSG:4326",
              })
            );
          });

          var vector = new VectorLayer({
            source: new VectorSource({
              features: coords,
            }),
          });
          this.mainMap.addLayer(vector);
        });
    },
    postHexTurf(extent, features) {
      var hexgrid = turf.hexGrid(extent, this.hexagonSide, {
        units: "kilometers",
      });
      var geomCheck = features.features[0].geometry.coordinates[0];
      var coords = [];

      var format = new GeoJSON();
      hexgrid.features.forEach((polygon) => {
        coords.push(
          format.readFeature(polygon, {
            dataProjection: "EPSG:4326",
            featureProjection: "EPSG:4326",
          })
        );
      });

      var vectorHex = new VectorLayer({
        source: new VectorSource({
          features: coords,
        }),
      });
      this.mainMap.addLayer(vectorHex);
    },
    getPoints() {
      var that = this;
      var allObj = [];
      var coords = [];

      axios.get("http://localhost:8000/points").then((response) => {
        response.data.forEach((r) => {
          allObj.push(r);
        });
        var now = new Date().getTime();
        var format = new GeoJSON();
        allObj.forEach((polygon) => {
          coords.push(
            format.readFeature(polygon, {
              dataProjection: "EPSG:4326",
              featureProjection: "EPSG:4326",
            })
          );
        });

        var vector = new VectorLayer({
          source: new VectorSource({
            features: coords,
          }),
        });
        this.mainMap.addLayer(vector);
      });
    },
    generateHexagons() {
      var that = this;
      var allObj = [];
      var coords = [];
      axios.get("http://localhost:8000/get_count").then((response) => {
        response.data.forEach((r) => {
          allObj.push(r.geom);
        });
        var format = new GeoJSON();
        allObj.forEach((polygon) => {
          coords.push(
            format.readFeature(polygon, {
              dataProjection: "EPSG:4326",
              featureProjection: "EPSG:4326",
            })
          );
        });

        var vector = new VectorLayer({
          source: new VectorSource({
            features: coords,
          }),
        });
        this.mainMap.addLayer(vector);
      });
    },
  },
};
</script>

<style>
.map {
  position: absolute;
  min-height: 100%;
  height: 600px; /* altura */
  width: 100%;
}
</style>


