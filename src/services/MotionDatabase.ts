import DanceEntry from '@/model/DanceEntry';
import DanceLesson from '@/model/DanceLesson';

import renegadeLesson from '@/model/lessons/renegade.lesson.json';
import itsafitLesson from '@/model/lessons/itsafit.lesson.json';
import deruloLesson from '@/model/lessons/derulo.lesson.json';
import unhhunhLesson from '@/model/lessons/unhhunh.lesson.json';

const dances: Array<DanceEntry> = [
  {
    title: 'Renegade',
    videoSrc: 'dances/renegade.mp4',
    hovering: false,
    lessons: [
      renegadeLesson as DanceLesson,
    ],
  },
  {
    title: 'Unh Hunhh',
    videoSrc: 'dances/unhhunh.mp4',
    hovering: false,
    lessons: [
      unhhunhLesson as DanceLesson,
    ],
  },
  {
    title: 'Derulo',
    videoSrc: 'dances/derulo.mp4',
    hovering: false,
    lessons: [
      deruloLesson as DanceLesson,
    ],
  },
  {
    title: "It's a fit",
    videoSrc: 'dances/itsafit.mp4',
    hovering: false,
    lessons: [
      itsafitLesson as DanceLesson,
    ],
  },
];

export default dances;
