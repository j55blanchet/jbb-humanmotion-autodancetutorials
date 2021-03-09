<template>
  <div ref="canvasBackground" class="container">
    <video ref="videoE" width="1280" height="720"></video>

    <div class="overlay">
      <slot></slot>
    </div>

    <canvas ref="canvasE" width="1280" height="720"></canvas>

    <div class="overlay">
      <button v-if="!isTracking" @click="startTracking()">Start Tracking</button>
    </div>
  </div>
</template>

<script lang="ts">

import { defineComponent } from 'vue';
import { StartTracking, DrawPose, GetCanvas } from '../services/MediaPipe';

export default defineComponent({
  name: 'CameraSurface',
  data: function (){
    return {
      isTracking: false,
      hasResults: false
    }
  },
  methods: {
    startTracking() {
      if (this.isTracking) return;
      this.isTracking = true;

      StartTracking(
        this.$refs.videoE as HTMLVideoElement,
        this.$refs.canvasE as HTMLCanvasElement,
        this.onResults);
    },
    onResults(results: any, canvasCtx: CanvasRenderingContext2D) {
      if (!this.hasResults)
        console.log("Got Results", results);
      this.hasResults = true;

      const canvas = canvasCtx.canvas;
      canvasCtx.clearRect(0, 0, canvas.width, canvas.height);

      if (results.poseLandmarks)
        DrawPose(canvasCtx, results.poseLandmarks);
    }
  }
});
</script>

<style lang="scss">

.container {
  position: relative;
  margin: 3rem auto;
  width: 1280px;
  // height: 720px;
  box-sizing: content-box;
  text-align: center;

  canvas {
    position: absolute;
    top: 0;
    left: 0;
    width: 1280px;
    height: 720px;
  }

  .overlay {
    position: absolute;
    top: 0;
    bottom: 0;
    left: 0;
    right: 0;
  }
}

</style>
