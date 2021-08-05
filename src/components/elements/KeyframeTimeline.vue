<template>
  <div class="keyframe-timeline-container">
    <div class="timeline">
      <!-- {{dbEntry.title}} -->

      <!-- <span class="item">
        <VideoPlayer :videoBaseUrl="dbEntry?.videoSrc + '#t=' + currentKeyframe"
          :videoOpacity="displayMode === 'video' ? 1.0 : 0"
          :setDrawStyle="setKFSkeletonDrawStyle"
          :fps="dbEntry.fps"
          :drawPoseLandmarks="displayMode === 'skeleton'"/>
      </span> -->
      <span
        class="item"
        v-for="(kfitem) in nearFutureKeyframes"
        :key="kfitem.kf"
        :style="{
          'left': 100 * kfitem.percentAcross + '%',
        }">
        <VideoPlayer
          :videoBaseUrl="dbEntry?.videoSrc + '#t=' + kfitem.kf"
          :fps="dbEntry.fps"
          :drawPoseLandmarks="displayMode === 'skeleton'"
          :videoOpacity="displayMode === 'video' ? 1.0 : 0"
          :setDrawStyle="setKFSkeletonDrawStyle"
        />
        </span>
      <!-- <span
        class="item"
        v-for="(kfitem, i) in farFutureKeyframes"
        :key="i"
        :style="{
          'right': (i*10) + 'px',
          'z-index': -i,
        }"
        >{{farFutureKeyframes.length}}</span> -->
    </div>
  </div>
</template>

<script lang="ts">

import {
  computed,
  defineComponent, Ref, toRefs,
} from 'vue';

import VideoPlayer from '@/components/elements/VideoPlayer.vue';

export default defineComponent({
  name: 'KeyframeTimeline',
  components: {
    VideoPlayer,
  },
  props: {
    displayMode: {
      type: String,
      default: 'video',
    },
    dbEntry: {
      type: Object,
      required: true,
    },
    keyframes: {
      type: Array,
      default: () => [],
    },
    currentTime: {
      type: Number,
      default: 0,
    },
    activeTimelineSecs: {
      type: Number,
      default: 5,
    },
    maxStackItems: {
      type: Number,
      default: 3,
    },
  },
  setup(props) {
    const {
      keyframes, currentTime, activeTimelineSecs, maxStackItems,
    } = toRefs(props);

    const keyframesTyped = keyframes as Ref<number[]>;

    const currentKeyframe = computed(() => keyframesTyped.value.find((kf, index) => kf < currentTime.value && (keyframesTyped.value[index + 1] === undefined || keyframesTyped.value[index + 1] >= currentTime.value)) ?? keyframesTyped.value[0] ?? null);

    const futureKeyframes = computed(() => keyframesTyped.value
      .map((kf) => ({
        timeRemaining: kf - currentTime.value,
        kf,
      }))
      .filter((item) => item.timeRemaining > 0));

    const nearFutureKeyframes = computed(
      () => {
        const current = [{
          kf: currentKeyframe.value,
          timeRemaining: 0,
        }];
        const upcoming = futureKeyframes.value
          .filter(({ timeRemaining }) => timeRemaining < activeTimelineSecs.value)
          .map((item) => ({ ...item, percentAcross: item.timeRemaining / activeTimelineSecs.value }));
        return current.concat(upcoming);
      },
    );
    const farFutureKeyframes = computed(() => futureKeyframes.value.filter(({ timeRemaining }) => timeRemaining >= activeTimelineSecs.value).slice(0, maxStackItems.value + 1));

    return {
      currentKeyframe,
      futureKeyframes,
      nearFutureKeyframes,
      farFutureKeyframes,

      setKFSkeletonDrawStyle: (canvasCtx: CanvasRenderingContext2D) => {
        canvasCtx.strokeStyle = 'rgba(100, 150, 150, 0.9)';
        canvasCtx.lineWidth = 3.5;
        canvasCtx.lineCap = 'round';
      },
    };
  },
});
</script>

<style lang="scss">

.keyframe-timeline-container {
  position: relative;
  // height: 50%;
  // margin-top: 25%;
  width: 100%;

  .timeline {
    // padding-top: 25%;
    height: 14rem;
    // background: gray;
    position: relative;

    .item {
      display: block;
      // background: lightgray;
      position: absolute;
      height: 100%;
      min-width: 1rem;
      border-radius: 0.25rem;
      border: 1px sold lightgray;
    }

    .placeholder {
      display: block;
      position: absolute;
      height: 100%;
      min-width: 1rem;
      border-radius: 0.25rem;
      border: 1px solid gray;
    }
  }
}
</style>
