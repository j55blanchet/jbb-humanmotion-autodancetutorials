<template>
  <div ref="canvasBackground" class="surface-container is-slightly-rounded">

    <div class="overlay overlay-background">
      <slot name="background"></slot>
    </div>

    <video
      class="mirrored is-slightly-rounded"
      ref="videoE"
      width="1280"
      height="720"
      muted
    ></video>

    <div class="overlay">
      <slot name="ui"></slot>
    </div>

    <DrawingSurface
    :enableDrawing="isActivelyTracking"
    :mpResults="trackingResults" ref="drawingSurface" class="overlay"/>
  </div>
</template>

<script lang="ts">

import {
  defineComponent, onUpdated, ref,
} from 'vue';
import webcamProvider from '@/services/WebcamProvider';
import DrawingSurface from './DrawingSurface.vue';
import { isTracking as mpIsTracking, StartTracking, sendFrames } from '../services/MediaPipe';

export default defineComponent({
  name: 'CameraSurface',
  components: {
    DrawingSurface,
  },
  data() {
    return {
      trackingIntervalId: -1,
    };
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
      if (this.trackingIntervalId !== -1) return;

      const videoE = this.$refs.videoE as HTMLVideoElement;
      const whenReady = () => {
        if (this.hasStartedTracking) return;
        this.hasStartedTracking = true;
        console.log('Video loaded. Starting tracking...');
        const sendFrame = StartTracking(
            this.$refs.videoE as HTMLVideoElement,
            this.onResults,
        );

        sendFrames(sendFrame);
        videoE.onloadedmetadata = null;
      };

      this.trackingIntervalId = setInterval(() => {

        if (this.hasStartedTracking) {
          clearInterval(this.trackingIntervalId);
          this.trackingIntervalId = -1;
        }

        if (videoE.readyState === 4) {
          whenReady();
          return;
        }

        console.log('Video not ready, will start tracking when loaded.');
      }, 100);

      webcamProvider.connectVideoElement(videoE);
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

  background: rgba(0, 0, 0, 0.3);

  .overlay {
    position: absolute;
    top: 0;
    bottom: 0;
    left: 0;
    right: 0;
  }

  .overlay.overlay-bottom {
    top: auto;
  }
  .overlay.overlay-left {
    right: auto;
  }
  .overlay.overlay-right {
    left: auto;
  }
  .overlay.overlay-top {
    bottom: auto;
  }
}

.mirrored {
  transform: scaleX(-1);
}

// .overlay-background {
//   z-index: -1;
// }

</style>
