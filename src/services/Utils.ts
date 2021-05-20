//
// Utils.ts
//

export default class Utils {

  static sleep(secs: number): Promise<void> {
    return new Promise((res) => setTimeout(res, secs * 1000));
  }

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

  static uuidv4() {
    // eslint-disable-next-line no-bitwise, no-mixed-operators, space-infix-ops
    return (`${1e7}-${1e3}-${4e3}-${8e3}-${1e11}`).replace(/[018]/g, (c: any) => (c ^ crypto.getRandomValues(new Uint8Array(1))[0] & 15 >> c / 4).toString(16));
  }

  static deepCopy<T>(obj: T): T {

    // Handle the 3 simple types, and null or undefined
    if (obj === null || undefined === obj || typeof obj !== 'object') {
      return obj;
    }

    if (obj instanceof Date) {
      const copy = new Date();
      copy.setTime(obj.getTime());
      return copy as unknown as T;
    }

    if (Array.isArray(obj)) {
      const len = obj.length;
      const copy = new Array(len);
      for (let i = 0; i < len; i += 1) {
        copy[i] = Utils.deepCopy(obj[i]);
      }
      return copy as unknown as T;
    }

    if (typeof obj === 'object') {
      const typedObj = obj as any;
      const copy = {} as any;
      const attrs = Object.keys(typedObj);
      for (let i = 0; i < attrs.length; i += 1) {
        const attr = attrs[i];
        const val = typedObj[attr];
        // eslint-disable-next-line no-prototype-builtins
        if (typedObj.hasOwnProperty(attr)) copy[attr] = Utils.deepCopy(val);
      }
      return copy;
    }

    throw new Error(`Unable to copy object ${obj}! It's type isn't supported`);
  }
}
