import RecordRTC, { invokeSaveAsDialog } from 'recordrtc';

import {
  computed, reactive, ref, Ref,
} from 'vue';

export const WEBCAM_DIMENSIONS = Object.freeze({
  width: 640,
  height: 480,
});

export class WebcamProvider {

  // Recorder class
  private readonly ongoingRecordings = new Map<string, RecordRTC>();

  private readonly cachedRecordings = new Map<string, RecordRTC>();

  // The actual media stream
  private mediaStream = ref(null as null | MediaStream);

  // List of active connections. Used so we know when to pause the webcam
  private activeConnections: Set<HTMLVideoElement> = new Set();

  private permissionState: Ref<PermissionState> = ref('prompt');

  private isWebcamLoading = ref(false);

  public webcamError = ref(null as any);

  public cachedVideoDeviceId: string | undefined = undefined;

  public cachedAudioDeviceId: string | undefined = undefined;

  constructor() {
    this.readPermissionStatus();
  }

  private async readPermissionStatus(): Promise<void> {
    if (navigator.permissions) {
      try {

        const result = await navigator.permissions.query({ name: 'camera' as any });
        this.permissionState.value = result.state;

        // eslint-disable-next-line no-empty
      } catch { }
    }
  }

  public permissionStatus(): Ref<PermissionState> {
    return this.permissionState;
  }

  public async startWebcam(videoDeviceId?: string, audioDeviceId?: string): Promise<void> {
    if (this.mediaStream.value || this.isWebcamLoading.value) {
      return;
    }
    this.isWebcamLoading.value = true;

    const audioDevice = audioDeviceId ?? this.cachedAudioDeviceId;
    const videoDevice = videoDeviceId ?? this.cachedVideoDeviceId;

    try {
      const constraints: MediaStreamConstraints = {
        video: {
          // facingMode: 'user',
          width: WEBCAM_DIMENSIONS.width,
          height: WEBCAM_DIMENSIONS.height,
          aspectRatio: 1.777777778,
          frameRate: 30,
          deviceId: videoDevice,
        },
        audio: {
          deviceId: audioDevice,
        },
      };

      if (!navigator.mediaDevices?.getUserMedia) throw new Error("Browser doesn't support webcam");

      this.mediaStream.value = await navigator.mediaDevices.getUserMedia(constraints);

      this.cachedVideoDeviceId = videoDevice;
      this.cachedAudioDeviceId = audioDevice;

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

    if (this.activeConnections.size === 0 && this.ongoingRecordings.size === 0) {
      this.stopWebcam();
    }
  }

  public async stopWebcam(): Promise<void> {

    // eslint-disable-next-line no-restricted-syntax
    for (const recorderId of this.ongoingRecordings.keys()) {
      try {
        // eslint-disable-next-line no-await-in-loop
        await this.abortRecording(recorderId);
        // eslint-disable-next-line no-empty
      } catch { }
    }

    if (this.mediaStream.value) {
      this.mediaStream.value.getTracks().forEach((x) => x.stop());
    }
    this.mediaStream.value = null;
  }

  public async startRecording(recordingId: string): Promise<void> {

    if (!this.mediaStream.value) {
      throw new Error('Webcam must be started before recording can happen');
    }

    const rtc = new RecordRTC(this.mediaStream.value, {
      type: 'video',
    });
    rtc.startRecording();

    this.ongoingRecordings.set(recordingId, rtc);

    console.log(`WebcamProvider :: starting recording with id ${recordingId}`);
  }

  public async abortRecording(recordingId: string): Promise<void> {
    const recorder = this.ongoingRecordings.get(recordingId);
    return new Promise((res) => {
      const end = () => {
        this.ongoingRecordings.delete(recordingId);
        res();
      };

      if (!recorder) {
        end();
        return;
      }

      recorder.stopRecording(() => {
        console.log(`WebcamProvider :: aborting recording with id ${recordingId}`);
        end();
      });
    });
  }

  public async stopRecording(recordingId: string): Promise<void> {

    if (!this.ongoingRecordings.has(recordingId)) {
      // console.warn(`WebcamProvider:: stopRecording -- Not currently recording for id ${recordingId}`);
      return Promise.resolve();
    }

    return new Promise((res) => {
      const recorder = this.ongoingRecordings.get(recordingId) as RecordRTC;
      recorder.stopRecording(() => {
        this.ongoingRecordings.delete(recordingId);
        this.cachedRecordings.set(recordingId, recorder);
        console.log(`WebcamProvider :: stopping recording with id ${recordingId}`);
        res();
      });
    });
  }

  public isRecording(recordingId: string): boolean {
    return this.ongoingRecordings.has(recordingId);
  }

  public async getBlob(recordingId: string): Promise<Blob> {
    const recorder = this.cachedRecordings.get(recordingId);
    if (!recorder) throw new Error(`No saved recording with id: ${recordingId}`);
    return recorder.getBlob();
  }

  public async clearRecording(recordingId: string) {
    this.cachedRecordings.delete(recordingId);
  }

  public getAllRecordings(): string[] {
    return [...this.cachedRecordings.keys()];
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
