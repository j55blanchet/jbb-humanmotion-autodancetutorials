<template>
  <canvas ref="canvasE" width="1280" height="720" class="drawCanvas"></canvas>
</template>

<script lang="ts">

import {
  ref, defineComponent, watch, toRefs, onMounted, Ref,
} from 'vue';
import { WEBCAM_DIMENSIONS } from '@/services/WebcamProvider';
import eventHub, { GestureNames } from '../services/EventHub';

import { Landmark, MpHolisticResults, PoseLandmarks } from '../services/MediaPipeTypes';
import {
  HAND_LANDMARK_CONNECTIONS, DrawConnections, HAND, DrawPose, usingHolistic,
} from '../services/MediaPipe';

function getAngle(lm0: Landmark, lm1: Landmark) {
  return Math.atan2(lm1.y - lm0.y, lm1.x - lm0.x);
}

const getSum = (input: Array<number>) => input.reduce((a, b) => a + b, 0);

function averageAngle(input: Array<Landmark>): number {
  if (input.length < 2) return 0;

  const angles = input.map(
    (val, i, arr) => (arr[i + 1] === undefined ? 0 : getAngle(arr[i], arr[i + 1])),
  );
  angles.pop();

  const y = getSum(angles.map(Math.sin));
  const x = getSum(angles.map(Math.cos));

  return Math.atan2(y, x);
}

function isLine(input: Array<Landmark>, angleTolerance?: number): boolean {
  if (input.length < 2) { return false; } // Single point: not a line

  // Default the tolerance to 15 deg (on either side)
  const tolerance = angleTolerance ?? Math.PI / 12;
  let lastAngle = getAngle(input[0], input[1]);

  // Make sure the angle is about correct
  for (let i = 1; i < input.length - 1; i += 1) {
    const thisAngle = getAngle(input[i], input[i + 1]);
    if (Math.abs(thisAngle - lastAngle) >= tolerance) { return false; }

    lastAngle = thisAngle;
  }
  return true;
}

function detectHandGesture(handLandmarks?: Landmark[]): string {
  if (!handLandmarks) return GestureNames.none;

  const FINGERS = [
    HAND.INDEX_FINGER,
    HAND.MIDDLE_FINGER,
    HAND.RING_FINGER,
    HAND.PINKY_FINGER,
  ];

  const FINGER_LANDMARKS = FINGERS.map((indices) => indices.map((lm) => handLandmarks[lm]));

  let areLines = true;
  FINGER_LANDMARKS.forEach((finger) => {
    if (!isLine(finger)) areLines = false;
  });

  const avgAngle = averageAngle(FINGER_LANDMARKS[0]);
  const avgAngleDeg = (avgAngle * 180) / Math.PI;

  const tolerance = 30;
  if (Math.abs(avgAngleDeg) < tolerance && areLines) return GestureNames.pointLeft;
  if (Math.abs(avgAngleDeg) > 180 - tolerance && areLines) return GestureNames.pointRight;

  return GestureNames.none;
}

function detectPoseGesture(poseLandmarks?: Landmark[]): string {
  if (!poseLandmarks) return GestureNames.none;

  const TOLERANCE = 20;
  const TOLERANCE_RADS = TOLERANCE / (180 * Math.PI);

  const left = [PoseLandmarks.leftElbow, PoseLandmarks.leftWrist].map((i) => poseLandmarks[i]);
  const lelb = left[0];
  const lwrist = left[1];
  if (lelb.visibility && lelb.visibility > 0.95 && lwrist.visibility && lwrist.visibility > 0.95) {
    const ang = getAngle(lelb, lwrist);
    if (Math.abs(ang) > Math.PI - TOLERANCE_RADS) return GestureNames.pointRight;
  }

  const right = [PoseLandmarks.rightElbow, PoseLandmarks.rightWrist].map((i) => poseLandmarks[i]);
  const relb = right[0];
  const rwrist = right[1];
  if (relb.visibility && relb.visibility > 0.95 && rwrist.visibility && rwrist.visibility > 0.95) {
    const ang = getAngle(relb, rwrist);
    if (Math.abs(ang) < TOLERANCE_RADS) return GestureNames.pointLeft;
  }

  return GestureNames.none;
}

function getGesture(mpResults?: MpHolisticResults): string {
  if (!mpResults) return GestureNames.none;
  let detectedGesture = GestureNames.none;

  if (usingHolistic) {
    if (detectedGesture === GestureNames.none) detectedGesture = detectHandGesture(mpResults.rightHandLandmarks);
    if (detectedGesture === GestureNames.none) detectedGesture = detectHandGesture(mpResults.leftHandLandmarks);
  } else if (detectedGesture === GestureNames.none) detectedGesture = detectPoseGesture(mpResults.poseLandmarks);

  return detectedGesture;
}

function drawHandShape(results: MpHolisticResults, canvasCtx: CanvasRenderingContext2D) {
  if (!results.rightHandLandmarks) {
    return;
  }

  canvasCtx.save();

  /* eslint-disable no-param-reassign */
  canvasCtx.strokeStyle = 'white';
  canvasCtx.lineWidth = 3.0;

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

  canvasCtx.save();

  const sourceAR = WEBCAM_DIMENSIONS.width / WEBCAM_DIMENSIONS.height;

  if (results.poseLandmarks) DrawPose(canvasCtx, results.poseLandmarks, sourceAR);
  // if (detectedGesture !== GestureNames.none) drawHandShape(results, canvasCtx);

  canvasCtx.restore();
}

export default defineComponent({
  name: 'DrawingSurface',
  props: {
    mpResults: {
      type: Object,
      required: false,
    },
    enableDrawing: {
      type: Boolean,
      default: true,
    },
  },
  setup(props) {
    const { mpResults, enableDrawing } = toRefs(props);

    const gesture = ref('none');
    const canvasE = ref(null) as unknown as Ref<HTMLCanvasElement>;

    onMounted(() => {
      const canvas = canvasE.value;
      const canvasCtx = canvas.getContext('2d') as CanvasRenderingContext2D;

      canvasCtx.strokeStyle = 'rgba(200, 250, 200, 0.75)';
      canvasCtx.lineWidth = 6;

      watch(mpResults as unknown as Ref<MpHolisticResults>, (newVal) => {

        const detectedGesture = getGesture(newVal);

        drawTrackingResults(enableDrawing.value, detectedGesture, newVal, canvasCtx);
        gesture.value = detectedGesture;

        if (detectedGesture !== GestureNames.none) {
          eventHub.emit('gesture', detectedGesture);
        }
      });
    });

    watch(enableDrawing, (isEnabledNow) => {
      const canvas = canvasE.value;
      const canvasCtx = canvas.getContext('2d') as CanvasRenderingContext2D;
      drawTrackingResults(
        isEnabledNow,
        gesture.value,
        mpResults?.value as MpHolisticResults,
        canvasCtx,
      );
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
