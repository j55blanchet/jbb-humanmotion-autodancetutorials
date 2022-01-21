import { computed, reactive } from 'vue';
import videoDatabase from '../../../data/database.json';
import VideoVideoDatabaseEntry from '@/model/VideoDatabaseEntry';

export class VideoDatabase {

  readonly allTags = reactive(new Set<string>());

  readonly entriesByClipName = reactive(new Map<string, VideoVideoDatabaseEntry>());

  readonly entries = computed(() => Array.from(this.entriesByClipName.values()));

  readonly clipNames = computed(() => this.entries.value.map((dbEntry) => dbEntry.clipName));

  constructor() {

    videoDatabase.forEach((videoEntry) => {
      this.entriesByClipName.set(videoEntry.clipName, {
        videoSrc: `videos/${videoEntry.clipPath}`,
        ...videoEntry,
        thumbnailSrc: `thumbs/${videoEntry.thumbnailSrc}`,
      });
      videoEntry.tags.forEach((tag) => this.allTags.add(tag));
    });

    console.log(`Video database: loaded ${this.entriesByClipName.size} videos`);
  }
}

const db = new VideoDatabase();
export default db;
