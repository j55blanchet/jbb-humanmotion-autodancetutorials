<template>
  <div class="sheet-motion">
    <div
      class="motion-line has-text-centered"
      :style="{
        'flex-grow': getStageFlexGrow(i),
      }"
      v-for="(stage, i) in data.kfsByStage"
      :key="i">

      <div class="motion-note" v-for="(kf, j) in stage" :key="kf"
      :style="{
        'background': getKFBackground(i, j),
        'flex-grow': getNoteFlexGrow(i, j),
      }">

        <VideoPlayer
          :videoBaseUrl="dbEntry?.videoSrc + '#t=' + kf"
          :fps="dbEntry?.fps ?? 30"
          :drawPoseLandmarks="drawMode === 'skeleton'"
          :videoOpacity="drawMode === 'video' ? 1.0 : 0.0"
          style="margin: 0; display:inline-block;"/>

        <div class="motion-hold"></div>
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
      default: 0.5,
    },
    fadeOutDurationSecs: {
      type: Number,
      default: 0.5,
    },
  },
  methods: {
    isActive(kf: number, nextkf: number) {
      return this.currentTime >= kf && this.currentTime < nextkf;
    },
    getStageFlexGrow(stageIndex: number) {
      const stage = this.data.kfsByStage[stageIndex];
      if (!stage) return 0;
      const nStage = this.data.kfsByStage[stageIndex + 1];
      if (!nStage) return 0;

      const stageStartTime = stage[0] ?? Infinity;
      const nStageStartTime = nStage[0] ?? Infinity;
      if (stageStartTime === Infinity || nStageStartTime === Infinity) return 0;

      return nStageStartTime - stageStartTime;
    },
    getNoteFlexGrow(stageIndex: number, kfIndex: number) {
      const stage = this.data.kfsByStage[stageIndex];
      if (!stage) {
        console.warn(`NoteFlexGrow ${stageIndex}-${kfIndex}: current stage is undefined`);
        return 0;
      }
      const nStage = this.data.kfsByStage[stageIndex + 1];

      const kf = stage[kfIndex];
      if (!kf) {
        console.warn(`NoteFlexGrow ${stageIndex}-${kfIndex}: current kf is undefined`);
        return 0;
      }
      let nextKf = stage[kfIndex + 1] ?? Infinity;
      if (nextKf === Infinity && nStage) {
        nextKf = nStage[0] ?? Infinity;
      }
      if (nextKf === Infinity) {
        console.log(`NoteFlexGrow ${stageIndex}-${kfIndex}: next kf is undefined`);
        return 0;
      }

      const res = nextKf - kf;
      if (res < 0) {
        console.log(`NoteFlexGrow ${stageIndex}-${kfIndex}: next kf is before this one`);
        return 0;
      }
      return res * 100;
    },
    getKFBackground(stageIndex: number, kfIndex: number) {
      const stage = this.data.kfsByStage[stageIndex];
      if (!stage) return 1.0;

      // const prev = stage[index - 1] ?? -Infinity;
      const curr = stage[kfIndex];
      let next = stage[kfIndex + 1] ?? Infinity;
      if (next === Infinity) {
        const nStage = this.data.kfsByStage[stageIndex + 1];
        if (nStage) {
          next = nStage[0] ?? Infinity;
        }
      }

      // https://gist.github.com/gre/1650294

      if (this.currentTime === -1) return 'none';
      if (this.currentTime < curr) {
        const timeUntil = curr - this.currentTime;
        let fadePercent = constrain(timeUntil / this.fadeInDurationSecs, 0, 1);
        fadePercent *= (2 - fadePercent);
        const saturation = remap(fadePercent, 0, 1, 80.0, 0.0);
        return `hsl(171, ${saturation}%, 90%)`;
      }
      if (this.currentTime < next) return 'hsl(171, 100%, 50%)';

      const timePassed = this.currentTime - curr;
      const fadePercent = constrain(timePassed / this.fadeOutDurationSecs, 0, 1);
      const brightness = remap(fadePercent, 0, 1, 50.0, 90.0);
      const saturation = remap(fadePercent, 0, 1, 100.0, 0.0);
      return `hsl(171, ${saturation}%, ${brightness}%)`;
    },
  },
});
</script>

<style lang="scss">

.sheet-motion {
  max-height: 100%;
  overflow-y: auto;
  display: flex;
  flex-flow: row wrap;

  .motion-line {

    display: inline-flex;
    flex-flow: row wrap;

    border-top: 0.125rem solid #333;
    border-bottom: 0.125rem solid #333;
    border-right: 0.125rem solid #333;
    border-left: 0.125rem solid #333;
    padding: 1rem 1rem;
    flex-grow: 1;

    .motion-note {
      // width: 8rem;
      display: flex;
      flex-flow: row nowrap;
      padding: 0.5rem;
      margin: 0.25rem;
      border-radius: 0.25rem;
      height: 15rem;
      text-align:left;
      align-items: center;

      transition: background-color 0.1s;

      .motion-hold {
        display: inline-block;
        // width: 100%;
        height: 0.25rem;
        border-radius: 999999rem;;
        background: #777;
        flex-grow: 1;
        flex-basis: 0;
      }
    }

    &:first-child {
      border-left: 1rem solid #333;
    }

    &:last-child {
      border-right: 1rem solid #333;
    }
  }
}
</style>
