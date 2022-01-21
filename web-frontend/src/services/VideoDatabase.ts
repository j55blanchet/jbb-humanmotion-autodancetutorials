import { computed, reactive } from 'vue';
import MiniLesson, { MiniLessonActivity } from '@/model/MiniLesson';
import videoDatabase from '../../../data/database.json';
import Utils from './Utils';
import VideoVideoDatabaseEntry from '@/model/VideoDatabaseEntry';

export class VideoDatabase {

  readonly allTags = reactive(new Set<string>());

  readonly entriesByClipName = reactive(new Map<string, VideoVideoDatabaseEntry>());

  readonly entries = computed(() => Array.from(this.entriesByClipName.values()));

  readonly motionNames = computed(() => this.entries.value.map((dbEntry) => dbEntry.clipName));

  readonly lessonsByVideo = reactive(new Map<string, MiniLesson[]>());

  readonly lessonsById = reactive(new Map<string, MiniLesson>());

  constructor() {

    videoDatabase.forEach((videoEntry) => {
      this.entriesByClipName.set(videoEntry.clipName, {
        videoSrc: `videos/${videoEntry.clipPath}`,
        ...videoEntry,
        thumbnailSrc: `thumbs/${videoEntry.thumbnailSrc}`,
      });
      this.lessonsByVideo.set(videoEntry.clipName, []);
      videoEntry.tags.forEach((tag) => this.allTags.add(tag));
    });

    console.log(`Motion database: loaded ${this.entriesByClipName.size} videos`);
    // defaultLessons.forEach((lesson) => {
    //   this.upsertLesson({
    //     source: 'builtin',
    //     ...lesson,
    //   } as MiniLesson);
    // });
    // console.log(`Motion database: loaded ${defaultLessons.length} built-in lessons`);

    const customLessonCount = this.loadCustomLessons();
    console.log(`Motion database: loaded ${customLessonCount} custom lessons`);
  }

  hasLesson(lesson: MiniLesson): boolean {
    const lessonList = this.lessonsByVideo.get(lesson.header.clipName) ?? [];
    const lessonIndex = lessonList.findIndex((val) => val._id === lesson._id);
    return lessonIndex !== -1;
  }

  upsertLesson(lesson: MiniLesson) {
    const updatedLesson = VideoDatabase.updateLessonFormat(lesson);
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

  getLessons(videoEntry: VideoVideoDatabaseEntry | string) {
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
    const customLessonIds = VideoDatabase.getCustomLessonIdsList();
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

  validateLesson(lesson: MiniLesson) {
    if (!lesson) throw new Error('Lesson is null or undefined');
    const clipName = lesson?.header?.clipName;
    if (!clipName) throw new Error('Clip name missing');
    if (!this.entriesByClipName.has(clipName)) throw new Error(`Matching video clip not found for ${clipName}`);
    if (!Array.isArray(lesson.activities) || lesson.activities.length < 1) throw new Error('Lesson contains no activities');
  }

  saveCustomLesson(lesson: MiniLesson) {
    this.upsertLesson(lesson);
    window.localStorage.setItem(`lesson-${lesson._id}`, JSON.stringify(lesson));

    const custLessonIds = VideoDatabase.getCustomLessonIdsList();
    if (custLessonIds.indexOf(lesson._id) === -1) {
      console.log(`Added custom lesson ${lesson.header.lessonTitle} id=${lesson._id} to localstorage`);
      custLessonIds.push(lesson._id);
    } else {
      console.log(`Updated custom lesson ${lesson.header.lessonTitle} id=${lesson._id} in localstorage`);
    }
    VideoDatabase.saveCustomLessonsIdsList(custLessonIds);
  }

  deleteCustomLesson(lesson: MiniLesson) {
    this.removeLesson(lesson);

    const custLessonIds = VideoDatabase.getCustomLessonIdsList();
    const lessonIdIndex = custLessonIds.indexOf(lesson._id);
    if (lessonIdIndex !== -1) custLessonIds.splice(lessonIdIndex, 1);
    VideoDatabase.saveCustomLessonsIdsList(custLessonIds);

    window.localStorage.removeItem(`lesson-${lesson._id}`);
  }
}

const db = new VideoDatabase();
export default db;
