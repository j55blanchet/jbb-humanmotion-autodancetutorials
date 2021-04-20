/* eslint-disable @typescript-eslint/no-var-requires */
/* eslint-disable @typescript-eslint/no-explicit-any */
/* eslint-disable import/prefer-default-export */
import { Landmark, MpHolisticResults, PoseLandmarks } from './MediaPipeTypes';
import eventHub, { EventNames } from './EventHub';
import Utils from './Utils';

export const usingHolistic = false;

let mp: any = null;
// eslint-disable-next-line global-require
if (usingHolistic) mp = require('@mediapipe/holistic/holistic');
// eslint-disable-next-line global-require
else mp = require('@mediapipe/pose/pose');

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
  [PoseLandmarks.leftWrist, PoseLandmarks.leftPinky],
  [PoseLandmarks.rightWrist, PoseLandmarks.rightPinky],
  [PoseLandmarks.leftWrist, PoseLandmarks.leftThumb],
  [PoseLandmarks.rightWrist, PoseLandmarks.rightThumb],
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

export function DrawPose(canvasCtx: CanvasRenderingContext2D, poseLandmarks: Array<Landmark>, sourceAR?: number) {

  if (poseLandmarks.length === 0) {
    return;
  }

  canvasCtx.save();
  let w = canvasCtx.canvas.width;
  let h = canvasCtx.canvas.height;

  if (sourceAR) {
    const canvasAR = canvasCtx.canvas.width / canvasCtx.canvas.height;

    if (sourceAR > canvasAR) {
      // video source is wider than canvas
      const adjustedHeight = w / sourceAR;
      const pixelsTaller = h - adjustedHeight;
      canvasCtx.translate(0, pixelsTaller / 2);
      h = adjustedHeight;

    } else if (sourceAR < canvasAR) {
      // video source is taller than canvas
      const adjustedWidth = sourceAR * h;
      const pixelsWider = w - adjustedWidth;
      canvasCtx.translate(pixelsWider / 2, 0);
      w = adjustedWidth;
    }
  }

  canvasCtx.beginPath();
  CONNECTIONS_TO_DRAW.forEach((connection) => {
    const p1 = poseLandmarks[connection[0]];
    const p2 = poseLandmarks[connection[1]];

    if (!p1 || !p2) return;
    if ((p1.visibility ?? 1) < 0.5 || (p2.visibility ?? 1) < 0.5) {
      // console.log('skipping b/c of insufficient visibility');
      return;
    }

    canvasCtx.moveTo(p1.x * w, p1.y * h);
    canvasCtx.lineTo(p2.x * w, p2.y * h);
    // console.log(`draw from ${connection[0]} to ${connection[1]}`);
  });

  const p1a = poseLandmarks[PoseLandmarks.leftShoulder];
  const p1b = poseLandmarks[PoseLandmarks.rightShoulder];
  const p2 = poseLandmarks[PoseLandmarks.nose];
  if (!p1a || !p1b || !p2) {
    canvasCtx.moveTo(w * 0.5 * (p1a.x + p1b.x), h * 0.5 * (p1a.y + p1b.y));
    canvasCtx.lineTo(w * p2.x, h * p2.y);
  }

  canvasCtx.stroke();

  canvasCtx.restore();
}

const trackingRequests: Record<string, boolean> = {};
const trackingCount = () => Object
  .keys(trackingRequests)
  .map((id) => trackingRequests[id])
  .filter((x) => x).length;

let latestResults: MpHolisticResults | null = null;
export function GetLatestResults() {
  return Object.freeze(latestResults);
}

export function StartTracking(videoE: HTMLVideoElement): void {
  if (trackingStarted) { throw Error('Tracking alread started'); }

  trackingStarted = true;
  trackingRequests.initial = true;

  let mpInstance: any = null;
  if (usingHolistic) mpInstance = new mp.Holistic({ locateFile: (file: any) => `https://cdn.jsdelivr.net/npm/@mediapipe/holistic/${file}` });
  else mpInstance = new mp.Pose({ locateFile: (file: any) => `https://cdn.jsdelivr.net/npm/@mediapipe/pose/${file}` });

  mpInstance.setOptions({
    upperBodyOnly: false,
    smoothLandmarks: true,
    minDetectionConfidence: 0.5,
    minTrackingConfidence: 0.5,
  });

  let frameId = 0;
  mpInstance.onResults((res: MpHolisticResults) => {
    trackingRequests.initial = false;
    latestResults = res;
    eventHub.emit(EventNames.trackingResults, res, frameId);
  });

  eventHub.on(EventNames.trackingRequested, (id: string) => {
    trackingRequests[id] = true;
  });
  eventHub.on(EventNames.trackingRequestFinished, (id: string) => {
    trackingRequests[id] = false;
  });

  Utils.DoEveryFrame(
    async () => {
      frameId += 1;
      eventHub.emit(EventNames.trackingProcessingStarted, frameId);
      if (trackingCount() > 0) await mpInstance.send({ image: videoE });
    },
    () => true,
  );
}

export function isTracking() {
  return trackingCount() > 0;
}
