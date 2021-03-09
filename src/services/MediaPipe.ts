/* eslint-disable @typescript-eslint/no-var-requires */
/* eslint-disable @typescript-eslint/no-explicit-any */
/* eslint-disable import/prefer-default-export */
const mp = require('@mediapipe/holistic/holistic');
const camUtils = require('@mediapipe/camera_utils/camera_utils');

export type Landmark = {
  x: number,
  y: number,
  visibility: number
}

export type PoseLandmarks = Array<Landmark>;

export const Landmarks = {
  nose: 0,
  left_eye_inner: 1,
  left_eye: 2,
  left_eye_outer: 3,
  right_eye_inner: 4,
  right_eye: 5,
  right_eye_outer: 6,
  left_ear: 7,
  right_ear: 8,
  mouth_left: 9,
  mouth_right: 10,
  left_shoulder: 11,
  right_shoulder: 12,
  left_elbow: 13,
  right_elbow: 14,
  left_wrist: 15,
  right_wrist: 16,
  left_pinky: 17,
  right_pinky: 18,
  left_index: 19,
  right_index: 20,
  left_thumb: 21,
  right_thumb: 22,
  left_hip: 23,
  right_hip: 24,
  left_knee: 25,
  right_knee: 26,
  left_ankle: 27,
  right_ankle: 28,
  left_heel: 29,
  right_heel: 30,
  left_foot_index: 31,
  right_foot_index: 32
}

const CONNECTIONS_TO_DRAW = [
  [Landmarks.left_index, Landmarks.left_wrist],
  [Landmarks.right_index, Landmarks.right_wrist],
  [Landmarks.left_wrist, Landmarks.left_elbow],
  [Landmarks.right_wrist, Landmarks.right_elbow],
  [Landmarks.left_elbow, Landmarks.left_shoulder],
  [Landmarks.right_elbow, Landmarks.right_shoulder],
  [Landmarks.left_shoulder, Landmarks.right_shoulder],
  [Landmarks.left_hip, Landmarks.left_shoulder],
  [Landmarks.right_hip, Landmarks.right_shoulder],
  [Landmarks.left_hip, Landmarks.right_hip],
  [Landmarks.left_hip, Landmarks.left_knee],
  [Landmarks.right_hip, Landmarks.right_knee],
  [Landmarks.left_knee, Landmarks.left_ankle],
  [Landmarks.right_knee, Landmarks.right_ankle],
  [Landmarks.left_ankle, Landmarks.left_heel],
  [Landmarks.right_ankle, Landmarks.right_heel],
  [Landmarks.left_heel, Landmarks.left_foot_index],
  [Landmarks.right_heel, Landmarks.right_foot_index],
  [Landmarks.left_ankle, Landmarks.left_foot_index],
  [Landmarks.right_ankle, Landmarks.right_foot_index],
  [Landmarks.nose, Landmarks.right_eye],
  [Landmarks.nose, Landmarks.left_eye]
];

let camera: any;

let videoElement: undefined | HTMLVideoElement;
let canvasElement: undefined | HTMLCanvasElement;

let trackingStarted = false;


export function GetCanvas() {
  return canvasElement;
}

export function GetVideo() {
  return videoElement;
}

export function DrawPose(canvasCtx: CanvasRenderingContext2D, poseLandmarks: PoseLandmarks) {
  console.log("Drawing overlay");
  canvasCtx.save();
  const w = canvasCtx.canvas.width;
  const h = canvasCtx.canvas.height;

  canvasCtx.strokeStyle = 'green';
  canvasCtx.lineWidth = 2;

  canvasCtx.beginPath();
  for (const connection of CONNECTIONS_TO_DRAW) {
    const p1 = poseLandmarks[connection[0]];
    const p2 = poseLandmarks[connection[1]];

    if (!p1 || !p2) continue;

    canvasCtx.moveTo(p1.x * w, p1.y * h);
    canvasCtx.lineTo(p2.x * w, p2.y * h);
  }

  const p1a = poseLandmarks[Landmarks.left_shoulder]
  const p1b = poseLandmarks[Landmarks.right_shoulder]
  const p2 = poseLandmarks[Landmarks.nose]
  canvasCtx.moveTo(w * 0.5 * (p1a.x + p1b.x), h * 0.5 * (p1a.y + p1b.y))
  canvasCtx.lineTo(w * p2.x, h * p2.y);
  canvasCtx.stroke()

  canvasCtx.restore();
};

export const StartTracking = function (videoElement: HTMLVideoElement, canvasElement: HTMLCanvasElement, onResults: (res: any, canvasCtx: CanvasRenderingContext2D) => void) {
  if (trackingStarted) { return; }

  trackingStarted = true;

  const renderingCtx = canvasElement.getContext('2d');

  const holistic = new mp.Holistic({ locateFile: (file: any) => `https://cdn.jsdelivr.net/npm/@mediapipe/holistic@0.1/${file}` });
  holistic.onResults((res: any) => {
    onResults(res, renderingCtx!)
  });

  camera = new camUtils.Camera(
    videoElement,
    {
      onFrame: async () => {
        await holistic.send({ image: videoElement })
      },
      width: 1280,
      height: 720,
    },
  );
  camera.start();
};
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
