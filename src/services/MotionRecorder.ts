import { MpHolisticResults } from './MediaPipeTypes';
import Utils from './Utils';

export interface Dimensions {
  width: number;
  height: number;
}

interface RecordingSession {
  userDimension: Dimensions;
  userFrames: MpHolisticResults[];
  demoDimension: Dimensions;
  demoFrames: MpHolisticResults[];
}

export class MotionRecorder {

  private recordingSessions: Record<number, RecordingSession> = {};

  private recordingSessionNextId = 0;

  startRecordingSession(userDims: Dimensions, demoDims: Dimensions): number {
    this.recordingSessions[this.recordingSessionNextId] = {
      userDimension: userDims,
      userFrames: [],
      demoDimension: demoDims,
      demoFrames: [],
    };
    this.recordingSessionNextId += 1;
    return this.recordingSessionNextId - 1;
  }

  saveMotionFrame(sessionId: number, userFrame: MpHolisticResults, demoFrame: MpHolisticResults) {
    const session = this.recordingSessions[sessionId];
    if (!session) throw new Error(`Recording session ${sessionId} wasn't found!`);

    debugger;
    session.userFrames.push(userFrame);
    session.demoFrames.push(demoFrame);
  }

  endRecordingSession(sessionId: number) {
    const session = this.recordingSessions[sessionId];
    if (!session) throw new Error(`Recording session ${sessionId} wasn't found!`);

    Utils.PromptDownloadFile(`RecordedSession-${sessionId}.json`, JSON.stringify(session));
  }
}

const motionRecorder = new MotionRecorder();

export default motionRecorder;
