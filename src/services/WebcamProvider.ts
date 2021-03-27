import RecordRTC, { invokeSaveAsDialog } from 'recordrtc';

export class WebcamProvider {
  private recorder?: RecordRTC;

  private mediaStream?: MediaStream;

  public async startWebcam() {
    if (this.mediaStream) {
      return;
    }

    const constraints: MediaStreamConstraints = {
      video: {
        facingMode: 'user',
        width: 1280,
        height: 720,
        aspectRatio: 1.777777778,
        frameRate: 30,
      },
    };

    if (!navigator.mediaDevices?.getUserMedia) throw new Error("Browser doesn't support webcam");

    this.mediaStream = await navigator.mediaDevices.getUserMedia(constraints);

  }

  static doEveryFrame(onFrame: () => Promise<void>) {
    requestAnimationFrame(() => {
      onFrame().then(() => {
        WebcamProvider.doEveryFrame(onFrame);
      });
    });
  }

  public connectVideoElement(videoE: HTMLVideoElement) {
    // eslint-disable-next-line no-param-reassign
    videoE.srcObject = this.mediaStream as any;
  }

  public async startRecording() {

    if (this.recorder) {
      return;
    }

    if (!this.mediaStream) {
      throw new Error('Webcam must be started before recording can happen');
    }

    // eslint-disable-next-line new-cap
    const recorder = new RecordRTC(this.mediaStream, {
      type: 'video',
    });
    recorder.startRecording();
    this.recorder = recorder;

  }

  public async stopRecording() {
    if (!this.recorder) throw new Error("Haven't started recording");

    await this.recorder.stopRecording();
  }

  public getMediaStream(): MediaStream | null {
    return this.mediaStream ?? null;
  }

  public postFiles(url: string, filename: string) {

    if (!this.recorder) throw new Error('Nothing to post');

    const blob = this.recorder.getBlob();
    invokeSaveAsDialog(blob, filename);

    const fname = `${filename}.webm`;

    const file = new File([blob], fname, {
      type: 'video/webm',
    });

    // videoElement.src = '';
    // videoElement.srcObject = null;

    WebcamProvider.xhr(url, file, () => {
      console.log('File successfully uploaded to server');
    });

    // if (mediaStream) { mediaStream.stop(); }
  }

  private static xhr(url: string, data: File, callback: (resText: string) => void) {
    const request = new XMLHttpRequest();
    request.onreadystatechange = () => {
      if (request.readyState === 4 && request.status === 200) {
        callback(request.responseText);
      }
    };

    // request.upload.onprogress = (e) => {
    //   const percent = e.loaded / e.total;
    // };

    request.upload.onload = () => {
      console.log(`${url} upload finished`);
    };

    request.open('POST', url);

    const formData = new FormData();
    formData.append('file', data);
    request.send(formData);
  }
}

const defaultProvider = new WebcamProvider();

export default defaultProvider;

// function startRecording() {

//   captureUserMedia((stream) => {
//     // mediaStream = stream;

//     // videoElement.srcObject = stream;

//     // videoElement.play();
//     // videoElement.muted = true;
//     // videoElement.controls = false;

//     recorder = RecordRTC(stream, {
//       type: 'video',
//     });

//     recorder.startRecording();
//   });
// }

// function stopRecording(postUrl, filename) {
//   recorder.stopRecording(() => {
//     postFiles(postUrl, filename);
//   });
// }

// function promptSave() {
//   const blob = recorder.getBlob();
//   invokeSaveAsDialog(blob);
// }

// function postFiles(url, filename) {
//   const blob = recorder.getBlob();
//   // invokeSaveAsDialog(blob);

//   var filename = `${filename}.webm`;

//   const file = new File([blob], filename, {
//     type: 'video/webm',
//   });

//   // videoElement.src = '';
//   // videoElement.srcObject = null;

//   xhr(url, file, (responseText) => {
//     console.log('File successfully uploaded to server');
//   });

//   if (mediaStream) { mediaStream.stop(); }
// }

// function xhr(url, data, callback) {
//   const request = new XMLHttpRequest();
//   request.onreadystatechange = () => {
//     if (request.readyState == 4 && request.status == 200) {
//       callback(request.responseText);
//     }
//   };

//   request.upload.onprogress = (e) => {
//     const percent = e.loaded / e.total;
//     // console.log(`${url} upload: ${percent} complete`);

//     if (window.unityInstance) {
//       unityInstance.SendMessage('Main Camera', 'UploadProgressed', percent);
//     }
//   };

//   request.upload.onload = () => {
//     console.log(`${url} upload finished`);
//   };

//   request.open('POST', url);

//   const formData = new FormData();
//   formData.append('file', data);
//   request.send(formData);
// }

// function generateRandomString() {
//   if (window.crypto) {
//     const a = window.crypto.getRandomValues(new Uint32Array(3));
//     let token = '';
//     for (let i = 0, l = a.length; i < l; i++) token += a[i].toString(36);
//     return token;
//   }
//   return (Math.random() * new Date().getTime()).toString(36).replace(/\./g, '');

// }
