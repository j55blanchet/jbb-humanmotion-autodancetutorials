// import parse from 'csv-parse';

import Parser, { Row } from '@gregoranders/csv';
import { Landmark } from '@/services/MediaPipeTypes';

export class PoseProvider {

  private poseFiles: Map<string, Landmark[][]> = new Map();

  async GetPose(baseName: string) {
    const cached = this.poseFiles.get(baseName);
    if (cached !== undefined) return cached;

    const stored = localStorage.getItem(`poses-${baseName}`);
    if (stored !== null) {
      const poses = JSON.parse(stored) as Landmark[][];
      this.poseFiles.set(baseName, poses);
      return poses;
    }

    const poseFile = await PoseProvider.getPoseFile(baseName);
    const poses = PoseProvider.convertToPoseList(poseFile);
    this.poseFiles.set(baseName, poses);

    localStorage.setItem(`poses-${baseName}`, JSON.stringify(poses));

    return poses;
  }

  private static async getPoseFile(baseName: string) {

    const url = `poses/${baseName}.poses.csv`;
    const response = await fetch(url);
    if (!response.ok) throw new Error(`Error fetching pose file: ${response.statusText}`);

    const text = await response.text();

    return new Parser().parse(text);
  }

  private static convertToPoseList(csv: readonly Row[]): Landmark[][] {
    return csv
      .map((row) => PoseProvider.convertRow(row))
      .filter((x) => x.length > 0);
  }

  private static convertRow(row: Row): Landmark[] {
    if (row.length === 0) return [];
    if (row[0].startsWith('#')) return [];

    const lms = [] as Landmark[];
    for (let i = 0; i + 2 < row.length; i += 3) {
      lms.push({
        x: Number.parseFloat(row[i]),
        y: Number.parseFloat(row[i + 1]),
        visibility: Number.parseFloat(row[i + 2]),
      });
    }

    return lms;
  }
}

const poseProvider = new PoseProvider();

export default poseProvider;
