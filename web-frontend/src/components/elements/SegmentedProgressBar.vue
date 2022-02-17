<template>
  <div class="segmented-progress-bar is-relative">
    <progress
      v-for="seg in segmentsData"
      :key="seg.id"
      :class="[{ 'is-disabled': !enableAll && !seg.enabled, [seg.cssClass]: enableAll || seg.enabled, 'is-dark': !enableAll && !seg.enabled}, ]"
      class="progress is-large"
      :max="seg.max - seg.min"
      :value="progress - seg.min"
      :style="{ 'flex-grow': (seg.max - seg.min) }"
    ></progress>
    <div class="is-absolute is-overlay is-flex">
      <div
        v-for="seg in segmentsData"
        :key="seg.id"
        :style="{ 'flex-grow': (seg.max - seg.min) }"
        class="has-text-centered label-div"
        :class="{'is-active': seg.enabled}">
        {{seg.label}}
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, computed, toRefs } from 'vue';
import MiniLesson, { MiniLessonActivity } from '@/model/MiniLesson';

export interface ProgressSegmentData {
  min: number;
  max: number;
  enabled: boolean;
  label: string;
}

export function calculateProgressSegments(lesson: MiniLesson, activity: MiniLessonActivity) {
  if (!lesson) return [];

  const allLabels = lesson.segmentLabels ?? [];
  let last = undefined as undefined | number;
  const segs = lesson.segmentBreaks.map((timestamp, i) => {
    let segData = undefined as undefined | ProgressSegmentData;
    const label = allLabels[i - 1] ?? '';
    if (last !== undefined) {
      const doesOverlap = Math.max(last, activity.startTime) < Math.min(timestamp, activity.endTime);
      segData = {
        label,
        min: last,
        max: timestamp,
        enabled: activity?.focusedSegments ? activity.focusedSegments.indexOf(i - 1) !== -1 : doesOverlap,
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

  progress.progress, .label-div {
    border-radius: 0.5rem;
    flex-basis: 10px;
    margin-bottom: auto;
  }

  .label-div.is-active {
    font-weight: 700;
  }

  progress.progress {
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
