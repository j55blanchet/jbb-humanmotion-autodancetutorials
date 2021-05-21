<template>
  <div class="segmented-progress-bar">
    <progress
      v-for="seg in segmentsData"
      :key="seg.id"
      :class="[{ 'is-disabled': !enableAll && !seg.enabled, [seg.cssClass]: enableAll || seg.enabled, 'is-dark': !enableAll && !seg.enabled}, ]"
      class="progress is-large"
      :max="seg.max - seg.min"
      :value="progress - seg.min"
      :style="{ 'flex-grow': (seg.max - seg.min) }"
    ></progress>
  </div>
</template>

<script lang="ts">
import { defineComponent, computed, toRefs } from 'vue';
import DanceLesson, { Activity } from '@/model/DanceLesson';

export interface ProgressSegmentData {
  min: number;
  max: number;
  enabled: boolean;
}

export function calculateProgressSegments(lesson: DanceLesson, activity: Activity) {
  if (!lesson) return [];

  let last = undefined as undefined | number;
  const segs = lesson.segmentBreaks.map((timestamp, i) => {
    let segData = undefined as undefined | ProgressSegmentData;
    if (last !== undefined) {
      segData = {
        min: last,
        max: timestamp,
        enabled: activity?.focusedSegments ? activity.focusedSegments.indexOf(i - 1) !== -1 : true,
      };
    }
    last = timestamp;
    return segData;
  }).filter((x) => x !== undefined);

  return segs as ProgressSegmentData[];
}

const cssClassOptions = [
  'is-info',
  'is-success',
  'is-warning',
  'is-primary',
  'is-danger',
];

export default defineComponent({
  name: 'SegmentedProgressBar',
  props: {
    segments: {
      default: Array,
      type: Array,
    },
    progress: {
      default: 0,
      type: Number,
    },
    enableAll: {
      default: false,
      type: Boolean,
    },
  },
  setup(props) {
    const {
      segments,
    } = toRefs(props);

    const segmentsData = computed(
      () => segments.value.map(
        (seg, i) => ({
          id: i,
          cssClass: cssClassOptions[i % cssClassOptions.length],
          ...(seg as ProgressSegmentData),
        }),
      ),
    );

    return {
      segmentsData,
    };
  },
});

</script>

<style lang="scss">
.segmented-progress-bar {
  display: flex;
  flex-direction: row;
  width: 100%;

  progress.progress {
    border-radius: 0.5rem;
    flex-basis: 10px;
    margin-bottom: auto;
    // border: 2px solid #BBB;

    -webkit-appearance: none;
    appearance: none;

    &.is-disabled::-webkit-progress-bar,
    &.is-disabled {
      background: #888;
    }

    &.is-disabled::-moz-progress-bar,
    &.is-disabled::-webkit-progress-value,
    &.is-disabled::-ms-fill {
      background: #888;
    }
  }
}
</style>
