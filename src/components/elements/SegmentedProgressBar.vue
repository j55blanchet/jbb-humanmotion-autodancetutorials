<template>
  <div class="segmented-progress-bar">
    <progress
      v-for="seg in segmentsData"
      :key="seg.id"
      :class="[{ 'is-disabled': !seg.enabled}, seg.cssClass]"
      class="progress is-large"
      :max="seg.max - seg.min"
      :value="progress - seg.min"
      :style="{ 'flex-grow': (seg.max - seg.min) }"
    ></progress>
  </div>
  <div>{{progress}}</div>
  <p v-for="seg in segmentsData"
  :key="seg.id">{{seg.min}}-{{seg.max}}</p>
</template>

<script lang="ts">
import { defineComponent, computed, toRefs } from 'vue';

export interface ProgressSegmentData {
  min: number;
  max: number;
  enabled: boolean;
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
