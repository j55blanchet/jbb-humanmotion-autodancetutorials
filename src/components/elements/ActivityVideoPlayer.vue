<template>
  <div class="activity-video-player">

    <WebcamBox
      ref="webcamBox"
      class="is-flex-grow-1 is-flex-shrink-1" style="height:0"
      :showStartWebcamButton="false"
      v-show="showingWebcam"/>

    <div :class="{
          'is-overlay': showingWebcam || showSheetMusic,
        }" class="is-flex-grow-1 is-flex-shrink-1" :style="{
          height: showingWebcam ? '100%' : 0,
        }">
      <PausingVideoPlayer
        :videoSrc="motion?.videoSrc"
        ref="videoPlayer"
        :drawPoseLandmarks="activity?.demoVisual === 'skeleton'"
        :videoOpacity="activity?.demoVisual === 'video' ? 1 : 0"
        :emphasizedJoints="emphasizedJoints"
        @progress="onProgress"
        @playback-completed="onPlaybackCompleted"
        @pause-hit="onPauseHit"
        @pause-end="onPauseEnded"
        :showControls="activity?.showVideoControls ?? false"
        :motionTrails="motionTrails"
        :drawMotionTrailsInTime="true"
      />
    </div>

    <div v-if="showSheetMusic" style="max-height:100%">
      <SheetMotion
        :dbEntry="motion"
        :drawMode="activity?.sheetMotionVisual"
        :currentTime="videoTime"
        :data="activity?.sheetMotion"
      />
    </div>

    <div class="is-overlay instructions-overlay mb-4">
      <InstructionCarousel v-show="!activityFinished && timedInstructions.length > 0" :sizeClass="'is-medium'" :instructions="timedInstructions" class="m-2"/>
      <InstructionCarousel v-show="pauseInstructs.length > 0" :sizeClass="'is-medium'" :instructions="pauseInstructs" class="m-2"/>
      <InstructionCarousel v-show="instructions.length > 0" :sizeClass="'is-medium'" :instructions="instructions" class="m-2"/>
      <InstructionCarousel v-show="activity?.staticInstruction" :sizeClass="'is-medium'"  :instructions="[{id:0, text:activity?.staticInstruction}]" class="m-2"/>
      <KeyframeTimeline
        :dbEntry="motion"
        :drawMode="keyframeVisual"
        :keyframes="activity?.keyframes ?? []"
        :currentTime="videoTime"
        v-if="keyframeVisual !== 'none'"
        />
    </div>
  </div>
</template>

<script lang="ts">

