import { computed, reactive } from 'vue';
import MiniLesson, { MiniLessonActivity } from '@/model/MiniLesson';

import VideoDatabaseEntry from '@/model/VideoDatabaseEntry';
import videoDB, { VideoDatabase } from '@/services/VideoDatabase';

import Utils from './Utils';

export function updateLessonFormat(lesson: MiniLesson): MiniLesson {
  const updatedLesson = lesson;
  updatedLesson.activities = lesson.activities.map((activity) => ({
    // Backwards compat - convert to new format if necessary
    //   > currently there's nothing to change
    ...activity,
  }));
  return updatedLesson;
}

export function createBlankActivity(motion: VideoDatabaseEntry, title: string): MiniLessonActivity {
  return {
    title,
    startTime: 0,
    endTime: motion.duration,
    demoVisual: 'video',
    userVisual: 'none',
    practiceSpeed: 1,
  };
}

export function createBlankLesson(videoEntry: VideoDatabaseEntry): MiniLesson {
  return {
    _id: Utils.uuidv4(),
    source: 'custom',
    header: {
      clipName: videoEntry.clipName,
      lessonTitle: 'New Lesson',
    },
    segmentBreaks: [0, videoEntry.duration],
    activities: [createBlankActivity(videoEntry, 'Activity 1')],
  };
}

export class MiniLessonManager {

  readonly lessonsByVideo = reactive(new Map<string, MiniLesson[]>());

  readonly lessonsById = reactive(new Map<string, MiniLesson>());

  constructor() {
    const customLessonCount = this.loadCustomLessons();
    console.log(`Motion database: loaded ${customLessonCount} custom lessons`);
  }

  hasLesson(lesson: MiniLesson): boolean {
    const lessonList = this.lessonsByVideo.get(lesson.header.clipName) ?? [];
    const lessonIndex = lessonList.findIndex((val) => val._id === lesson._id);
    return lessonIndex !== -1;
  }

  upsertLesson(lesson: MiniLesson) {
    const updatedLesson = MiniLessonManager.updateLessonFormat(lesson);
    const lessonList = this.lessonsByVideo.get(lesson.header.clipName) ?? [];
    const existingIndex = lessonList.findIndex((les) => les._id === lesson._id);
    if (existingIndex !== -1) lessonList[existingIndex] = updatedLesson;
    else lessonList.push(updatedLesson);
    this.lessonsByVideo.set(lesson.header.clipName, lessonList);

    this.lessonsById.set(lesson._id, lesson);
  }

  static updateLessonFormat(lesson: MiniLesson): MiniLesson {
    const updatedLesson = lesson;
    updatedLesson.activities = lesson.activities.map((activity) => ({
      // Backwards compat - convert to new format if necessary
      //   > currently there's nothing to change
      ...activity,
    }));
    return updatedLesson;
  }

  removeLesson(lesson: MiniLesson) {
    const lessonList = this.lessonsByVideo.get(lesson.header.clipName) ?? [];
    const lessonIndex = lessonList.findIndex((val) => val._id === lesson._id);
    if (lessonIndex !== -1) lessonList.splice(lessonIndex, 1);
    this.lessonsByVideo.set(lesson.header.clipName, lessonList);

    this.lessonsById.delete(lesson._id);
  }

  getLessons(videoEntry: VideoDatabaseEntry | string) {
    let lessons = undefined as undefined | MiniLesson[];
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
    const customLessonIds = MiniLessonManager.getCustomLessonIdsList();
    let countLoaded = 0;
    for (let i = 0; i < customLessonIds.length; i += 1) {
      const id = customLessonIds[i];
      const custLesson = localStorage.getItem(`lesson-${id}`);
      if (custLesson) {
        this.upsertLesson(JSON.parse(custLesson) as MiniLesson);
        countLoaded += 1;
      }
    }
    return countLoaded;
  }

  static validateLesson(lesson: MiniLesson) {
    if (!lesson) throw new Error('Lesson is null or undefined');
    const clipName = lesson?.header?.clipName;
    if (!clipName) throw new Error('Clip name missing');
    if (!videoDB.entriesByClipName.has(clipName)) throw new Error(`Matching video clip not found for ${clipName}`);
    if (!Array.isArray(lesson.activities) || lesson.activities.length < 1) throw new Error('Lesson contains no activities');
  }

  saveCustomLesson(lesson: MiniLesson) {
    this.upsertLesson(lesson);
    window.localStorage.setItem(`lesson-${lesson._id}`, JSON.stringify(lesson));

    const custLessonIds = MiniLessonManager.getCustomLessonIdsList();
    if (custLessonIds.indexOf(lesson._id) === -1) {
      console.log(`Added custom lesson ${lesson.header.lessonTitle} id=${lesson._id} to localstorage`);
      custLessonIds.push(lesson._id);
    } else {
      console.log(`Updated custom lesson ${lesson.header.lessonTitle} id=${lesson._id} in localstorage`);
    }
    MiniLessonManager.saveCustomLessonsIdsList(custLessonIds);
  }

  deleteCustomLesson(lesson: MiniLesson) {
    this.removeLesson(lesson);

    const custLessonIds = MiniLessonManager.getCustomLessonIdsList();
    const lessonIdIndex = custLessonIds.indexOf(lesson._id);
    if (lessonIdIndex !== -1) custLessonIds.splice(lessonIdIndex, 1);
    MiniLessonManager.saveCustomLessonsIdsList(custLessonIds);

    window.localStorage.removeItem(`lesson-${lesson._id}`);
  }
}

const miniLessonManager = new MiniLessonManager();
export default miniLessonManager;
