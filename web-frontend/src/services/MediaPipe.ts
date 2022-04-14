/* eslint-disable no-multi-spaces */
/* eslint-disable @typescript-eslint/no-var-requires */
/* eslint-disable @typescript-eslint/no-explicit-any */
/* eslint-disable import/prefer-default-export */
import { delay } from '@azure/core-http';
import { Holistic } from '@mediapipe/holistic';
import { Pose } from '@mediapipe/pose';
import { Landmark, MpHolisticResults, PoseLandmarks } from './MediaPipeTypes';
import eventHub, { EventNames, TrackingActions } from './EventHub';
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
  // { v0: PoseLandmarks.leftHip,      v1: PoseLandmarks.leftShoulder,   size: 1.7 },
  // { v0: PoseLandmarks.rightHip,     v1: PoseLandmarks.rightShoulder,  size: 1.7 },
  { v0: PoseLandmarks.midShouder,   v1: PoseLandmarks.midHip,           size: 3.0 },
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

  // { v0: PoseLandmarks.leftEye,      v1: PoseLandmarks.rightEye,       size: 2.0 },
  // { v0: PoseLandmarks.nose,         v1: PoseLandmarks.leftEye,        size: 1.0 },

  { v0: PoseLandmarks.leftEar,       v1: PoseLandmarks.leftEyeOuter,  size: 1.0 },
  { v0: PoseLandmarks.leftEyeOuter,  v1: PoseLandmarks.rightEyeOuter, size: 1.0 },
  { v0: PoseLandmarks.rightEyeOuter, v1: PoseLandmarks.rightEar,      size: 1.0 },
  { v0: PoseLandmarks.rightEar,      v1: PoseLandmarks.mouthRight,    size: 1.0 },
  { v0: PoseLandmarks.mouthRight,    v1: PoseLandmarks.mouthLeft,     size: 1.0 },
  { v0: PoseLandmarks.mouthLeft,     v1: PoseLandmarks.leftEar,       size: 1.0 },
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

function MidLandmark(lm1: Landmark, lm2: Landmark): Landmark {
  return {
    x: (lm1.x + lm2.x) / 2,
    y: (lm1.y + lm2.y) / 2,
    visibility: ((lm1.visibility ?? 1) + (lm2.visibility ?? 1)) / 2,
  };
}

function GetLandmark(lm: number, lms: Array<Landmark>) {
  if (lm >= 0) return lms[lm];

  if (lm === PoseLandmarks.midHip) {
    return MidLandmark(lms[PoseLandmarks.leftHip], lms[PoseLandmarks.rightHip]);
  }

  if (lm === PoseLandmarks.midShouder) {
    return MidLandmark(lms[PoseLandmarks.leftShoulder], lms[PoseLandmarks.rightShoulder]);
  }

  if (lm === PoseLandmarks.midEye) {
    return MidLandmark(lms[PoseLandmarks.leftEye], lms[PoseLandmarks.rightEye]);
  }

  return undefined;
}

function DrawSkeleton(
  canvasCtx: CanvasRenderingContext2D,
  width: number,
  height: number,
  poseLandmarks: Landmark[],
  enableSizeVariation: boolean,
  emphasizedJoints: number[],
  emphasisStroke?: string,
) {
  const w = width;
  const h = height;

  CONNECTIONS_TO_DRAW.forEach((connection) => {
    const  p1 = GetLandmark(connection.v0, poseLandmarks);
    const  p2 = GetLandmark(connection.v1, poseLandmarks);

    if (!p1 || !p2) return;
    if ((p1.visibility ?? 1) < 0.25 || (p2.visibility ?? 1) < 0.25) {
      // console.log('skipping b/c of insufficient visibility');
      return;
    }

    const emphasized = emphasizedJoints
    && emphasizedJoints.indexOf(connection.v0) !== -1
    && emphasizedJoints.indexOf(connection.v1) !== -1;

    canvasCtx.save();
    if (emphasized && emphasisStroke) {
      canvasCtx.strokeStyle = emphasisStroke;
    }
    if (enableSizeVariation) {
      canvasCtx.lineWidth *= connection.size;
    }
    canvasCtx.beginPath();
    canvasCtx.moveTo(p1.x * w, p1.y * h);
    canvasCtx.lineTo(p2.x * w, p2.y * h);
    canvasCtx.stroke();
    canvasCtx.restore();
  });
}

