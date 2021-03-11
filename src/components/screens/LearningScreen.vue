<template>
  <div class="learning-screen"
    :class="{'background-blur': !awaitingGesture}"
    >
    <teleport to="#topbarLeft">
      <button class="button" @click="$emit('back-selected')">&lt; Back</button>
    </teleport>

    <VideoPlayer
      :videoBaseUrl="targetDance.videoSrc"
      :height="'720px'"
    />

    <teleport to="#belowSurface">
      <div class="master-bar">
        <SegmentedProgressBar
          :segments="progressSegments"
          :value="2.5"
        />
      </div>
    </teleport>
  </div>
</template>

<script lang="ts">
import DanceEntry from '@/model/DanceEntry';
import DanceLesson from '@/model/DanceLesson';
import {
  ref, computed, defineComponent, toRefs,
} from 'vue';
import SegmentedProgressBar, { ProgressSegmentData } from '../elements/SegmentedProgressBar.vue';
import VideoPlayer from '../elements/VideoPlayer.vue';

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
    const { targetDance, targetLesson } = toRefs(props);

    const awaitingGesture = ref(false);

    const progressSegments = computed(() => {
      const lesson = targetLesson?.value as DanceLesson | undefined;
      if (!lesson) return [];

      let last = 0;
      return lesson.segmentBreaks.map((timestamp) => {
        const segData: ProgressSegmentData = {
          min: last,
          max: timestamp,
          enabled: true,
        };
        last = timestamp;
        return segData;
      });
    });
    return {
      progressSegments,
      awaitingGesture,
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
