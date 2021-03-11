<template>
  <div class="learning-screen"
    :class="{'background-blur': !awaitingGesture}"
    >
    <teleport to="#topbarLeft">
      <button class="button" @click="$emit('back-selected')">&lt; Back</button>
    </teleport>
    <teleport to="#topbarRight">
      <progress class="progress" :max="targetLesson.activities.count" value="5"></progress>
    </teleport>

    <VideoPlayer
      :videoBaseUrl="targetDance.videoSrc"
      :height="'720px'"
      ref="videoPlayer"
    />

    <teleport to="#belowSurface">
      <div class="master-bar">
        <SegmentedProgressBar
          :segments="progressSegments"
          :value="videoTime"
          ref="progressBar"
        />
      </div>
    </teleport>
  </div>
</template>

<script lang="ts">
import DanceLesson from '@/model/DanceLesson';
import {
  computed, defineComponent, onMounted, ref, toRefs,
} from 'vue';
import { setupGestureListening } from '@/services/EventHub';
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

  let last = 0;
  const segs = lesson.segmentBreaks.map((timestamp) => {
    const segData: ProgressSegmentData = {
      min: last,
      max: timestamp,
      enabled: true,
    };
    last = timestamp;
    return segData;
  });
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
  setup(props) {
    const { targetLesson, targetDance } = toRefs(props);

    const videoPlayer = ref(null as null | typeof VideoPlayer);
    const videoTime = ref(0);

    const progressBar = ref(null as null | typeof SegmentedProgressBar);

    const activityId = ref(0);
    const activity = computed(() => {
      const lesson = targetLesson?.value as unknown as DanceLesson | null;
      return lesson?.activities[activityId.value];
    });
    const activityFinished = ref(false);

    const progressSegments = computed(() => {
      const lesson = targetLesson?.value as DanceLesson | undefined;
      const dance = targetDance?.value as DanceEntry | undefined;
      if (lesson && dance) return calculateProgressSegments(dance, lesson);
      return [];
    });

    setupGestureListening({});

    function onActivityFinished() {
      activityFinished.value = false;
      console.log('LEARNING SCREEN:: Activity finished');
    }
    function onTimeChanged(time: number) {
      videoTime.value = time;
    }

    onMounted(() => {
      setTimeout(() => {
        console.log('LEARNING SCREEN:: Starting playback');
        const vidPlayer = videoPlayer.value;
        const vidActivity = activity.value;
        if (!vidPlayer || !vidActivity) {
          console.error('LEARNING SCREEN:: Aborting video playback: videoElement or lessonActivity is null', vidPlayer, vidActivity);
          return;
        }

        vidPlayer.playVideo(
          vidActivity.startTime,
          vidActivity.endTime,
          1,
          onActivityFinished,
          onTimeChanged,
        );
      }, 1000);
    });

    return {
      progressSegments,
      activity,
      videoPlayer,
      progressBar,
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
