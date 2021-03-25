<template>
  <div class="learning-screen"
    :class="{'background-blur': !activityFinished}"
    >
    <teleport to="#topbarLeft">
      <button class="button" @click="$emit('back-selected')">&lt; Back</button>
    </teleport>
    <teleport to="#topbarRight">
      <span class="tag">{{activityId}} / {{activityCount}}</span>
      <progress class="lessonProgress progress ml-2" :max="activityCount" :value="activityId">
      </progress>
    </teleport>
    <teleport to="#topbarCenter">
        <h3>{{activityTitle}}</h3>
    </teleport>

    <PausingVideoPlayer
      :videoSrc="targetDance.videoSrc"
      :height="'720px'"
      ref="videoPlayer"
      @progress="onTimeChanged"
      @playback-completed="onActivityFinished"
      @pause-hit="onPauseHit"
      @pause-end="onPauseEnded"
    />

    <div class="overlay instructions-overlay mb-4">
      <InstructionCarousel :instructions="instructions" class="m-2"/>
      <InstructionCarousel :instructions="timedInstructions" class="m-2"/>
    </div>

    <div class="vcenter-parent overlay" v-show="activityFinished">
      <div class="content translucent-text p-6 is-rounded">
        <h3 class="has-text-white">Use a gesture to proceed</h3>
        <div class="columns">
            <div class="column">
              <p class="mt-4 mb-0">Repeat</p>
              <span class="icon is-large fa-flip-horizontal">
                <i class="fas fa-2x fa-hand-paper fa-rotate-90"></i>
              </span>
              <br>
              <p class="mt-4 has-text-grey-lighter">{{activityTitle}}</p>
            </div>
            <div class="column">
              <p class="mt-4 mb-0">Next</p>
              <span class="icon is-large" >
                <i class="fas fa-2x fa-hand-paper fa-rotate-90"></i>
              </span>
              <br>
              <p class="mt-4 has-text-grey-lighter">{{nextActivityTitle}}</p>
            </div>
          </div>
      </div>
    </div>

    <teleport to="#belowSurface">
      <div>
        <div class="master-bar mt-4">
          <SegmentedProgressBar
            :segments="progressSegments"
            :progress="videoTime"
            ref="progressBar"
          />
        </div>
      </div>
    </teleport>
  </div>
</template>

<script lang="ts">
import DanceLesson, { PauseInfo } from '@/model/DanceLesson';
import {
  computed, defineComponent, onMounted, ref, toRefs,
} from 'vue';
import { GestureNames, setupGestureListening, TrackingActions } from '@/services/EventHub';
import DanceEntry from '@/model/DanceEntry';
import InstructionCarousel, { Instruction } from '@/components/elements/InstructionCarousel.vue';
import SegmentedProgressBar, { ProgressSegmentData } from '../elements/SegmentedProgressBar.vue';
import PausingVideoPlayer from '../elements/PausingVideoPlayer.vue';

const ActivityPlayState = Object.freeze({
  NotStarted: 'NotStarted',
  Playing: 'Playing',
  ActivityEnded: 'ActivityEnded',
});

//
// TODO!
//   * Update segment breaks in activity to have the first activity
//     start time and the last activity end time.
//

function calculateProgressSegments(dance: DanceEntry, lesson: DanceLesson) {
  if (!lesson) return [];

  let last = undefined as undefined | number;
  const segs = lesson.segmentBreaks.map((timestamp) => {
    let segData = undefined as undefined | ProgressSegmentData;
    if (last !== undefined) {
      segData = {
        min: last,
        max: timestamp,
        enabled: true,
      };
    }
    last = timestamp;
    return segData;
  }).filter((x) => x !== undefined);

  return segs;
}

