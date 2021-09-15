<template>
  <div class="sheet-motion">
    <div
      class="motion-line has-text-centered"
      :style="{
        'flex-grow': getPhraseFlexGrow(i),
      }"
      v-for="(phrase, i) in data.phrases"
      :key="i">
      <!-- <div>{{phrase}}</div> -->

      <div class="motion-note" v-for="(kf, j) in phrase.frames" :key="kf"
      :style="{
        'background': getFrameBackground(i, j),
        'flex-grow': getFrameFlexGrow(i, j),
      }">

        <VideoPlayer
          :videoBaseUrl="dbEntry?.videoSrc + '#t=' + kf.timestamp"
          :fps="dbEntry?.fps ?? 30"
          :drawPoseLandmarks="drawMode === 'skeleton'"
          :videoOpacity="drawMode === 'video' && kf.type === 'move' ? 1.0 : 0.0"
          style="margin: 0; display:inline-block;background:lightgray;"/>
          <!-- {{kf}} -->

        <div class="motion-hold"></div>
          <!-- <p class="tag is-selectable">{{getFrameBackground(i, j)}}</p> -->
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
    getPhraseFlexGrow(phraseIndex: number) {
      if (!this.data.variableLength) return 0;

      const phrase = this.data.phrases[phraseIndex];
      if (!phrase) return 0;
      const nPhrase = this.data.phrases[phraseIndex + 1];
      if (!nPhrase) return 0;

      const phraseStartTime = phrase.frames[0]?.timestamp ?? Infinity;
      const nPhraseStartTime = nPhrase.frames[0]?.timestamp ?? Infinity;
      if (phraseStartTime === Infinity || nPhraseStartTime === Infinity) return 0;

      return nPhraseStartTime - phraseStartTime;
    },
    getFrameFlexGrow(phraseIndex: number, kfIndex: number) {
      if (!this.data.variableLength) return 0;

      const phrase = this.data.phrases[phraseIndex];
      if (!phrase) {
        console.warn(`NoteFlexGrow ${phraseIndex}-${kfIndex}: current phrase is undefined`);
        return 0;
      }
      const nPhrase = this.data.phrases[phraseIndex + 1];

      const curFrame = phrase.frames[kfIndex];
      if (!curFrame) {
        console.warn(`NoteFlexGrow ${phraseIndex}-${kfIndex}: current kf is undefined`);
        return 0;
      }
      const kf = curFrame.timestamp;
      let nextKf = phrase.frames[kfIndex + 1]?.timestamp ?? Infinity;
      if (nextKf === Infinity && nPhrase) {
        nextKf = nPhrase.frames[0]?.timestamp ?? Infinity;
      }
      if (nextKf === Infinity) {
        // console.log(`NoteFlexGrow ${phraseIndex}-${kfIndex}: next kf is undefined`);
        return 0;
      }

      const res = nextKf - kf;
      if (res < 0) {
        console.log(`NoteFlexGrow ${phraseIndex}-${kfIndex}: next kf is before this one`);
        return 0;
      }
      return res * 100;
    },
    getFrameBackground(phraseIndex: number, kfIndex: number) {
      const phrase = this.data.phrases[phraseIndex];
      if (!phrase) return 1.0;

      // const prev = phrase.frames[index - 1] ?? -Infinity;
      const curr = phrase.frames[kfIndex]?.timestamp ?? -Infinity;
      let next = phrase.frames[kfIndex + 1]?.timestamp ?? Infinity;
      if (next === Infinity) {
        const nPhrase = this.data.phrases[phraseIndex + 1];
        if (nPhrase) {
          next = nPhrase.frames[0]?.timestamp ?? Infinity;
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
