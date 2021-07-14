// import parse from 'csv-parse';

import Parser, { Row } from '@gregoranders/csv';
import { Landmark } from '@/services/MediaPipeTypes';

const VIDEO_EXTENSIONS = ['.mp4', '.m4v', '.mov'];

export class PoseProvider {

  private poseFiles: Map<string, Readonly<Array<Readonly<Array<Readonly<Landmark>>>>>> = new Map();

  async GetPose(videoName: string) {
    if (videoName.length < 4) return [];

    let poseFilename = videoName.replace('videos', 'poses');
    for (let i = 0; i < VIDEO_EXTENSIONS.length; i += 1) {
      const extension = VIDEO_EXTENSIONS[i];
      poseFilename = poseFilename.replace(extension, '.pose.csv');
    }

    const cached = this.poseFiles.get(poseFilename);
    if (cached !== undefined) return cached;

    const stored = localStorage.getItem(poseFilename);
    if (stored !== null) {
      const poses = JSON.parse(stored) as Readonly<Array<Readonly<Array<Readonly<Landmark>>>>>;
      this.poseFiles.set(poseFilename, Object.freeze(poses));
      return poses;
    }

    const poseFile = await PoseProvider.getPoseFile(poseFilename);
    const poses = PoseProvider.convertToPoseList(poseFile);
    this.poseFiles.set(poseFilename, poses);

    localStorage.setItem(poseFilename, JSON.stringify(poses));

    return poses;
  }

  private static async getPoseFile(url: string) {

    const response = await fetch(url);
    if (!response.ok) throw new Error(`Error fetching pose file: ${response.statusText}`);

    const text = await response.text();

    return new Parser().parse(text);
  }

  private static convertToPoseList(csv: readonly Row[]) {
    const temp = csv.map((row) => PoseProvider.convertRow(row));
    return Object.freeze(temp.filter((x) => x.length > 0));
  }

  private static convertRow(row: Row) {
    if (row.length === 0) return [];
    if (row[0].startsWith('#')) return [];

    const lms = [] as Array<Readonly<Landmark>>;
    for (let i = 0; i + 2 < row.length; i += 3) {
      lms.push(
        Object.freeze({
          x: Number.parseFloat(row[i]),
          y: Number.parseFloat(row[i + 1]),
          visibility: Number.parseFloat(row[i + 2]),
        }),
      );
    }

    return Object.freeze(lms);
  }
}

const poseProvider = new PoseProvider();

export default poseProvider;