export default defineComponent({
  components: {
    SegmentedProgressBar,
    PausingVideoPlayer,
    InstructionCarousel,
  },
  props: {
    targetDance: Object,
    targetLesson: Object,
  },
  setup(props, { emit }) {
    const { targetLesson, targetDance } = toRefs(props);

    const activityState = ref(ActivityPlayState.NotStarted);

    const videoPlayer = ref(null as null | typeof PausingVideoPlayer);
    const videoTime = ref(0);

    const progressBar = ref(null as null | typeof SegmentedProgressBar);

    const activityId = ref(0);
    const activity = computed(() => {
      const lesson = targetLesson?.value as unknown as DanceLesson | null;
      return lesson?.activities[activityId.value];
    });
    const activityTitle = computed(() => activity.value?.title ?? '');
    const activityCount = computed(() => {
      const lesson = targetLesson?.value as unknown as DanceLesson | null;
      return lesson?.activities?.length ?? 0;
    });
    const hasNextActivity = computed(() => activityCount.value > activityId.value + 1);
    const activityFinished = computed(() => activityState.value === ActivityPlayState.ActivityEnded);
    const nextActivityTitle = computed(() => {
      if (!hasNextActivity.value) return 'Finish Lesson';
      const lesson = targetLesson?.value as unknown as DanceLesson | null;

      const nextActivity = lesson?.activities[activityId.value + 1];
      return nextActivity?.title ?? 'Unknown';
    });

    const pauseInstructs = ref([] as Instruction[]);
    function onPauseHit(pause: PauseInfo) {
      if (pause.instruction) {
        pauseInstructs.value.push({
          id: pause.time,
          text: pause.instruction,
        });
      }
    }
    function onPauseEnded() {
      // Remove all pause instructions
      pauseInstructs.value.splice(0);
    }

    const instructions = computed(() => {
      const mActivity = activity.value;
      const state = activityState.value;
      if (!mActivity) return [];

      const instructs: Instruction[] = [];

      if (mActivity.staticInstruction) {
        instructs.push({
          id: 0,
          text: mActivity.staticInstruction,
        });
      }

      if (state === ActivityPlayState.NotStarted && mActivity.startInstruction) {
        instructs.push({
          id: 1,
          text: mActivity.startInstruction,
        });
      } else if (state !== ActivityPlayState.NotStarted && mActivity.playingInstruction) {
        instructs.push({
          id: 2,
          text: mActivity.playingInstruction,
        });
      }

      return instructs;
    });
    const timedInstructions = computed(() => {
      const mActivity = activity.value;
      const time = videoTime.value;
      if (!mActivity) return [];

      const activeTimedInstructions = mActivity.timedInstructions?.map(
        (ti, i) => ({
          id: i,
          text: ti.text,
          start: ti.startTime,
          end: ti.endTime,
        })
      ).filter((ti) => ti.start <= time && time < ti.end) ?? [];

      return activeTimedInstructions;
    });

    const progressSegments = computed(() => {
      const lesson = targetLesson?.value as DanceLesson | undefined;
      const dance = targetDance?.value as DanceEntry | undefined;
      if (lesson && dance) return calculateProgressSegments(dance, lesson);
      return [];
    });

    function playActivity() {
      console.log(`LEARNING SCREEN:: Starting playback (activityId: ${activityId.value})`);
      activityState.value = ActivityPlayState.Playing;
      const vidPlayer = videoPlayer.value;
      const vidActivity = activity.value;
      if (!vidPlayer || !vidActivity) {
        console.error('LEARNING SCREEN:: Aborting video playback: videoElement or lessonActivity is null', vidPlayer, vidActivity);
        return;
      }

      vidPlayer.play(
        vidActivity.startTime,
        vidActivity.endTime,
        (vidActivity.practiceSpeeds ?? [1])[0] ?? 1,
        vidActivity.pauses ?? [],
        1.5,
      );
    }

    function gotoNextActivity() {
      activityState.value = ActivityPlayState.NotStarted;
      if (!hasNextActivity.value) {
        emit('lesson-completed');
        return;
      }
      activityId.value += 1;
      setTimeout(() => { playActivity(); }, 1000);
    }

    function onActivityFinished() {
      activityState.value = ActivityPlayState.ActivityEnded;
      console.log('LEARNING SCREEN:: Activity finished. Requesting tracking...');
      TrackingActions.requestTracking();
    }

    setupGestureListening({
      [GestureNames.pointRight]: () => {
        TrackingActions.endTrackingRequest();
        if (!activityFinished.value) return;
        gotoNextActivity();
      },
      [GestureNames.pointLeft]: () => {
        TrackingActions.endTrackingRequest();
        if (!activityFinished.value) return;
        playActivity();
      },
    });
    // Todo: quit tracking request when component unmounted. (perhaps
    //       refactor tracking requests to have an id)

    function onTimeChanged(time: number) {
      videoTime.value = time;
    }

    onMounted(() => {
      setTimeout(() => {
        playActivity();
      }, 1000);
    });

    return {
      activityState,
      progressSegments,
      activity,
      activityId,
      activityCount,
      activityTitle,
      nextActivityTitle,
      instructions,
      timedInstructions,
      videoPlayer,
      progressBar,
      activityFinished,
      videoTime,
      onActivityFinished,
      onTimeChanged,

      onPauseHit,
      onPauseEnded,
    };
  },
});
</script>

<style lang="scss">

.learning-screen {
  position: relative;
  width: 100%;
  height: 100%;
}

.master-bar {
  width: 1280px;
  // margin: 0 auto;
  // padding: 1rem 1rem 1rem 1rem;
  // border-radius: 0 0 0.5rem 0.5rem;
}

.instructions-overlay {
  display: flex;
  flex-direction: column-reverse;
  align-items: center;
  justify-content: flex-start;
}

.lessonProgress {
  width: 128px;
}
</style>
