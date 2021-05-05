import { Landmark, MpHolisticResults, PoseLandmarks } from './MediaPipeTypes';
import eventHub, { EventNames, GestureNames } from './EventHub';
import {
  HAND, usingHolistic,
} from './MediaPipe';

const minDetectionVisibility = 0.85;

function getAngle(lm0: Landmark, lm1: Landmark) {
  return Math.atan2(lm1.y - lm0.y, lm1.x - lm0.x);
}
function dist(lm0: Landmark, lm1: Landmark) {
  return Math.sqrt((lm1.x - lm0.x) ** 2 + (lm1.y - lm0.y) ** 2);
}
const getSum = (input: Array<number>) => input.reduce((a, b) => a + b, 0);

function midPoint(lm0: Landmark, lm1: Landmark): Landmark {
  return {
    x: (0.5) * (lm0.x + lm1.x),
    y: (0.5) * (lm0.y + lm1.y),
  };
}

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

function detectHandPointingGestures(handLandmarks?: Landmark[]): string {
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

function detectPosePointingGestures(poseLandmarks?: Landmark[]): string {
  if (!poseLandmarks) return GestureNames.none;

  const TOLERANCE = 20;
  const TOLERANCE_RADS = TOLERANCE / (180 * Math.PI);

  const left = [PoseLandmarks.leftElbow, PoseLandmarks.leftWrist].map((i) => poseLandmarks[i]);
  const lelb = left[0];
  const lwrist = left[1];
  if (lelb.visibility && lelb.visibility > minDetectionVisibility && lwrist.visibility && lwrist.visibility > minDetectionVisibility) {
    const ang = getAngle(lelb, lwrist);
    if (Math.abs(ang) > Math.PI - TOLERANCE_RADS) return GestureNames.pointRight;
  }

  const right = [PoseLandmarks.rightElbow, PoseLandmarks.rightWrist].map((i) => poseLandmarks[i]);
  const relb = right[0];
  const rwrist = right[1];
  if (relb.visibility && relb.visibility > minDetectionVisibility && rwrist.visibility && rwrist.visibility > minDetectionVisibility) {
    const ang = getAngle(relb, rwrist);
    if (Math.abs(ang) < TOLERANCE_RADS) return GestureNames.pointLeft;
  }

  return GestureNames.none;
}

function isNamasteGesture(results: MpHolisticResults): boolean {
  /* eslint-disable operator-linebreak, no-multi-spaces */
  const IDs = PoseLandmarks;
  const poseLMs = results.poseLandmarks;
  if (!poseLMs) return false;

  const areArmLandmarksVisible =
    (poseLMs[IDs.leftShoulder].visibility  ?? 0) > minDetectionVisibility &&
    (poseLMs[IDs.leftElbow].visibility     ?? 0) > minDetectionVisibility &&
    (poseLMs[IDs.leftWrist].visibility     ?? 0) > minDetectionVisibility &&
    (poseLMs[IDs.rightShoulder].visibility ?? 0) > minDetectionVisibility &&
    (poseLMs[IDs.rightElbow].visibility    ?? 0) > minDetectionVisibility &&
    (poseLMs[IDs.rightWrist].visibility    ?? 0) > minDetectionVisibility;

  // See if elbows are down, against the stomach
  const downwards = -Math.PI / 2; // -90 deg
  const leftForearmTargetAngle = downwards;
  const rightForearmTargetAngle = downwards;
  const elbowAngleTolerance = Math.PI / 9; // 20 deg

  const leftForearmAngle = getAngle(poseLMs[IDs.leftShoulder], poseLMs[IDs.leftElbow]);
  const rightForearmAngle = getAngle(poseLMs[IDs.rightShoulder], poseLMs[IDs.rightElbow]);

  const areElbowsNearChest =
    Math.abs(leftForearmAngle - leftForearmTargetAngle) < elbowAngleTolerance / 2 &&
    Math.abs(rightForearmAngle - rightForearmTargetAngle) < elbowAngleTolerance / 2;

  // See if hands are up and together, near base of neck
  const handNeckMinRelativeDist = 0.8;
  const shoulderDist = dist(poseLMs[IDs.leftShoulder], poseLMs[IDs.rightShoulder]);
  const neckCenter = midPoint(poseLMs[IDs.leftShoulder], poseLMs[IDs.rightShoulder]);
  const leftWristNeckDist = dist(neckCenter, poseLMs[IDs.leftWrist]) / shoulderDist;
  const rightWristNeckDist = dist(neckCenter, poseLMs[IDs.rightWrist]) / shoulderDist;

  const areHandsNearNeckBase =
    leftWristNeckDist  < handNeckMinRelativeDist &&
    rightWristNeckDist < handNeckMinRelativeDist;

  // console.log('areArmLandmarksVisible', areArmLandmarksVisible);
  // console.log('areElbowsNearChest', areElbowsNearChest);
  // console.log('areHandsNearNeckBase', areHandsNearNeckBase);
  // console.log('  leftWristNeckDist', leftWristNeckDist);
  // console.log('  rightWristNeckDist', rightWristNeckDist);
  return areArmLandmarksVisible &&
        //  areElbowsNearChest &&
         areHandsNearNeckBase;

  /* eslint-enable operator-linebreak, no-multi-spaces */
}

export default function detectGesture(mpResults?: MpHolisticResults): string {
  if (!mpResults) return GestureNames.none;
  let detectedGesture = GestureNames.none;

  if (usingHolistic) {
    if (detectedGesture === GestureNames.none) detectedGesture = detectHandPointingGestures(mpResults.rightHandLandmarks);
    if (detectedGesture === GestureNames.none) detectedGesture = detectHandPointingGestures(mpResults.leftHandLandmarks);
  } else detectedGesture = detectPosePointingGestures(mpResults.poseLandmarks);

  if (detectedGesture === GestureNames.none && isNamasteGesture(mpResults)) {
    detectedGesture = GestureNames.namaste;
  }

  return detectedGesture;
}

export function startGestureDetection() {
  eventHub.on(EventNames.trackingResults, (results: MpHolisticResults) => {
    const detectedGesture = detectGesture(results);
    eventHub.emit(EventNames.gesture, detectedGesture, results);
  });
}
