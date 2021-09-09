<template>
  <div class="sheet-motion">
    <div
      class="motion-line has-text-centered"
      v-for="(stage, i) in data.kfsByStage"
      :key="i">

      <div class="motion-note" v-for="(kf, j) in stage" :key="kf"
      :style="{
        'background': getKFBackground(i, j),
      }">

        <VideoPlayer
          :videoBaseUrl="dbEntry?.videoSrc + '#t=' + kf"
          :fps="dbEntry?.fps ?? 30"
          :drawPoseLandmarks="drawMode === 'skeleton'"
          :videoOpacity="drawMode === 'video' ? 1.0 : 0.0"/>

          <!-- <p class="tag is-selectable">{{getKFBackground(i, j)}}</p> -->
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';

import VideoPlayer from '@/components/elements/VideoPlayer.vue';

function constrain(val: number, min: number, max: number) {
  return Math.min(Math.max(val, min), max);
}
function remap(val: number, min: number, max: number, newMin: number, newMax: number) {
  return ((val - min) / (max - min)) * (newMax - newMin) + newMin;
}

export default defineComponent({
  name: 'SheetMotion',
  components: {
    VideoPlayer,
  },
  props: {
    dbEntry: {
      type: Object,
      required: true,
    },
    currentTime: {
      type: Number,
      default: -1,
    },
    drawMode: {
      type: String,
      default: 'video',
    },
    data: {
      type: Object,
      default: () => ({
        kfsByStage: [[]],
      }),
    },
    fadeInDurationSecs: {
      type: Number,
      default: 1.0,
    },
    fadeOutDurationSecs: {
      type: Number,
      default: 1.0,
    },
  },
  methods: {
    isActive(kf: number, nextkf: number) {
      return this.currentTime >= kf && this.currentTime < nextkf;
    },
    getKFBackground(stageIndex: number, index: number) {
      const stage = this.data.kfsByStage[stageIndex];
      if (!stage) return 1.0;

      // const prev = stage[index - 1] ?? -Infinity;
      const curr = stage[index];
      const next = stage[index + 1] ?? Infinity;

      // https://gist.github.com/gre/1650294

      if (this.currentTime === -1) return 'none';
      if (this.currentTime < curr) {
        const timeUntil = curr - this.currentTime;
        let fadePercent = constrain(timeUntil / this.fadeInDurationSecs, 0, 1);
        fadePercent *= (2 - fadePercent);
        const saturation = remap(fadePercent, 0, 1, 80.0, 0.0);
        return `hsl(171, ${saturation}%, 50%)`;
      }
      if (this.currentTime < next) return 'hsl(171, 100%, 50%)';

      const timePassed = this.currentTime - curr;
      const fadePercent = constrain(timePassed / this.fadeOutDurationSecs, 0, 1);
      const brightness = remap(fadePercent, 0, 1, 50.0, 26.0);
      const saturation = remap(fadePercent, 0, 1, 100.0, 0.0);
      return `hsl(171, ${saturation}%, ${brightness}%)`;
    },
  },
});
</script>

<style lang="scss">

.sheet-motion {
  max-height: 100%;
  overflow-y: scroll;
  .motion-line {
    .motion-note {
      width: 8rem;
      display: inline-block;
      padding: 0.5rem;
      margin: 0.25rem;
      border-radius: 0.25rem;

      transition: background-color 0.1s;
    }
  }
}
</style>
