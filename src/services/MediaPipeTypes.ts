// Inspired from https://gist.github.com/TheJLifeX/74958cc59db477a91837244ff598ef4a

export type Landmark = {
  x: number;
  y: number;
  z?: number;
  visibility?: number;
}

export type MpHolisticResults = {
  image?: any;
  timestamp?: number;
  faceLandmarks?: Array<Landmark>;
  poseLandmarks?: Array<Landmark>;
  rightHandLandmarks?: Array<Landmark>;
  leftHandLandmarks?: Array<Landmark>;
}
export const HandLandmarks = {
  wrist: 0,
  thumbCMC: 1,
  thumbMCP: 2,
  thumbIP: 3,
  thumbTIP: 4,
  indexMCP: 5,
  indexPIP: 6,
  indexDIP: 7,
  indexTIP: 8,
  middleMCP: 9,
  middlePIP: 10,
  middleDIP: 11,
  middleTIP: 12,
  ringMCP: 13,
  ringPIP: 14,
  ringDIP: 15,
  ringTIP: 16,
  pinkyMCP: 17,
  pinkyPIP: 18,
  pinkyDIP: 19,
  pinkyTIP: 20,
};

export const PoseLandmarks = {
  nose: 0,
  leftEyeInner: 1,
  leftEye: 2,
  leftEyeOuter: 3,
  rightEyeInner: 4,
  rightEye: 5,
  rightEyeOuter: 6,
  leftEar: 7,
  rightEar: 8,
  mouthLeft: 9,
  mouthRight: 10,
  leftShoulder: 11,
  rightShoulder: 12,
  leftElbow: 13,
  rightElbow: 14,
  leftWrist: 15,
  rightWrist: 16,
  leftPinky: 17,
  rightPinky: 18,
  leftIndex: 19,
  rightIndex: 20,
  leftThumb: 21,
  rightThumb: 22,
  leftHip: 23,
  rightHip: 24,
  leftKnee: 25,
  rightKnee: 26,
  leftAnkle: 27,
  rightAnkle: 28,
  leftHeel: 29,
  rightHeel: 30,
  leftFootIndex: 31,
  rightFootIndex: 32,
};
