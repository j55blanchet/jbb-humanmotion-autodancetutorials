import DanceLesson, { Activity } from '@/model/DanceLesson';

import videoDatabase from '@/model/videoDatabase.json';
import defaultLessons from '@/model/bakedInLessons.json';

import { computed, reactive } from 'vue';
import Utils from './Utils';

export interface DatabaseEntry {
  title: string;
  clipName: string;
  clipPath: string;
  frameCount: number;
  fps: number;
  duration: number;
  width: number;
  height: number;
  videoSrc: string;
}

export class MotionDatabase {
  readonly motionsMap = reactive(new Map<string, DatabaseEntry>());

  readonly motions = computed(() => Array.from(this.motionsMap.values()));

  readonly lessons = reactive(new Map<string, DanceLesson[]>());

  constructor() {

    videoDatabase.forEach((videoEntry) => {
      this.motionsMap.set(videoEntry.clipName, {
        videoSrc: `motions/${videoEntry.clipPath}`,
        ...videoEntry,
      });
      this.lessons.set(videoEntry.clipName, []);
    });

    console.log(`Motion database: loaded ${this.motionsMap.size} videos`);
    defaultLessons.forEach((lesson) => {
      this.addLesson(lesson as DanceLesson);
    });
    console.log(`Motion database: loaded ${defaultLessons.length} built-in lessons`);
  }

  addLesson(lesson: DanceLesson) {
    const lessonList = this.lessons.get(lesson.header.clipName);
    if (lessonList === undefined) {
      console.warn(`No video entry found for lesson ${lesson.header.clipName}`);
      this.lessons.set(lesson.header.clipName, [lesson]);
      return;
    }

    lessonList.push(lesson);
    this.lessons.set(lesson.header.clipName, lessonList);
  }

  getLessons(videoEntry: DatabaseEntry | string) {
    let lessons = undefined as undefined | DanceLesson[];
    if (typeof videoEntry === 'object' && videoEntry !== null) lessons = this.lessons.get(videoEntry.clipName);
    else lessons = this.lessons.get(videoEntry);
    return lessons;
  }
}

export function createBlankActivity(motion: DatabaseEntry, title: string): Activity {
  return {
    title,
    startTime: 0,
    endTime: motion.duration,
    demoVisual: 'video',
    userVisual: 'none',
    practiceSpeed: 1,
  };
}

export function createBlankLesson(videoEntry: DatabaseEntry): DanceLesson {
  return {
    _id: Utils.uuidv4(),
    header: {
      clipName: videoEntry.clipName,
      lessonTitle: 'New Lesson',
    },
    segmentBreaks: [0, videoEntry.duration],
    activities: [createBlankActivity(videoEntry, 'Activity 1')],
    fps: videoEntry.fps,
  };
}

const db = new MotionDatabase();
export default db;