import {
  computed, defineComponent, ref, toRefs, watchEffect,
} from 'vue';
import InstructionCarousel, { Instruction } from '@/components/elements/InstructionCarousel.vue';
import PausingVideoPlayer from '@/components/elements/PausingVideoPlayer.vue';
import KeyframeTimeline from '@/components/elements/KeyframeTimeline.vue';
import WebcamBox from '@/components/elements/WebcamBox.vue';
import SheetMotion from '@/components/elements/SheetMotion.vue';
import { MiniLessonActivity, MotionTrail, PauseInfo } from '@/model/MiniLesson';
import Constants from '@/services/Constants';

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
    activity: { type: Object },
    defaultPauseDuration: { type: Number, default: 1.5 },
    maxHeight: { type: String, default: '400px' },
  },
  components: {
    PausingVideoPlayer,
    InstructionCarousel,
    WebcamBox,
    KeyframeTimeline,
    SheetMotion,
  },
  setup(props) {
    const { activity } = toRefs(props);
    const state = ref(ActivityPlayState.AwaitingStart);
    const activityFinished = computed(() => state.value === ActivityPlayState.ActivityEnded);
    const awaitingStart = computed(() => state.value === ActivityPlayState.AwaitingStart);
    const isPlaying = computed(() => state.value === ActivityPlayState.Playing);
    const isPendingStart = computed(() => state.value === ActivityPlayState.PendingStart);
    const videoPlayer = ref(null as null | typeof PausingVideoPlayer);
    const webcamBox = ref(null as null | typeof WebcamBox);
    const videoTime = ref(0);

    const pauseInstructs = ref([] as Instruction[]);
    const onPlaybackCompleted = () => {
      state.value = ActivityPlayState.ActivityEnded;
    };
    const onPauseHit = (pause: PauseInfo) => {
      console.log(`Hit pause${pause}`);
      if (pause.instruction) pauseInstructs.value.push({ id: pause.time, text: pause.instruction });
    };
    const onPauseEnded = () => pauseInstructs.value.splice(0);

    const startTime = computed(() => activity?.value?.startTime ?? 0);

    function reset(newTime?: number) {
      pauseInstructs.value.splice(0);
      state.value = ActivityPlayState.AwaitingStart;
      const time = newTime ?? startTime.value ?? 0;

      if (videoPlayer.value) videoPlayer.value.setTime(time);
    }

    watchEffect(() => reset(startTime.value));

    const trailBreakEndIndex = computed(() => {
      const trailBreaks = activity?.value?.motionTrailBreaks as number[];
      if (!trailBreaks) return -1;
      const time = videoTime.value;
      for (let i = 0; i < trailBreaks.length; i += 1) {
        if (trailBreaks[i] > time) return i;
      }
      return trailBreaks.length;
    });
    const trailStartTime = computed(() => {
      const trailBreaks = activity?.value?.motionTrailBreaks as number[];
      if (trailBreakEndIndex.value < 1 || !trailBreaks) return -Infinity;
      return trailBreaks[trailBreakEndIndex.value - 1];
    });
    const trailEndTime = computed(() => {
      const trailBreaks = activity?.value?.motionTrailBreaks as number[];
      if (trailBreakEndIndex.value < 1 || !trailBreaks) return Infinity;
      return trailBreaks[trailBreakEndIndex.value];
    });

    const motionTrails = computed(() => {
      const trailsRaw = activity?.value?.motionTrails as MotionTrail[] ?? [];
      const trailBreaks = activity?.value?.motionTrailBreaks as number[];
      if (trailBreaks) {
        return trailsRaw.map((trail) => {
          let startIndex = trail.findIndex(([t, x, y]) => t >= trailStartTime.value);
          let endIndex = trail.findIndex(([t, x, y]) => t > trailEndTime.value);
          if (startIndex === -1) startIndex = 0;
          if (endIndex === -1) endIndex = trail.length;
          return trail.slice(startIndex, endIndex);
        });
      }
      return trailsRaw;
    });

    return {
      webcamBox,
      videoPlayer,
      videoTime,
      state,
      ActivityPlayState,
      awaitingStart,
      activityFinished,
      pauseInstructs,
      isPlaying,
      isPendingStart,

      reset,
      startTime,

      onPlaybackCompleted,
      onPauseHit,
      onPauseEnded,

      motionTrails,
      trailStartTime,
      trailEndTime,
    };
  },
  computed: {
    keyframeVisual(): 'none' | 'skeleton' | 'video' {
      return (this as any)?.activity?.keyframeVisual ?? 'none';
    },
    showingWebcam() {
      return ((this as any)?.activity?.userVisual ?? 'none') !== 'none';
    },
    showSheetMusic() {
      return ((this as any)?.activity?.sheetMotionVisual ?? 'none') !== 'none';
    },
    emphasizedJoints(): number[] { return this.activity?.emphasizedJoints ?? []; },
    instructions(): Instruction[] {
      const mActivity = this.activity;
      if (!mActivity) return [];

      const instructs: Instruction[] = [];

      if ((this.state === ActivityPlayState.AwaitingStart || this.state === ActivityPlayState.PendingStart) && mActivity.startInstruction) {
        let text = mActivity.startInstruction;
        if (this.state === ActivityPlayState.PendingStart) { text += '...'; }
        instructs.push({
          id: 1,
          text,
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
    timedInstructions(): Instruction[] {
      const mActivity = this.activity as unknown as MiniLessonActivity | null;
      const time = this.videoTime;

      if (!mActivity) return [];

      const activeTimedInstructions = mActivity.timedInstructions?.map(
        (ti, i) => ({
          id: i,
          text: ti.text,
          start: ti.startTime,
          end: ti.endTime,
        })
      ).filter((ti) => ti.start <= time && time < ti.end) ?? [];

      // console.log(`TimedI updated for time ${time}, count=${activeTimedInstructions.length}`, mActivity.timedInstructions);

      return activeTimedInstructions;
    },
  },
  methods: {
    async startWebcam() {
      return this.webcamBox?.startWebcam() ?? new Error('WebcamBox is null');
    },
    play(delay?: number | undefined) {
      this.reset();
      const vidPlayer = this.videoPlayer;
      const vidActivity = this.activity as MiniLessonActivity | null;
      if (!vidActivity) return;
      if (!vidPlayer) {
        console.error('LEARNING SCREEN:: Aborting video playback: vidPlayer is null');
        return;
      }

      this.state = ActivityPlayState.PendingStart;

      vidPlayer.play(
        vidActivity.startTime,
        vidActivity.endTime,
        vidActivity.practiceSpeed ?? 1,
        vidActivity.pauses ?? [],
        delay ?? Constants.DefaultPauseDuration,
        () => {
          this.state = ActivityPlayState.Playing;
        },
      );
    },
    onProgress(val: number) {
      this.videoTime = val;
      this.$emit('progress', val);
    },
  },
});

</script>

<style lang="scss">

.activity-video-player {
  position: relative;
  display: flex;
  flex-flow: column nowrap;
  justify-content: stretch;
  align-items: stretch;
  height: 100%;
  width: 100%;

  .keyframe-video {
    max-height: 33%;
    // max-width: 33%;
  }
}

.instructions-overlay {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-end;
  pointer-events: none;
}

.keyframe-container {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
  align-content: right;
}

</style>
