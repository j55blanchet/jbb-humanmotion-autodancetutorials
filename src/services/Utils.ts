//
// Utils.ts
//

export default class Utils {

  static PromptDownloadFile(filename: string, text: string) {
    const element = document.createElement('a');
    element.setAttribute('href', `data:text/plain;charset=utf-8,${encodeURIComponent(text)}`);
    element.setAttribute('download', filename);
    element.style.display = 'none';

    document.body.appendChild(element);
    element.click();

    document.body.removeChild(element);
  }

  // static CaptureVideoImage(videoE: HTMLVideoElement) {
  //   const canvas = document.createElement('canvas');
  //   canvas.style.display = 'none';
  //   document.appendChild(canvas);
  //   canvas.width = videoE.width;
  //   canvas.height = videoE.height;
  //   const ctx = canvas.getContext('2d')!;

  //   ctx.drawImage(videoE, 0, 0, videoE.width, videoE.height);
  // }

  static DoEveryFrame(
    onFrame: () => Promise<void>,
    shouldRun?: () => boolean,
  ) {

    if (shouldRun !== undefined && !shouldRun()) {
      requestAnimationFrame(() => {
        Utils.DoEveryFrame(onFrame);
      });
    } else {
      requestAnimationFrame(() => {
        onFrame().then(() => {
          Utils.DoEveryFrame(onFrame);
        });
      });
    }
  }

}
