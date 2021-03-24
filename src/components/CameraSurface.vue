<template>
  <div ref="canvasBackground" class="surface-container">

    <div class="overlay overlay-background">
      <slot name="background"></slot>
    </div>

    <video class="mirrored" ref="videoE" width="1280" height="720"></video>

    <div class="overlay">
      <slot name="ui"></slot>
    </div>

    <DrawingSurface
    :enableDrawing="isActivelyTracking"
    :mpResults="trackingResults" ref="drawingSurface" class="overlay"/>
  </div>
</template>

<script lang="ts">

import { defineComponent, onUpdated, ref } from 'vue';
import DrawingSurface from './DrawingSurface.vue';
import { isTracking as mpIsTracking, StartTracking } from '../services/MediaPipe';

export default defineComponent({
  name: 'CameraSurface',
  components: {
    DrawingSurface,
  },
  setup() {
    // const { enableDrawing } = toRefs(props);
    const hasStartedTracking = ref(false);
    const isActivelyTracking = ref(false);
    const hasResults = ref(false);
    const trackingResults = ref({});

    onUpdated(() => {
      isActivelyTracking.value = mpIsTracking();
    });

    return {
      hasStartedTracking,
      isActivelyTracking,
      hasResults,
      trackingResults,
    };
  },
  methods: {
    startTracking() {
      if (this.hasStartedTracking) return;
      this.hasStartedTracking = true;

      StartTracking(
        this.$refs.videoE as HTMLVideoElement,
        (this.$refs.drawingSurface as any).$refs.canvasE as HTMLCanvasElement,
        this.onResults,
      );
    },
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    onResults(results: any) {
      if (!this.hasResults) {
        this.$emit('tracking-attained');
        console.log('Got Results', results);
      }
      this.hasResults = true;
      this.trackingResults = results;
      // this.$refs.drawingSurface.draw(results, canvasCtx);
    },
  },
});
</script>

<style lang="scss">

.surface-container {
  position: relative;
  margin: auto;
  width: 1280px;
  height: 720px;
  box-sizing: content-box;
  text-align: center;

  .overlay {
    position: absolute;
    top: 0;
    bottom: 0;
    left: 0;
    right: 0;
  }
}

.mirrored {
  transform: scaleX(-1);
}

// .overlay-background {
//   z-index: -1;
// }

</style>
