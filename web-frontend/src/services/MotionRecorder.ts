import { MpHolisticResults } from './MediaPipeTypes';
import Utils from './Utils';
import { saveBlob } from './WebcamProvider';
import ScreenRecorder from './ScreenRecorder';

export interface Dimensions {
  width: number;
  height: number;
}

interface RecordingSession {
  frameTimestamps: number[];
  userDimension: Dimensions;
  userFrames: MpHolisticResults[];
  demoDimension: Dimensions;
  demoFrames: MpHolisticResults[];
}

export class MotionRecorder {

  private recordingSessions: Record<number, RecordingSession> = {};

  private recordingSessionNextId = 0;

  private screenRecorder = new ScreenRecorder();

  async startRecordingSession(userDims: Dimensions, demoDims: Dimensions): Promise<number> {
    this.recordingSessions[this.recordingSessionNextId] = {
      frameTimestamps: [],
      userDimension: userDims,
      userFrames: [],
      demoDimension: demoDims,
      demoFrames: [],
    };
    this.recordingSessionNextId += 1;

    await this.screenRecorder.startRecording();
    return this.recordingSessionNextId - 1;
  }

  saveMotionFrame(sessionId: number, timestamp: number, userFrame: MpHolisticResults, demoFrame: MpHolisticResults) {
    const session = this.recordingSessions[sessionId];
    if (!session) throw new Error(`Recording session ${sessionId} wasn't found!`);

    debugger;
    if (userFrame.image) delete userFrame.image;
    session.frameTimestamps.push(timestamp);
    session.userFrames.push(userFrame);
    session.demoFrames.push(demoFrame);
  }

  async endRecordingSession(sessionId: number, start: number, end: number) {
    const session = this.recordingSessions[sessionId];
    if (!session) throw new Error(`Recording session ${sessionId} wasn't found!`);

    const recordedBlob = await this.screenRecorder.endRecording();
    saveBlob(recordedBlob, 'recording.webm');

    const mSession = { startTime: start, endTime: end, ...session };

    Utils.PromptDownloadFile(`RecordedSession-${sessionId}.json`, JSON.stringify(mSession));
  }
}

const motionRecorder = new MotionRecorder();

export default motionRecorder;
