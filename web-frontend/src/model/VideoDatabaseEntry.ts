export default interface VideoDatabaseEntry {
  title: string;
  clipName: string;
  clipPath: string;
  frameCount: number;
  fps: number;
  duration: number;
  width: number;
  height: number;
  videoSrc: string;
  thumbnailSrc: string;
  startTime: number;
  endTime: number;
  tags: string[];
// eslint-disable-next-line semi
}
