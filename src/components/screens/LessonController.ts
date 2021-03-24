import DanceLesson, { Activity } from '@/model/DanceLesson';
import VideoPlayer from '@/components/elements/VideoPlayer.vue';
import { reactive } from 'vue';

export default class LessonController {

  public activityIndex = 0;

  private get curActivity(): Activity {
    return this.lesson.activities[this.activityIndex];
  }

  private get hasNextActivity(): boolean {
    return this.lesson.activities.length > this.activityIndex + 1;
  }

  private pViewModel = reactive({
    video: {
      show: false,
    },
  });

  public get viewModel() {
    return this.pViewModel;
  }

  // eslint-disable-next-line no-useless-constructor
  constructor(public lesson: DanceLesson, public videoPlayer: typeof VideoPlayer) {
  }

  playbackFinished() {
    if (this.hasNextActivity) this.playNextActivity();
  }

  playNextActivity() {
    this.activityIndex += 1;
  }
}
