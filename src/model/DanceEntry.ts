/* eslint-disable semi */
import DanceLesson from './DanceLesson';

export default interface DanceEntry {
  title: string;
  videoSrc: string;
  hovering: boolean;
  lessons: Array<DanceLesson>;
}

export interface LessonSelection {
  dance: DanceEntry;
  lesson: DanceLesson;
}
