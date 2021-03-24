import DanceLesson from './DanceLesson';
/* eslint-disable */

import renegadeLesson from './lessons/renegade.lesson.json';
import itsafitLesson from './lessons/itsafit.lesson.json';
import deruloLesson from './lessons/derulo.lesson.json';
import unhhunhLesson from './lessons/unhhunh.lesson.json';


export default interface DanceEntry {
  title: string;
  videoSrc: string;
  thumbnail: string;
  animatedThumb: string;
  hovering: boolean;
  lessons: Array<DanceLesson>;
}

export interface LessonSelection {
  dance: DanceEntry;
  lesson: DanceLesson;
}

export const dances: Array<DanceEntry> = [
  {
    title: 'Renegade',
    videoSrc: 'dances/renegade.mp4',
    thumbnail: 'dances/renegade.jpg',
    animatedThumb: 'dances/renegade.gif',
    hovering: false,
    lessons: [
      renegadeLesson as DanceLesson,
    ],
  },
  {
    title: 'Unh Hunhh',
    videoSrc: 'dances/unhhunh.mp4',
    thumbnail: 'dances/unhhunh.jpg',
    animatedThumb: 'dances/unhhunh.gif',
    hovering: false,
    lessons: [
      unhhunhLesson as DanceLesson
    ],
  },
  {
    title: 'Derulo',
    videoSrc: 'dances/derulo.mp4',
    thumbnail: 'null',
    animatedThumb: 'null',
    hovering: false,
    lessons: [
      deruloLesson as DanceLesson
    ],
  },
  {
    title: "It's a fit",
    videoSrc: 'dances/itsafit.mp4',
    thumbnail: 'null',
    animatedThumb: 'null',
    hovering: false,
    lessons: [
      itsafitLesson as DanceLesson
    ],
  }
];
