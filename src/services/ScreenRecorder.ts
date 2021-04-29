import RecordRTC, { invokeSaveAsDialog } from 'recordrtc';

export default class ScreenRecorder {

  private recorder: RecordRTC | null = null;

  async startRecording() {

    const captureStream = await (navigator.mediaDevices as any).getDisplayMedia({});

    this.recorder = new RecordRTC(captureStream);
    this.recorder.startRecording();
  }

  async endRecording(): Promise<Blob> {
    if (!this.recorder) throw new Error('Recording not started!');
    const { recorder } = this;

    return new Promise((res, rej) => {
      try {
        recorder.stopRecording(() => {
          res(recorder.getBlob());
        });
      } catch (e) {
        rej(e);
      }
    });
  }

}
