<template>
  <div class="segmented-progress-bar">
    <progress
      v-for="seg in segments"
      :key="seg.i"
      :class="[seg.isEnabled ? seg.cssClass : '', seg.disabledCss]"
      class="progress is-large"
      :max="seg.max"
      :min="seg.min"
      :value="progressValue(seg.id)"
      :style="{ 'flex-grow': seg.max }"
    ></progress>
  </div>
</template>

<script lang="ts">
import { defineComponent, computed, toRefs } from 'vue';

interface ProgressSegment {
  offset: number;
  id: number;
  max: number;
  cssClass: string;
  disabledCss: string;
  isEnabled: boolean;
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
    mins: Array,
    maxes: Array,
    value: {
      default: 0,
      type: Number,
    },
    disabled: Array,
  },
  setup(props) {
    const {
      mins, maxes, value, disabled,
    } = toRefs(props);

    const segments = computed(() => {
      const segMins = mins?.value as number[];
      const segMaxes = maxes?.value as number[];

      if (!segMins || !segMaxes) return [];

      const count = Math.min(segMins.length, segMaxes.length);
      if (segMins.length !== segMaxes.length) {
        console.error("Lengths of properties don't match up");
      }

      const segs: ProgressSegment[] = [];
      const disabledBars = (disabled ?? []) as number[];
      for (let i = 0; i < count; i += 1) {
        const isDisabled = (disabledBars.indexOf(i) !== -1);
        segs.push({
          id: i,
          offset: segMins[i],
          max: segMaxes[i] - segMins[i],
          cssClass: cssClassOptions[i % cssClassOptions.length],
          disabledCss: isDisabled ? 'is-disabled' : 'is-enabled',
          isEnabled: !isDisabled,
        });
      }
      return segs;
    });

    function progressValue(id: number) {
      const seg = segments.value[id];
      if (!seg) return 0;
      return value.value - seg.offset;
    }

    return {
      segments,
      progressValue,
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
