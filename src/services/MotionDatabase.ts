import VideoLesson, { Activity } from '@/model/VideoLesson';

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

  readonly lessonsByVideo = reactive(new Map<string, VideoLesson[]>());

  readonly lessonsById = reactive(new Map<string, VideoLesson>());

  constructor() {

    videoDatabase.forEach((videoEntry) => {
      this.motionsMap.set(videoEntry.clipName, {
        videoSrc: `videos/${videoEntry.clipPath}`,
        ...videoEntry,
      });
      this.lessonsByVideo.set(videoEntry.clipName, []);
    });

    console.log(`Motion database: loaded ${this.motionsMap.size} videos`);
    defaultLessons.forEach((lesson) => {
      this.upsertLesson({
        source: 'builtin',
        ...lesson,
      } as VideoLesson);
    });
    console.log(`Motion database: loaded ${defaultLessons.length} built-in lessons`);

    const customLessonCount = this.loadCustomLessons();
    console.log(`Motion database: loaded ${customLessonCount} custom lessons`);
  }

  hasLesson(lesson: VideoLesson): boolean {
    const lessonList = this.lessonsByVideo.get(lesson.header.clipName) ?? [];
    const lessonIndex = lessonList.findIndex((val) => val._id === lesson._id);
    return lessonIndex !== -1;
  }

  upsertLesson(lesson: VideoLesson) {
    const lessonList = this.lessonsByVideo.get(lesson.header.clipName) ?? [];
    const existingIndex = lessonList.findIndex((les) => les._id === lesson._id);
    if (existingIndex !== -1) lessonList[existingIndex] = lesson;
    else lessonList.push(lesson);
    this.lessonsByVideo.set(lesson.header.clipName, lessonList);

    this.lessonsById.set(lesson._id, lesson);
  }

  removeLesson(lesson: VideoLesson) {
    const lessonList = this.lessonsByVideo.get(lesson.header.clipName) ?? [];
    const lessonIndex = lessonList.findIndex((val) => val._id === lesson._id);
    if (lessonIndex !== -1) lessonList.splice(lessonIndex, 1);
    this.lessonsByVideo.set(lesson.header.clipName, lessonList);

    this.lessonsById.delete(lesson._id);
  }

  getLessons(videoEntry: DatabaseEntry | string) {
    let lessons = undefined as undefined | VideoLesson[];
    if (typeof videoEntry === 'object' && videoEntry !== null) lessons = this.lessonsByVideo.get(videoEntry.clipName);
    else lessons = this.lessonsByVideo.get(videoEntry);
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
        this.upsertLesson(JSON.parse(custLesson) as VideoLesson);
        countLoaded += 1;
      }
    }
    return countLoaded;
  }

  validateLesson(lesson: VideoLesson) {
    if (!lesson) throw new Error('Lesson is null or undefined');
    const clipName = lesson?.header?.clipName;
    if (!clipName) throw new Error('Clip name missing');
    if (!this.motionsMap.has(clipName)) throw new Error(`Matching video clip not found for ${clipName}`);
    if (!Array.isArray(lesson.activities) || lesson.activities.length < 1) throw new Error('Lesson contains no activities');
  }

  saveCustomLesson(lesson: VideoLesson) {
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

  deleteCustomLesson(lesson: VideoLesson) {
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

export function createBlankLesson(videoEntry: DatabaseEntry): VideoLesson {
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
