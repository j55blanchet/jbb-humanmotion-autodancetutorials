<template>
  <div class="activity-video-player">

    <div class="overlay" v-show="activity && activity.userVisual !== 'none'">
      <WebcamBox :maxHeight="maxHeight"/>
    </div>

    <PausingVideoPlayer
        :videoSrc="motion.videoSrc"
        ref="videoPlayer"
        :maxHeight="maxHeight"
        :drawPoseLandmarks="activity?.demoVisual === 'skeleton'"
        :videoOpacity="activity?.demoVisual === 'video' ? 1 : 0"
        :emphasizedJoints="emphasizedJoints"
        @progress="onProgress"
        @playback-completed="onPlaybackCompleted"
        @pause-hit="onPauseHit"
        @pause-end="onPauseEnded"
      />

    <div class="overlay instructions-overlay mb-4">
      <InstructionCarousel v-show="!activityFinished && timedInstructions().length > 0" :sizeClass="'is-large'" :instructions="timedInstructions()" class="m-2"/>
      <InstructionCarousel v-show="instructions.length > 0" :sizeClass="'is-large'" :instructions="instructions" class="m-2"/>
      <InstructionCarousel v-show="activity.staticInstruction" :sizeClass="'is-large'"  :instructions="[{id:0, text:activity.staticInstruction}]" class="m-2"/>
    </div>
  </div>
</template>

<script lang="ts">

import {
  computed, ComputedRef, defineComponent, nextTick, onBeforeUnmount, onMounted, Ref, ref, toRefs, watch,
} from 'vue';
import InstructionCarousel, { Instruction } from '@/components/elements/InstructionCarousel.vue';
import PausingVideoPlayer from '@/components/elements/PausingVideoPlayer.vue';
import WebcamBox from '@/components/elements/WebcamBox.vue';
import { Activity } from '@/model/DanceLesson';

const ActivityPlayState = Object.freeze({
  AwaitingStart: 'AwaitingStart',
  PendingStart: 'PendingStart',
  Playing: 'Playing',
  ActivityEnded: 'ActivityEnded',
});

export default defineComponent({
  name: 'ActivityVideoPlayer',
  emits: ['progress', 'activityEnded'],
  props: {
    motion: { type: Object },
    lesson: { type: Object },
    activity: { type: Object },
    defaultPauseDuration: { type: Number, default: 1.5 },
    maxHeight: { type: String, default: '400px' },
  },
  components: {
    PausingVideoPlayer,
    InstructionCarousel,
    WebcamBox,
  },
  setup(props, { emit }) {
    const { motion, lesson, activity } = toRefs(props);
    const state = ref(ActivityPlayState.AwaitingStart);
    const activityFinished = computed(() => state.value === ActivityPlayState.ActivityEnded);
    const videoElement = ref(null as null | typeof PausingVideoPlayer);
    const videoTime = () => (videoElement.value as any)?.getVideoTime() ?? 0;

    const onPlaybackCompleted = () => {};
    const onPauseHit = () => {};
    const onPauseEnded = () => {};

    return {
      videoElement,
      videoTime,
      state,
      activityFinished,

      onPlaybackCompleted,
      onPauseHit,
      onPauseEnded,
    };
  },
  computed: {
    emphasizedJoints(): number[] { return this.activity?.emphasizedJoints ?? []; },
    instructions(): Instruction[] {
      const mActivity = this.activity;
      if (!mActivity) return [];

      const instructs: Instruction[] = [];

      if ((this.state === ActivityPlayState.AwaitingStart || this.state === ActivityPlayState.PendingStart) && mActivity.startInstruction) {
        instructs.push({
          id: 1,
          text: mActivity.startInstruction,
        });
      } else if (this.state === ActivityPlayState.Playing && mActivity.playingInstruction) {
        instructs.push({
          id: 2,
          text: mActivity.playingInstruction,
        });
      } else if (this.state === ActivityPlayState.ActivityEnded && mActivity.endInstruction) {
        instructs.push({
          id: 2,
          text: mActivity.endInstruction,
        });
      }

      return instructs;
    },
  },
  methods: {
    timedInstructions(): Instruction[] {
      const mActivity = this.activity as unknown as Activity | null;
      const time = this.videoTime();
      if (!mActivity) return [];

      const activeTimedInstructions = mActivity.timedInstructions?.map(
        (ti, i) => ({
          id: i,
          text: ti.text,
          start: ti.startTime,
          end: ti.endTime,
        })
      ).filter((ti) => ti.start <= time && time < ti.end) ?? [];

      return activeTimedInstructions;
    },
    onProgress(val: number) {
      this.$emit('progress', val);
    },
  },
});

</script>

<style lang="scss">

.activity-video-player {
  // background: black;
  position: relative;
}

</style>
