<template>
  <div class="learning-screen"
    :class="{'background-blur': !activityFinished}"
    >
    <teleport to="#topbarLeft">
      <button class="button" @click="$emit('back-selected')">&lt; Back</button>
    </teleport>
    <teleport to="#topbarRight">
      <span>#{{activityId}} / {{activityCount}}: {{activityTitle}}</span>
      <progress class="progress" :max="activityCount" value="5"></progress>
    </teleport>

    <VideoPlayer
      :videoBaseUrl="targetDance.videoSrc"
      :height="'720px'"
      ref="videoPlayer"
      v-show="!activityFinished"
      v-on:video-progressed="onTimeChanged"
      v-on:playback-finished="onActivityFinished"
    />

    <div class="overlay" v-show="activityFinished">
      <div class="card">
        <div class="card-header">
          <h3 class="card-header-title">Use a gesture to proceed</h3>
        </div>
      </div>
    </div>

    <teleport to="#belowSurface">
      <div>
        <div class="master-bar">
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
import DanceLesson from '@/model/DanceLesson';
import {
  computed, defineComponent, onMounted, ref, toRefs,
} from 'vue';
import { GestureNames, setupGestureListening, TrackingActions } from '@/services/EventHub';
import DanceEntry from '@/model/DanceEntry';
import SegmentedProgressBar, { ProgressSegmentData } from '../elements/SegmentedProgressBar.vue';
import VideoPlayer from '../elements/VideoPlayer.vue';

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
    if (last) {
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
    VideoPlayer,
  },
  props: {
    targetDance: Object,
    targetLesson: Object,
  },
  setup(props, { emit }) {
    const { targetLesson, targetDance } = toRefs(props);

    const videoPlayer = ref(null as null | typeof VideoPlayer);
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
    const activityFinished = ref(false);

    const progressSegments = computed(() => {
      const lesson = targetLesson?.value as DanceLesson | undefined;
      const dance = targetDance?.value as DanceEntry | undefined;
      if (lesson && dance) return calculateProgressSegments(dance, lesson);
      return [];
    });

    function playActivity() {
      console.log(`LEARNING SCREEN:: Starting playback (activityId: ${activityId.value})`);
      activityFinished.value = false;
      const vidPlayer = videoPlayer.value;
      const vidActivity = activity.value;
      if (!vidPlayer || !vidActivity) {
        console.error('LEARNING SCREEN:: Aborting video playback: videoElement or lessonActivity is null', vidPlayer, vidActivity);
        return;
      }

      vidPlayer.playVideo(
        vidActivity.startTime,
        vidActivity.endTime,
        (vidActivity.practiceSpeeds ?? [1])[0] ?? 1,
      );
    }

    function gotoNextActivity() {

      if (!hasNextActivity.value) {
        emit('lesson-completed');
        return;
      }
      activityId.value += 1;
      setTimeout(() => { playActivity(); }, 1000);
    }

    function onActivityFinished() {
      activityFinished.value = true;
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

    function onTimeChanged(time: number) {
      videoTime.value = time;
    }

    onMounted(() => {
      setTimeout(() => {
        playActivity();
      }, 1000);
    });

    return {
      progressSegments,
      activity,
      activityId,
      activityCount,
      activityTitle,
      videoPlayer,
      progressBar,
      activityFinished,
      videoTime,
      onActivityFinished,
      onTimeChanged,
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
  margin: 0 auto;
  padding: 1rem 1rem 1rem 1rem;
  border-radius: 0 0 0.5rem 0.5rem;
}

</style>