export function DrawPose(
  canvasCtx: CanvasRenderingContext2D,
  poseLandmarks: Landmark[],
  options?: {
    sourceAspectRatio?: number;
    emphasizedJoints?: number[];
    emphasisStroke? : string;
    enableSizeVariation?: boolean;
    outlineColor?: string;
  },
) {

  if (poseLandmarks.length === 0) {
    return;
  }

  const jointsWithEmphasis = options?.emphasizedJoints ?? [];
  const enableSizeVariation = options?.enableSizeVariation ?? false;

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

  if (options?.outlineColor) {
    canvasCtx.save();
    canvasCtx.strokeStyle = options.outlineColor;
    const outlineWidth = Math.max(1, canvasCtx.lineWidth / 10.0);
    canvasCtx.lineWidth += outlineWidth * 2;
    DrawSkeleton(canvasCtx, w, h, poseLandmarks, enableSizeVariation, jointsWithEmphasis);
    canvasCtx.restore();
  }
  DrawSkeleton(canvasCtx, w, h, poseLandmarks, enableSizeVariation, jointsWithEmphasis, options?.emphasisStroke);

  // const p1a = poseLandmarks[PoseLandmarks.leftShoulder];
  // const p1b = poseLandmarks[PoseLandmarks.rightShoulder];
  // const p2 = poseLandmarks[PoseLandmarks.nose];
  // if (!p1a || !p1b || !p2) {
  //   canvasCtx.beginPath();
  //   canvasCtx.moveTo(w * 0.5 * (p1a.x + p1b.x), h * 0.5 * (p1a.y + p1b.y));
  //   canvasCtx.lineTo(w * p2.x, h * p2.y);
  //   canvasCtx.stroke();
  // }

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

export async function StartTracking(videoE: HTMLVideoElement) {
  if (trackingStarted) { throw Error('Tracking alread started'); }

  trackingStarted = true;
  trackingRequests.initial = true;

  let mpInstance: any = null;
  if (usingHolistic) mpInstance = new mp.Holistic({ locateFile: (file: any) => `https://cdn.jsdelivr.net/npm/@mediapipe/holistic@0.5.1635989137/${file}` });
  else mpInstance = new mp.Pose({ locateFile: (file: any) => `https://cdn.jsdelivr.net/npm/@mediapipe/pose@0.5.1635988162/${file}` });

  mpInstance.setOptions({
    upperBodyOnly: false,
    smoothLandmarks: true,
    minDetectionConfidence: 0.5,
    minTrackingConfidence: 0.5,
  });

  console.log('Creating tracking promise');

  return new Promise<void>((resolve) => {
    let frameId = 0;
    let timestamp = Date.now();
    let sendSrcTime = 0;
    mpInstance.onResults((res: MpHolisticResults) => {
      trackingRequests.initial = false;
      latestResults = res;
      res.timestamp = timestamp;
      eventHub.emit(EventNames.trackingResults, res, frameId);
      resolve();
    });

    eventHub.on(EventNames.trackingRequested, (id: string) => {
      trackingRequests[id] = true;
    });
    eventHub.on(EventNames.trackingRequestFinished, (id: string) => {
      trackingRequests[id] = false;
    });

    console.log('Creating tracking promise');
    Utils.DoEveryFrame(
      async () => {
        if (videoE.currentTime === sendSrcTime) {
          // Ensure that we don't send the same frame twice
          return;
        }

        frameId += 1;
        eventHub.emit(EventNames.trackingProcessingStarted, frameId);
        timestamp = Date.now();
        sendSrcTime = videoE.currentTime;
        if (trackingCount() > 0) await mpInstance.send({ image: videoE });
      },
      () => true,
    );
  });
}

export function isTracking() {
  return trackingCount() > 0;
}

// https://stackoverflow.com/questions/32699721/javascript-extract-video-frames-reliably
async function extractFramesFromVideo(videoUrl: string, startTime?: number, endTime?: number, fps = 25, onFrame?: (index: number, dataUrl: string) => void): Promise<number> {

  // eslint-disable-next-line no-async-promise-executor
  return new Promise(async (resolve) => {

    // fully download it first (no buffering):
    const videoBlob = await fetch(videoUrl).then((r) => r.blob());
    const videoObjectUrl = URL.createObjectURL(videoBlob);
    const video = document.createElement('video');

    let seekResolve: any;
    video.addEventListener('seeked', async () => {
      if (seekResolve) seekResolve();
    });

    video.src = videoObjectUrl;

    // workaround chromium metadata bug (https://stackoverflow.com/q/38062864/993683)
    while ((video.duration === Infinity || Number.isNaN(video.duration)) && video.readyState < 2) {
      // eslint-disable-next-line no-await-in-loop
      await new Promise((r) => setTimeout(r, 1000));
      video.currentTime = 10000000 * Math.random();
    }
    const { duration } = video;

    const canvas = document.createElement('canvas');

    // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
    const context = canvas.getContext('2d')!;
    const [w, h] = [video.videoWidth, video.videoHeight];
    canvas.width =  w;
    canvas.height = h;

    let frameCount = 0;
    const interval = 1 / fps;
    let currentTime = startTime ?? 0;

    while (currentTime < (endTime ?? duration)) {
      video.currentTime = currentTime;
      // eslint-disable-next-line no-await-in-loop, no-loop-func
      await new Promise((r) => { seekResolve = r; });

      context.drawImage(video, 0, 0, w, h);
      const base64ImageData = canvas.toDataURL();
      if (onFrame) onFrame(frameCount, base64ImageData);
      frameCount += 1;
      console.log(`Got frame ${frameCount}`);

      currentTime += interval;
    }
    resolve(frameCount);
  });
}

export async function processVideoElement(videoObjectURL: string, startTime: number, endTime: number) {
  console.log(`processVideoElement :: Processing video element from ${startTime} to ${endTime}`);

  let mediapipe: Pose | Holistic;
  if (usingHolistic) mediapipe = new mp.Holistic({ locateFile: (file: any) => `https://cdn.jsdelivr.net/npm/@mediapipe/holistic@0.5.1635989137/${file}` });
  else mediapipe = new mp.Pose({ locateFile: (file: any) => `https://cdn.jsdelivr.net/npm/@mediapipe/pose@0.5.1635988162/${file}` });

  mediapipe.setOptions({
    modelComplexity: 0,
    smoothLandmarks: true,
    enableSegmentation: false,
  });

  await mediapipe.initialize();

  console.log('Mediapipe initialized');

  const imageTestE = document.createElement('img');
  imageTestE.style.visibility = 'hidden';
  const results: Array<MpHolisticResults> = [];

  mediapipe.onResults((mpResults: MpHolisticResults) => {
    console.log(`Got mp results ${results.length}`);
    results.push(mpResults);
  });

  const frameQueue: Array<string> = [];
  const allFramesPromise = extractFramesFromVideo(
    videoObjectURL,
    startTime,
    endTime,
    30.0,
    // onFrame:
    (index, dataUrl) => {
      frameQueue.push(dataUrl);
    },
  );

  let allFramesExtracted = false;
  let countExtractedFrames = -1;

  Utils.DoEveryFrame(
    async () => {
      if (frameQueue.length === 0) {
        await new Promise((r) => setTimeout(r, 100));
        return;
      }

      const frame = frameQueue[0];
      // eslint-disable-next-line prefer-destructuring
      if (imageTestE.src !== frame) imageTestE.src = frame;
      if (!imageTestE.complete) return;
      console.log(`Mediapipe processing frame ${results.length}`);

      await mediapipe.send(imageTestE as any);

      frameQueue.splice(0, 1);
    },
    undefined,
    () => allFramesExtracted === true && countExtractedFrames === results.length,
  );

  countExtractedFrames = await allFramesPromise;
  allFramesExtracted = true;

  while (countExtractedFrames !== results.length) {
    // eslint-disable-next-line no-await-in-loop
    await new Promise((r) => setTimeout(r, 500));
    console.log(`Waiting for ${countExtractedFrames - results.length} frames to process`);
  }

  await mediapipe.close();

  return results;

  // srcVideoE.oncanplay = async () => {
  //   startTime = Math.min(Math.abs(startTime), srcVideoE.duration);
  //   endTime = Math.min(Math.abs(endTime), srcVideoE.duration);
  // };

  // srcVideoE.onseeked = async () => {

  // };

  // srcVideoE.src = videoObjectURL;

  // await mediapipe.close();

  // startTime = Math.min(e.duration, Math.abs(startTime));
  // endTime = Math.min(e.duration, Math.abs(endTime));

  // if (!isTracking()) {
  //   await StartTracking(e);
  // }

  // const trackInfo = [];

  // console.log('processVideoElement :: Tracking started; moving time along');

  // TrackingActions.requestTracking('videoProcessing');

  // e.currentTime = startTime;
  // while (e.currentTime < endTime) {

  //   e.currentTime += 1 / 30.0;
  //   delay(100);
  //   trackInfo.push(GetLatestResults());

  // }

  // TrackingActions.endTrackingRequest('videoProcessing');
}
