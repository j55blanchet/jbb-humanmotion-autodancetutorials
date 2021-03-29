// import parse from 'csv-parse';

import Parser from '@gregoranders/csv';

export default class PoseProvider {

  static async getPose(baseName: string) {

    const url = `poses/${baseName}.poses.csv`;
    const response = await fetch(url);
    if (!response.ok) throw new Error(`Error fetching pose file: ${response.statusText}`);

    const text = await response.text();

    return new Parser().parse(text);
  }
}
