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
  if (!enabled) return;

  const sourceAR = (results.image?.width ?? WEBCAM_DIMENSIONS.width) /
                   (results.image?.height ?? WEBCAM_DIMENSIONS.height);


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
    const mpResults = ref({} as MpHolisticResults);

    setupGestureListening({},
      (ges, trackingResults) => {
        gesture.value = ges;
        mpResults.value = trackingResults;
        // console.log('Drawing surface: recvived tracking results', ges, trackingResults);
      });

    onMounted(() => {
      const canvas = canvasE.value;
      const canvasCtx = canvas.getContext('2d') as CanvasRenderingContext2D;

      canvasCtx.strokeStyle = 'rgba(200, 250, 200, 0.75)';
      canvasCtx.lineWidth = 6;
      canvasCtx.lineCap = 'round';
    });

    watch([enableDrawing, mpResults, gesture], (newVals) => {
      const canvas = canvasE.value;
      const canvasCtx = canvas.getContext('2d') as CanvasRenderingContext2D;

      canvasCtx.clearRect(0, 0, canvas.width, canvas.height);

      const isEnabled = newVals[0];
      const holisticResults = newVals[1];
      const detectedGesture = newVals[2];

      drawTrackingResults(
        isEnabled as unknown as boolean,
        detectedGesture as unknown as string,
        holisticResults as unknown as MpHolisticResults,
        canvasCtx,
      );
    });

    return {
      canvasE,
      gesture,
      mpResults,
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
