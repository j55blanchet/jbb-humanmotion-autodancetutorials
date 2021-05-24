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
      this.upsertLesson({
        source: 'builtin',
        ...lesson,
      } as DanceLesson);
    });
    console.log(`Motion database: loaded ${defaultLessons.length} built-in lessons`);

    const customLessonCount = this.loadCustomLessons();
    console.log(`Motion database: loaded ${customLessonCount} custom lessons`);
  }

  hasLesson(lesson: DanceLesson): boolean {
    const lessonList = this.lessons.get(lesson.header.clipName) ?? [];
    const lessonIndex = lessonList.findIndex((val) => val._id === lesson._id);
    return lessonIndex !== -1;
  }

  upsertLesson(lesson: DanceLesson) {
    const lessonList = this.lessons.get(lesson.header.clipName) ?? [];
    const existingIndex = lessonList.findIndex((les) => les._id === lesson._id);
    if (existingIndex !== -1) lessonList[existingIndex] = lesson;
    else lessonList.push(lesson);
    this.lessons.set(lesson.header.clipName, lessonList);
  }

  removeLesson(lesson: DanceLesson) {
    const lessonList = this.lessons.get(lesson.header.clipName) ?? [];
    const lessonIndex = lessonList.findIndex((val) => val._id === lesson._id);
    if (lessonIndex !== -1) lessonList.splice(lessonIndex, 1);
    this.lessons.set(lesson.header.clipName, lessonList);
  }

  getLessons(videoEntry: DatabaseEntry | string) {
    let lessons = undefined as undefined | DanceLesson[];
    if (typeof videoEntry === 'object' && videoEntry !== null) lessons = this.lessons.get(videoEntry.clipName);
    else lessons = this.lessons.get(videoEntry);
    return lessons;
  }

  private static getCustomLessonIdsList(): Array<string> {
    return JSON.parse(window.localStorage.getItem('custom-lessons') ?? '[]');
  }

  private static saveCustomLessonsIdsList(customLessonIds: Array<string>) {
    window.localStorage.setItem('custom-lessons', JSON.stringify(customLessonIds));
  }

  private loadCustomLessons(): number {
    const customLessonIds = MotionDatabase.getCustomLessonIdsList();
    let countLoaded = 0;
    for (let i = 0; i < customLessonIds.length; i += 1) {
      const id = customLessonIds[i];
      const custLesson = localStorage.getItem(`lesson-${id}`);
      if (custLesson) {
        this.upsertLesson(JSON.parse(custLesson) as DanceLesson);
        countLoaded += 1;
      }
    }
    return countLoaded;
  }

  validateLesson(lesson: DanceLesson) {
    if (!lesson) throw new Error('Lesson is null or undefined');
    const clipName = lesson?.header?.clipName;
    if (!clipName) throw new Error('Clip name missing');
    if (!this.motionsMap.has(clipName)) throw new Error(`Matching video clip not found for ${clipName}`);
    if (!Array.isArray(lesson.activities) || lesson.activities.length < 1) throw new Error('Lesson contains no activities');
  }

  saveCustomLesson(lesson: DanceLesson) {
    this.upsertLesson(lesson);
    window.localStorage.setItem(`lesson-${lesson._id}`, JSON.stringify(lesson));

    const custLessonIds = MotionDatabase.getCustomLessonIdsList();
    if (custLessonIds.indexOf(lesson._id) === -1) {
      console.log(`Added custom lesson ${lesson.header.lessonTitle} id=${lesson._id} to localstorage`);
      custLessonIds.push(lesson._id);
    } else {
      console.log(`Updated custom lesson ${lesson.header.lessonTitle} id=${lesson._id} in localstorage`);
    }
    MotionDatabase.saveCustomLessonsIdsList(custLessonIds);
  }

  deleteCustomLesson(lesson: DanceLesson) {
    this.removeLesson(lesson);

    const custLessonIds = MotionDatabase.getCustomLessonIdsList();
    const lessonIdIndex = custLessonIds.indexOf(lesson._id);
    if (lessonIdIndex !== -1) custLessonIds.splice(lessonIdIndex, 1);
    MotionDatabase.saveCustomLessonsIdsList(custLessonIds);

    window.localStorage.removeItem(`lesson-${lesson._id}`);
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
    source: 'custom',
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
