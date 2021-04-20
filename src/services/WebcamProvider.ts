import RecordRTC, { invokeSaveAsDialog } from 'recordrtc';

import { computed, ref, Ref } from 'vue';

export const WEBCAM_DIMENSIONS = Object.freeze({
  width: 640,
  height: 480,
});

export class WebcamProvider {

  // Recorder class
  private recorder = ref(null as null | RecordRTC);

  // The actual media stream
  private mediaStream = ref(null as null | MediaStream);

  // List of active connections. Used so we know when to pause the webcam
  private activeConnections: Set<HTMLVideoElement> = new Set();

  private permissionState: Ref<PermissionState> = ref('prompt');

  private isWebcamLoading = ref(false);

  public webcamError = ref(null as any);

  public isRecording = ref(false);

  constructor() {
    this.readPermissionStatus();
  }

  private async readPermissionStatus(): Promise<void> {
    if (navigator.permissions) {
      try {
        const result = await navigator.permissions.query({ name: 'camera' });
        this.permissionState.value = result.state;

        // eslint-disable-next-line no-empty
      } catch { }
    }
  }

  public permissionStatus(): Ref<PermissionState> {
    return this.permissionState;
  }

  public async startWebcam(): Promise<void> {
    if (this.mediaStream.value || this.isWebcamLoading.value) {
      return;
    }
    this.isWebcamLoading.value = true;

    try {
      const constraints: MediaStreamConstraints = {
        video: {
          facingMode: 'user',
          width: WEBCAM_DIMENSIONS.width,
          height: WEBCAM_DIMENSIONS.height,
          aspectRatio: 1.777777778,
          frameRate: 30,
        },
        audio: true,
      };

      if (!navigator.mediaDevices?.getUserMedia) throw new Error("Browser doesn't support webcam");

      this.mediaStream.value = await navigator.mediaDevices.getUserMedia(constraints);

      this.permissionState.value = 'granted';
    } finally {
      this.isWebcamLoading.value = false;
    }
  }

  public webcamStatus = computed(() => {
    if (this.mediaStream.value) return 'running';
    if (this.isWebcamLoading.value) return 'loading';
    return 'stopped';
  });

  public async connectVideoElement(videoE: HTMLVideoElement): Promise<void> {

    if (this.permissionState.value !== 'granted') throw new Error("Doesn't have permissions yet!");

    this.activeConnections.add(videoE);

    // eslint-disable-next-line no-param-reassign
    console.log('Connecting media stream to video');
    videoE.srcObject = this.mediaStream.value;
    videoE.onloadedmetadata = () => {
      videoE.play();
      console.log('Connected media stream to video');
    };
  }

  public disconnectVideoElement(videoE: HTMLVideoElement): void {
    this.activeConnections.delete(videoE);

    videoE.srcObject = null;

    if (this.activeConnections.size === 0 && !this.recorder) {
      this.stopWebcam();
    }
  }

  public async stopWebcam(): Promise<void> {
    if (this.recorder) {
      try {
        await this.stopRecording();
        // eslint-disable-next-line no-empty
      } catch { }
    }

    if (this.mediaStream.value) {
      this.mediaStream.value.getTracks().forEach((x) => x.stop());
    }
    this.mediaStream.value = null;
  }

  public async startRecording(): Promise<void> {
    if (this.recorder.value || this.isRecording.value) {
      return;
    }

    if (!this.mediaStream.value) {
      throw new Error('Webcam must be started before recording can happen');
    }

    this.isRecording.value = true;

    const rtc = new RecordRTC(this.mediaStream.value, {
      type: 'video',
    });
    rtc.startRecording();
    this.recorder.value = rtc;
  }

  public async stopRecording(): Promise<Blob> {

    return new Promise((res) => {
      if (!this.recorder.value) throw new Error("Haven't started recording");
      this.isRecording.value = false;
      const recorder = this.recorder.value;
      this.recorder.value.stopRecording(() => {
        res(recorder.getBlob());
        this.recorder.value = null;
      });
    });
  }

  public async clearRecording(): Promise<void> {
    // TODO: pay attention to status of recording
    // this.recorder?.stopRecording();
    this.recorder.value = null;
  }

  // public async postFiles(url: string, filename: string): Promise<void> {
  //   if (!this.recorder) throw new Error('Nothing to post');

  //   const blob = this.recorder.getBlob();
  //   invokeSaveAsDialog(blob, filename);

  //   const fname = `${filename}.webm`;

  //   const file = new File([blob], fname, {
  //     type: 'video/webm',
  //   });

  // videoElement.src = '';
  // videoElement.srcObject = null;

  // if (mediaStream) { mediaStream.stop(); }
  // }
}

export const saveBlob = invokeSaveAsDialog;

const defaultProvider = new WebcamProvider();

export default defaultProvider;
