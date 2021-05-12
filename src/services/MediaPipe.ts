/* eslint-disable no-multi-spaces */
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
  { v0: PoseLandmarks.leftWrist,    v1: PoseLandmarks.leftPinky,      size: 1.0 },
  { v0: PoseLandmarks.rightWrist,   v1: PoseLandmarks.rightPinky,     size: 1.0 },
  { v0: PoseLandmarks.leftWrist,    v1: PoseLandmarks.leftThumb,      size: 1.0 },
  { v0: PoseLandmarks.rightWrist,   v1: PoseLandmarks.rightThumb,     size: 1.0 },
  { v0: PoseLandmarks.leftIndex,    v1: PoseLandmarks.leftWrist,      size: 1.0 },
  { v0: PoseLandmarks.rightIndex,   v1: PoseLandmarks.rightWrist,     size: 1.0 },
  { v0: PoseLandmarks.leftWrist,    v1: PoseLandmarks.leftElbow,      size: 1.1 },
  { v0: PoseLandmarks.rightWrist,   v1: PoseLandmarks.rightElbow,     size: 1.1 },
  { v0: PoseLandmarks.leftElbow,    v1: PoseLandmarks.leftShoulder,   size: 1.3 },
  { v0: PoseLandmarks.rightElbow,   v1: PoseLandmarks.rightShoulder,  size: 1.3 },
  { v0: PoseLandmarks.leftShoulder, v1: PoseLandmarks.rightShoulder,  size: 2.0 },
  { v0: PoseLandmarks.leftHip,      v1: PoseLandmarks.leftShoulder,   size: 1.7 },
  { v0: PoseLandmarks.rightHip,     v1: PoseLandmarks.rightShoulder,  size: 1.7 },
  { v0: PoseLandmarks.leftHip,      v1: PoseLandmarks.rightHip,       size: 1.7 },
  { v0: PoseLandmarks.leftHip,      v1: PoseLandmarks.leftKnee,       size: 1.5 },
  { v0: PoseLandmarks.rightHip,     v1: PoseLandmarks.rightKnee,      size: 1.5 },
  { v0: PoseLandmarks.leftKnee,     v1: PoseLandmarks.leftAnkle,      size: 1.4 },
  { v0: PoseLandmarks.rightKnee,    v1: PoseLandmarks.rightAnkle,     size: 1.4 },
  { v0: PoseLandmarks.leftAnkle,    v1: PoseLandmarks.leftHeel,       size: 1.0 },
  { v0: PoseLandmarks.rightAnkle,   v1: PoseLandmarks.rightHeel,      size: 1.0 },
  { v0: PoseLandmarks.leftHeel,     v1: PoseLandmarks.leftFootIndex,  size: 1.0 },
  { v0: PoseLandmarks.rightHeel,    v1: PoseLandmarks.rightFootIndex, size: 1.0 },
  { v0: PoseLandmarks.leftAnkle,    v1: PoseLandmarks.leftFootIndex,  size: 1.0 },
  { v0: PoseLandmarks.rightAnkle,   v1: PoseLandmarks.rightFootIndex, size: 1.0 },
  { v0: PoseLandmarks.nose,         v1: PoseLandmarks.rightEye,       size: 1.0 },
  { v0: PoseLandmarks.nose,         v1: PoseLandmarks.leftEye,        size: 1.0 },
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

export function DrawPose(
  canvasCtx: CanvasRenderingContext2D,
  poseLandmarks: Landmark[],
  options?: {
    sourceAspectRatio?: number;
    emphasizedJoints?: number[];
    emphasisStroke? : string;
  },
) {

  if (poseLandmarks.length === 0) {
    return;
  }

  const jointsWithEmphasis = options?.emphasizedJoints;

  canvasCtx.save();
  let w = canvasCtx.canvas.width;
  let h = canvasCtx.canvas.height;

  const sourceAR = options?.sourceAspectRatio;
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

  CONNECTIONS_TO_DRAW.forEach((connection) => {
    const p1 = poseLandmarks[connection.v0];
    const p2 = poseLandmarks[connection.v1];

    if (!p1 || !p2) return;
    if ((p1.visibility ?? 1) < 0.5 || (p2.visibility ?? 1) < 0.5) {
      // console.log('skipping b/c of insufficient visibility');
      return;
    }

    const emphasized = jointsWithEmphasis
    && jointsWithEmphasis.indexOf(connection.v0) !== -1
    && jointsWithEmphasis.indexOf(connection.v1) !== -1;

    canvasCtx.save();
    if (emphasized && options?.emphasisStroke) {
      canvasCtx.strokeStyle = options.emphasisStroke;
    }
    canvasCtx.lineWidth *= connection.size;
    canvasCtx.beginPath();
    canvasCtx.moveTo(p1.x * w, p1.y * h);
    canvasCtx.lineTo(p2.x * w, p2.y * h);
    canvasCtx.stroke();
    canvasCtx.restore();
  });

  const p1a = poseLandmarks[PoseLandmarks.leftShoulder];
  const p1b = poseLandmarks[PoseLandmarks.rightShoulder];
  const p2 = poseLandmarks[PoseLandmarks.nose];
  if (!p1a || !p1b || !p2) {
    canvasCtx.beginPath();
    canvasCtx.moveTo(w * 0.5 * (p1a.x + p1b.x), h * 0.5 * (p1a.y + p1b.y));
    canvasCtx.lineTo(w * p2.x, h * p2.y);
    canvasCtx.stroke();
  }

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
  if (usingHolistic) mpInstance = new mp.Holistic({ locateFile: (file: any) => `https://cdn.jsdelivr.net/npm/@mediapipe/holistic@0.1.1613603339/${file}` });
  else mpInstance = new mp.Pose({ locateFile: (file: any) => `https://cdn.jsdelivr.net/npm/@mediapipe/pose@0.2.1617147663/${file}` });

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
