import { MpHolisticResults } from './MediaPipeTypes';
import Utils from './Utils';
import webcamProvider, { saveBlob } from './WebcamProvider';

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

  async startRecordingSession(userDims: Dimensions, demoDims: Dimensions): Promise<number> {
    this.recordingSessions[this.recordingSessionNextId] = {
      userDimension: userDims,
      userFrames: [],
      demoDimension: demoDims,
      demoFrames: [],
    };
    this.recordingSessionNextId += 1;

    await webcamProvider.startRecording();
    return this.recordingSessionNextId - 1;
  }

  saveMotionFrame(sessionId: number, userFrame: MpHolisticResults, demoFrame: MpHolisticResults) {
    const session = this.recordingSessions[sessionId];
    if (!session) throw new Error(`Recording session ${sessionId} wasn't found!`);

    debugger;
    if (userFrame.image) delete userFrame.image;
    session.userFrames.push(userFrame);
    session.demoFrames.push(demoFrame);
  }

  async endRecordingSession(sessionId: number, start: number, end: number) {
    const session = this.recordingSessions[sessionId];
    if (!session) throw new Error(`Recording session ${sessionId} wasn't found!`);

    const webcamBlob = await webcamProvider.stopRecording();
    saveBlob(webcamBlob, 'webcam.webm');

    const mSession = { startTime: start, endTime: end, ...session };

    Utils.PromptDownloadFile(`RecordedSession-${sessionId}.json`, JSON.stringify(mSession));
  }
}

const motionRecorder = new MotionRecorder();

export default motionRecorder;
