/* eslint-disable @typescript-eslint/no-var-requires */
/* eslint-disable @typescript-eslint/no-explicit-any */
/* eslint-disable import/prefer-default-export */
import { Landmark, PoseLandmarks } from './MediaPipeTypes';
import eventHub, { EventNames } from './EventHub';

const mp = require('@mediapipe/holistic/holistic');
const camUtils = require('@mediapipe/camera_utils/camera_utils');

export const HAND_LANDMARK_CONNECTIONS = [
  [0, 1], [1, 2], [2, 3], [3, 4], // Thumb
  [0, 5], [5, 6], [6, 7], [7, 8], // Index
  [5, 9], [9, 10], [10, 11], [11, 12], // Middle
  [9, 13], [13, 14], [14, 15], [15, 16], // Ring
  [0, 17], [13, 17], [17, 18], [18, 19], [19, 20], // Pinky
];

export const HAND = {
  THUMB_FINGER: [1, 2, 3, 4],
  INDEX_FINGER: [5, 6, 7, 8],
  MIDDLE_FINGER: [9, 10, 11, 12],
  RING_FINGER: [13, 14, 15, 16],
  PINKY_FINGER: [17, 18, 19, 20],
};

const CONNECTIONS_TO_DRAW = [
  [PoseLandmarks.leftIndex, PoseLandmarks.leftWrist],
  [PoseLandmarks.rightIndex, PoseLandmarks.rightWrist],
  [PoseLandmarks.leftWrist, PoseLandmarks.leftElbow],
  [PoseLandmarks.rightWrist, PoseLandmarks.rightElbow],
  [PoseLandmarks.leftElbow, PoseLandmarks.leftShoulder],
  [PoseLandmarks.rightElbow, PoseLandmarks.rightShoulder],
  [PoseLandmarks.leftShoulder, PoseLandmarks.rightShoulder],
  [PoseLandmarks.leftHip, PoseLandmarks.leftShoulder],
  [PoseLandmarks.rightHip, PoseLandmarks.rightShoulder],
  [PoseLandmarks.leftHip, PoseLandmarks.rightHip],
  [PoseLandmarks.leftHip, PoseLandmarks.leftKnee],
  [PoseLandmarks.rightHip, PoseLandmarks.rightKnee],
  [PoseLandmarks.leftKnee, PoseLandmarks.leftAnkle],
  [PoseLandmarks.rightKnee, PoseLandmarks.rightAnkle],
  [PoseLandmarks.leftAnkle, PoseLandmarks.leftHeel],
  [PoseLandmarks.rightAnkle, PoseLandmarks.rightHeel],
  [PoseLandmarks.leftHeel, PoseLandmarks.leftFootIndex],
  [PoseLandmarks.rightHeel, PoseLandmarks.rightFootIndex],
  [PoseLandmarks.leftAnkle, PoseLandmarks.leftFootIndex],
  [PoseLandmarks.rightAnkle, PoseLandmarks.rightFootIndex],
  [PoseLandmarks.nose, PoseLandmarks.rightEye],
  [PoseLandmarks.nose, PoseLandmarks.leftEye],
];

let camera: any;
let trackingStarted = false;

export function DrawConnections(
  canvasCtx: CanvasRenderingContext2D,
  landmarks: Array<Landmark>,
  connections: Array<Array<number>>,
) {
  const w = canvasCtx.canvas.width;
  const h = canvasCtx.canvas.height;

  canvasCtx.beginPath();
  connections.forEach((connection) => {
    const p1 = landmarks[connection[0]];
    const p2 = landmarks[connection[1]];

    if (!p1 || !p2) return;

    canvasCtx.moveTo(p1.x * w, p1.y * h);
    canvasCtx.lineTo(p2.x * w, p2.y * h);
  });

  canvasCtx.stroke();
  canvasCtx.restore();
}

export function DrawPose(canvasCtx: CanvasRenderingContext2D, poseLandmarks: Array<Landmark>) {
  canvasCtx.save();
  const w = canvasCtx.canvas.width;
  const h = canvasCtx.canvas.height;

  /* eslint-disable no-param-reassign */
  canvasCtx.strokeStyle = 'green';
  canvasCtx.lineWidth = 2;
  /* eslint-enable no-param-reassign */

  canvasCtx.beginPath();
  CONNECTIONS_TO_DRAW.forEach((connection) => {
    const p1 = poseLandmarks[connection[0]];
    const p2 = poseLandmarks[connection[1]];

    if (!p1 || !p2) return;

    canvasCtx.moveTo(p1.x * w, p1.y * h);
    canvasCtx.lineTo(p2.x * w, p2.y * h);
  });

  const p1a = poseLandmarks[PoseLandmarks.leftShoulder];
  const p1b = poseLandmarks[PoseLandmarks.rightShoulder];
  const p2 = poseLandmarks[PoseLandmarks.nose];
  canvasCtx.moveTo(w * 0.5 * (p1a.x + p1b.x), h * 0.5 * (p1a.y + p1b.y));
  canvasCtx.lineTo(w * p2.x, h * p2.y);
  canvasCtx.stroke();

  canvasCtx.restore();
}

let trackingCount = 0;

export function StartTracking(
  videoE: HTMLVideoElement,
  canvasE: HTMLCanvasElement,
  onResults: (res: any, canvasCtx: CanvasRenderingContext2D) => void,
) {
  if (trackingStarted) { return; }

  trackingStarted = true;
  trackingCount += 1;

  const renderingCtx = canvasE.getContext('2d');

  const holistic = new mp.Holistic({ locateFile: (file: any) => `https://cdn.jsdelivr.net/npm/@mediapipe/holistic@0.1/${file}` });
  holistic.setOptions({
    upperBodyOnly: false,
    smoothLandmarks: true,
    minDetectionConfidence: 0.5,
    minTrackingConfidence: 0.5,
  });
  holistic.onResults((res: any) => {
    onResults(res, renderingCtx as CanvasRenderingContext2D);
    eventHub.emit(EventNames.trackingResultsAcquired, res);
  });

  eventHub.on(EventNames.trackingRequested, () => {
    trackingCount += 1;
  });
  eventHub.on(EventNames.trackingRequestFinished, () => {
    trackingCount -= 1;
  });

  camera = new camUtils.Camera(
    videoE,
    {
      onFrame: async () => {
        if (trackingCount > 0) await holistic.send({ image: videoE });
      },
      width: 1280,
      height: 720,
    },
  );
  camera.start();
}

export function isTracking() {
  return trackingCount > 0;
}
// function removeElements(landmarks, elements) {
//   for (const element of elements) {
//     delete landmarks[element];
//   }
// }

// function removeLandmarks(results) {
//   if (results.poseLandmarks) {
//     removeElements(
//       results.poseLandmarks,
//       [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 15, 16, 17, 18, 19, 20, 21, 22],
//     );
//   }
// }

// function connect(ctx: CanvasRenderingContext2D, connectors: Array<Array<number>>) {
//   const { canvas } = ctx;
//   for (const connector of connectors) {
//     const from = connector[0];
//     const to = connector[1];
//     if (from && to) {
//       if (from.visibility && to.visibility
//         && (from.visibility < 0.1 || to.visibility < 0.1)) {
//         continue;
//       }
//       ctx.beginPath();
//       ctx.moveTo(from.x * canvas.width, from.y * canvas.height);
//       ctx.lineTo(to.x * canvas.width, to.y * canvas.height);
//       ctx.stroke();
//     }
//   }
// }
