<template>
  <canvas ref="canvasE" width="1280" height="720" class="drawCanvas"></canvas>
</template>

<script lang="ts">

import {
  ref, defineComponent, watch, toRefs, onMounted, Ref,
} from 'vue';
import { WEBCAM_DIMENSIONS } from '@/services/WebcamProvider';
import { GestureNames, setupGestureListening } from '../services/EventHub';

import { MpHolisticResults } from '../services/MediaPipeTypes';
import {
  HAND_LANDMARK_CONNECTIONS, DrawConnections, DrawPose,
} from '../services/MediaPipe';

function drawHandShape(results: MpHolisticResults, canvasCtx: CanvasRenderingContext2D) {
  if (!results.rightHandLandmarks) {
    return;
  }

  canvasCtx.save();

  /* eslint-disable no-param-reassign */
  canvasCtx.strokeStyle = 'white';
  canvasCtx.lineWidth = 3.0;
  canvasCtx.lineCap = 'round';

  DrawConnections(canvasCtx, results.rightHandLandmarks, HAND_LANDMARK_CONNECTIONS);
  canvasCtx.restore();
}

function drawTrackingResults(
  enabled: boolean,
  detectedGesture: string,
  results: MpHolisticResults,
  canvasCtx: CanvasRenderingContext2D,
) {
  const { canvas } = canvasCtx;
  canvasCtx.clearRect(0, 0, canvas.width, canvas.height);

  if (!enabled) return;

  // console.log('Drawing tracking results', canvasCtx, canvas);
  const sourceAR = WEBCAM_DIMENSIONS.width / WEBCAM_DIMENSIONS.height;

  if (results.poseLandmarks) {
    DrawPose(canvasCtx, results.poseLandmarks, {
      sourceAspectRatio: sourceAR,
    });
  }
  if (detectedGesture !== GestureNames.none) drawHandShape(results, canvasCtx);
}

export default defineComponent({
  name: 'DrawingSurface',
  props: {
    enableDrawing: {
      type: Boolean,
      default: true,
    },
  },
  setup(props) {
    const { enableDrawing } = toRefs(props);

    const canvasE = ref(null) as unknown as Ref<HTMLCanvasElement>;
    const gesture = ref(GestureNames.none);
    const mpResults = ref(null as MpHolisticResults | null);

    setupGestureListening({},
      (ges, trackingResults) => {
        gesture.value = ges;
        mpResults.value = trackingResults;
      });

    onMounted(() => {
      const canvas = canvasE.value;
      const canvasCtx = canvas.getContext('2d') as CanvasRenderingContext2D;

      canvasCtx.strokeStyle = 'rgba(200, 250, 200, 0.75)';
      canvasCtx.lineWidth = 6;
      canvasCtx.lineCap = 'round';
    });

    watch([enableDrawing, mpResults, gesture], (isEnabledNow, results, ges) => {
      const canvas = canvasE.value;
      const canvasCtx = canvas.getContext('2d') as CanvasRenderingContext2D;

      // Temp, for testing
      canvasCtx.save();
      canvasCtx.fillStyle = isEnabledNow ? 'rgba(0, 255, 0, 0.5)' : 'rgba(255, 0, 0, 0.5)';
      canvasCtx.rect(0, 0, canvas.width, canvas.height);
      canvasCtx.restore();
      // drawTrackingResults(
        // isEnabledNow as unknown as boolean,
        // ges as unknown as string,
        // results as MpHolisticResults,
        // canvasCtx,
      // );
    });

    return {
      canvasE,
      gesture,
    };
  },
});
</script>

<style lang="scss">

$pointer-size: 64px;

.drawCanvas {
  transform: scaleX(-1);
  pointer-events: none;
}

.pointer-container {
  position: fixed;
  // transition: top .1s, left .1s;

  img {
    position: relative;
    left: -$pointer-size / 2;
    top: -32px;
    width: 64px;
    height: 64px;
  }
}

</style>
