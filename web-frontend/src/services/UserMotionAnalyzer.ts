import { Landmark, PoseLandmarks } from '@/services/MediaPipeTypes';

export type PoseSequence = Readonly<Array<
  Readonly<Array<
    Readonly<Landmark>
  >>
>>

// From qijia:
//  i used 8 points (i.e., 16, 14, 12, 11, 13, 15, 23 ,24)
//  to form 8 vectors (i.e., 16-14, 14-12, 12-11, 11-13, 13-15,
//                           11-23, 23-24, 24-12)
const ScoreVectors = Object.freeze([
  [PoseLandmarks.rightShoulder, PoseLandmarks.rightElbow],
  [PoseLandmarks.rightElbow, PoseLandmarks.rightWrist],
  [PoseLandmarks.rightShoulder, PoseLandmarks.leftShoulder],
  [PoseLandmarks.leftShoulder, PoseLandmarks.leftElbow],
  [PoseLandmarks.leftElbow, PoseLandmarks.leftWrist],
  [PoseLandmarks.leftShoulder, PoseLandmarks.leftHip],
  [PoseLandmarks.leftHip, PoseLandmarks.rightHip],
  [PoseLandmarks.rightHip, PoseLandmarks.rightShoulder],
]);

function VectorFromLandmarks(from: Landmark, to: Landmark) {
  return [to.x - from.x, to.y - from.y];
}

function NormalizedVectorFromLandmarks(from: Landmark, to: Landmark) {
  const [x, y] = VectorFromLandmarks(from, to);
  const length = Math.sqrt(x * x + y * y);
  return [x / length, y / length];
}

function ScoreBeat(
  userBeat: PoseSequence,
  targetBeat: PoseSequence,
): number {

  const seqLength = Math.min(userBeat.length, targetBeat.length);

  const scoresByVector = ScoreVectors.map((vector) => {
    const srcLandmark = vector[0];
    const destLandmark = vector[1];

    let score = 0;
    for (let frame = 0; frame < seqLength; frame++) {
      const userFrame = userBeat[frame];
      const targetFrame = targetBeat[frame];

      const userVector = NormalizedVectorFromLandmarks(userFrame[srcLandmark], userFrame[destLandmark]);
      const targetVector = NormalizedVectorFromLandmarks(targetFrame[srcLandmark], targetFrame[destLandmark]);

      const vectorDiff = [userVector[0] - targetVector[0], userVector[1] - targetVector[1]];
      const absVectorDiff = [Math.abs(vectorDiff[0]), Math.abs(vectorDiff[1])];
      const frameVectorError = absVectorDiff[0] + absVectorDiff[1];
      score += frameVectorError;
    }
    return score;
  });

  scoresByVector.map((score) => score / seqLength);

  const scoreSum = scoresByVector.reduce((a, b) => a + b, 0);
  const netScore = scoreSum / scoresByVector.length;
  return netScore;
}

export function ScoreUserMotion(
  userMotion: PoseSequence,
  targetMotion: PoseSequence,
  fps: number,
  bpm: number,
): number {

  const framesPerBeat = (fps * 60) / bpm;
  const beatCount = Math.floor(userMotion.length / framesPerBeat);
  const scoresByBeat = [];

  for (let beat = 0; beat < beatCount; beat++) {
    const beatStart = beat * framesPerBeat;
    const beatEnd = beatStart + framesPerBeat;
    const userBeat = userMotion.slice(beatStart, beatEnd);
    const targetBeat = targetMotion.slice(beatStart, beatEnd);

    const score = ScoreBeat(userBeat, targetBeat);
    scoresByBeat.push(score);
  }

  const meanScore = scoresByBeat.reduce((a, b) => a + b, 0) / scoresByBeat.length;
  return meanScore;
}
