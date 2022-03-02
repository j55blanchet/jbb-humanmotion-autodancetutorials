<template>
  <div class="activity-video-player">

    <WebcamBox
      ref="webcamBox"
      class="is-flex-grow-1 is-flex-shrink-1" style="height:0"
      :showStartWebcamButton="false"
      v-show="showingWebcam"/>

    <div
        :class="{
          'is-overlay': showingWebcam || showSheetMusic,
        }"
        class="is-flex-grow-1 is-flex-shrink-1"
        :style="{
          height: showingWebcam ? '100%' : 0,
        }"

        v-show="!needsToStartWebcam">
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

    <video v-if="isReviewing"  style="height:100%" class="flipped" :src="recordingObjectUrl" controls></video>

    <div class="is-overlay instructions-overlay mb-4">
      <InstructionCarousel v-show="pauseInstructs.length > 0" :sizeClass="'is-medium'" :tagClass="'is-white'" :instructions="pauseInstructs" class="m-2"/>
      <InstructionCarousel v-show="instructions.length > 0" :sizeClass="'is-medium'" :tagClass="'is-white'" :instructions="instructions" class="m-2"/>
      <InstructionCarousel v-show="!activityFinished && timedInstructions.length > 0" :sizeClass="'is-large'" :instructions="timedInstructions" class="m-2"/>
      <InstructionCarousel v-show="activity?.staticInstruction" :sizeClass="'is-medium'" :tagClass="''"  :instructions="[{id:0, text:activity?.staticInstruction}]" class="m-2"/>
      <KeyframeTimeline
        :dbEntry="motion"
        :drawMode="keyframeVisual"
        :keyframes="activity?.keyframes ?? []"
        :currentTime="videoTime"
        v-if="keyframeVisual !== 'none'"
        />
    </div>

    <div class="is-overlay p-4 has-background-white" style="overflow: scroll;" v-if="needsToStartWebcam">
      <WebcamSourceSelectionMenu
        v-model:videoDeviceId="videoDeviceId"
        v-model:audioDeviceId="audioDeviceId"
        @startWebcamClicked="startWebcam" />
    </div>
  </div>
</template>

<script lang="ts">

import {
  computed, defineComponent, onBeforeUnmount, Ref, ref, toRefs, watch, watchEffect,
} from 'vue';
import InstructionCarousel, { Instruction } from '@/components/elements/InstructionCarousel.vue';
import PausingVideoPlayer from '@/components/elements/PausingVideoPlayer.vue';
import KeyframeTimeline from '@/components/elements/KeyframeTimeline.vue';
import WebcamBox from '@/components/elements/WebcamBox.vue';
import SheetMotion from '@/components/elements/SheetMotion.vue';
import WebcamSourceSelectionMenu from '@/components/elements/WebcamSourceSelectionMenu.vue';
import { MiniLessonActivity, MotionTrail, PauseInfo } from '@/model/MiniLesson';
import Constants from '@/services/Constants';
import webcamProvider from '@/services/WebcamProvider';
import eventLogger from '@/services/EventLogger';

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
    WebcamSourceSelectionMenu,
  },
  setup(props) {
    const { activity } = toRefs(props);
    const typedActivity = computed(() => (activity.value as MiniLessonActivity) ?? null);
    const state = ref(ActivityPlayState.AwaitingStart);

    const shouldReview = computed(() => (typedActivity?.value?.reviewing) !== undefined);
    const shouldRecord = computed(() => ((typedActivity?.value?.recording) !== undefined) || shouldReview.value);

    const activityFinished = computed(() => state.value === ActivityPlayState.ActivityEnded);
    const awaitingStart = computed(() => state.value === ActivityPlayState.AwaitingStart);
    const isPlaying = computed(() => state.value === ActivityPlayState.Playing);
    const isPendingStart = computed(() => state.value === ActivityPlayState.PendingStart);
    const isReviewing = computed(() => state.value === ActivityPlayState.ActivityEnded && shouldReview.value);
    const videoPlayer = ref(null as null | typeof PausingVideoPlayer);
    const webcamBox = ref(null as null | typeof WebcamBox);
    const videoTime = ref(0);

    const recordingId = computed(() => {
      if (!shouldRecord.value) return '';
      return typedActivity?.value?.recording?.identifier ?? 'unknown-or-temp-identifier';
    });

    const recordingObjectUrl = ref(null as null | string);

    onBeforeUnmount(() => {
      webcamProvider.abortRecording(recordingId.value);
    });

    const pauseInstructs = ref([] as Instruction[]);
    const onPlaybackCompleted = async () => {

      if (shouldRecord.value && webcamProvider.isRecording(recordingId.value)) {
        await webcamProvider.stopRecording(recordingId.value);
        const blob = await webcamProvider.getBlob(recordingId.value);
        recordingObjectUrl.value = URL.createObjectURL(blob);
      }

      eventLogger.log(`Playback completed for activity ${activity.value?.title}`);

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
      webcamProvider.abortRecording(recordingId.value);
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
      typedActivity,
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
      isReviewing,

      shouldReview,
      shouldRecord,
      recordingId,
      recordingObjectUrl,
      isRecording: () => webcamProvider.isRecording(recordingId.value),

      reset,
      startTime,

      onPlaybackCompleted,
      onPauseHit,
      onPauseEnded,

      motionTrails,
      trailStartTime,
      trailEndTime,

      audioDeviceId: ref(''),
      videoDeviceId: ref(''),
    };
  },
  computed: {
    keyframeVisual(): 'none' | 'skeleton' | 'video' {
      return (this as any)?.activity?.keyframeVisual ?? 'none';
    },
    showingWebcam() {
      const hideForReview = (this as any)?.isReviewing ?? false;
      return !hideForReview && (((this as any)?.activity?.userVisual ?? 'none') !== 'none');
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
        }),
      ).filter((ti) => ti.start <= time && time < ti.end) ?? [];

      // console.log(`TimedI updated for time ${time}, count=${activeTimedInstructions.length}`, mActivity.timedInstructions);

      return activeTimedInstructions;
    },
    needsToStartWebcam() {
      const needsUserVisual = ((this as any).activity?.userVisual ?? 'none') !== 'none';
      const needsWebcam = this.shouldRecord || needsUserVisual;
      return needsWebcam && webcamProvider.webcamStatus.value !== 'running';
    },
  },
  methods: {
    async startWebcam() {
      if (this.webcamBox) {
        await this.webcamBox.startWebcam(this.videoDeviceId, this.audioDeviceId);
        this.play();
      }
      return new Error('WebcamBox is null');
    },
    async play(delay?: number | undefined) {
      this.reset();
      const vidPlayer = this.videoPlayer;
      const vidActivity = this.activity as MiniLessonActivity | null;
      if (!vidActivity) return;
      if (!vidPlayer) {
        console.error('LEARNING SCREEN:: Aborting video playback: vidPlayer is null');
        return;
      }

      this.state = ActivityPlayState.PendingStart;

      if (this.shouldRecord && !this.isRecording()) {
        console.log('Gonna do some muthafucking recording!');
        await webcamProvider.startRecording(this.recordingId);
      }

      eventLogger.log(`Starting playback of activity ${this.activity?.title} at ${vidActivity.startTime.toFixed(2)}`);

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
