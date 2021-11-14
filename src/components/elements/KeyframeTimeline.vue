<template>
  <div class="keyframe-timeline-container">
    <div class="timeline">
      <!-- {{dbEntry.title}} -->

      <!-- <span class="item">
        <VideoPlayer :videoBaseUrl="dbEntry?.videoSrc + '#t=' + currentKeyframe"
          :videoOpacity="drawMode === 'video' ? 1.0 : 0"
          :setDrawStyle="setKFSkeletonDrawStyle"
          :fps="dbEntry.fps"
          :drawPoseLandmarks="drawMode === 'skeleton'"/>
      </span> -->
      <span
        class="item"
        v-for="(kfitem) in allKeyframes"
        :key="kfitem.kf"
        :style="{
          'left': 'calc(-14rem + ' + 100 * kfitem.left + '%)',
          'opacity': kfitem.opacity,
          'width': '14rem',
        }">
        <VideoPlayer
          :videoBaseUrl="dbEntry?.videoSrc + '#t=' + kfitem.kf"
          :fps="dbEntry.fps"
          :drawPoseLandmarks="drawMode === 'skeleton'"
          :videoOpacity="drawMode === 'video' ? 1.0 : 0"
          :setDrawStyle="setKFSkeletonDrawStyle"
        />
        <p v-if="showTimestamps" class="has-text-centered">
          <span class="tag">{{kfitem.kf.toFixed(2)}}s</span>
        </p>
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
    drawMode: {
      type: String,
      default: 'skeleton',
    },
    timelineActiveItemsLimit: {
      type: Number,
      default: 1,
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
    maxActiveTimelineSecs: {
      type: Number,
      default: 2.5,
    },
    showTimestamps: {
      type: Boolean,
      default: false,
    },
  },
  setup(props) {
    const minStackItems = 3;
    const {
      keyframes, currentTime, maxActiveTimelineSecs, timelineActiveItemsLimit,
    } = toRefs(props);

    const keyframesTyped = keyframes as Ref<number[]>;

    const currentKeyframe = computed(() => keyframesTyped.value.find((kf, index) => (
      kf < currentTime.value
      && (keyframesTyped.value[index + 1] === undefined || keyframesTyped.value[index + 1] >= currentTime.value)
    )) ?? null);

    const futureKeyframes = computed(() => keyframesTyped.value
      .map((kf) => ({
        timeRemaining: kf - currentTime.value,
        kf,
      }))
      .filter((item) => item.timeRemaining > 0));

    const separatedKeyframes = computed(() => {
      let separationIndex = futureKeyframes.value.findIndex(
        (kf, i) => i >= timelineActiveItemsLimit.value || kf.timeRemaining > maxActiveTimelineSecs.value,
      );
      separationIndex = separationIndex === -1 ? futureKeyframes.value.length : separationIndex;
      const active = futureKeyframes.value.slice(0, separationIndex);
      const future = futureKeyframes.value.slice(separationIndex, separationIndex + minStackItems);

      let timelineTime = maxActiveTimelineSecs.value;
      if (timelineActiveItemsLimit.value === 1 && active.length > 0) {
        const lastKfTime = currentKeyframe.value ?? 0;
        const nextKfTime = active[0].kf;
        const timeTONextKf = nextKfTime - lastKfTime;
        timelineTime = Math.min(timelineTime, timeTONextKf);
      }
      const lastScrollingKf = active[active.length - 1]?.kf;

      return {
        separationIndex,
        activeKeyframes: active.map((kfitem) => ({
          ...kfitem,
          left: kfitem.timeRemaining / timelineTime,
          opacity: 1,
        })),
        stackTimeline: future.map((kfitem, i) => ({
          ...kfitem,
          left: 1.0,
          // eslint-disable-next-line no-nested-ternary
          opacity: i > 0 ? 0
            : (lastScrollingKf
              ? (kfitem.kf - lastScrollingKf) / 1.5
              : 1),
        })),
      };
    });

    const allKeyframes = computed(
      () => {
        const current = [];
        if (currentKeyframe.value !== null) {
          current.push({
            kf: currentKeyframe.value,
            timeRemaining: 0,
            opacity: 1,
            left: 0,
          });
        }
        const timeline = separatedKeyframes.value.activeKeyframes;
        timeline.reverse();

        const stack = separatedKeyframes.value.stackTimeline;
        stack.reverse();

        return [...stack, ...current, ...timeline];
      },
    );

    return {
      currentKeyframe,
      allKeyframes,
      separatedKeyframes,
      futureKeyframes,
      // currentKeyframe,
      // futureKeyframes,
      // activeKeyframes,
      // stackTimeline,

      setKFSkeletonDrawStyle: (canvasCtx: CanvasRenderingContext2D) => {
        canvasCtx.strokeStyle = 'rgba(100, 250, 250, 1)';
        canvasCtx.lineWidth = 7;
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
    margin-left: 14rem;
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
