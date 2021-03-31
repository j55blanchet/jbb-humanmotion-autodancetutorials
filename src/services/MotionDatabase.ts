import DanceEntry from '@/model/DanceEntry';
import DanceLesson from '@/model/DanceLesson';

import renegadeLesson from '@/model/lessons/renegade.lesson.json';
import itsafitLesson from '@/model/lessons/itsafit.lesson.json';
import deruloLesson from '@/model/lessons/derulo.lesson.json';
import unhhunhLesson from '@/model/lessons/unhhunh.lesson.json';

import aslCoconutLesson from '@/model/lessons/asl/COCONUT.lesson.json';
import aslFlipFlopsLesson from '@/model/lessons/asl/flipflops.lesson.json';
import aslOceanLesson from '@/model/lessons/asl/ocean.lesson.json';
import aslSailboatLesson from '@/model/lessons/asl/sailboat.lesson.json';
import aslTurtleLesson from '@/model/lessons/asl/TURTLE.lesson.json';
import aslUmbrellaLesson from '@/model/lessons/asl/UMBRELLA.lesson.json';

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

  {
    title: 'ASL: Coconut',
    videoSrc: 'dances/asl/COCONUT.mp4',
    hovering: false,
    lessons: [aslCoconutLesson as DanceLesson],
  },
  {
    title: 'ASL: Flip Flips',
    videoSrc: 'dances/asl/flipflops.mp4',
    hovering: false,
    lessons: [aslFlipFlopsLesson as DanceLesson],
  },
  {
    title: 'ASL: Ocean',
    videoSrc: 'dances/asl/ocean.mp4',
    hovering: false,
    lessons: [aslOceanLesson as DanceLesson],
  },
  {
    title: 'ASL: Sailboat',
    videoSrc: 'dances/asl/sailboat.mp4',
    hovering: false,
    lessons: [aslSailboatLesson as DanceLesson],
  },
  {
    title: 'ASL: Turtle',
    videoSrc: 'dances/asl/TURTLE.mp4',
    hovering: false,
    lessons: [aslTurtleLesson as DanceLesson],
  },
  {
    title: 'ASL: Umbrella',
    videoSrc: 'dances/asl/UMBRELLA.mp4',
    hovering: false,
    lessons: [aslUmbrellaLesson as DanceLesson],
  },
];

export default dances;
