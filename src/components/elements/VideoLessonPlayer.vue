<template>
  <div class="video-lesson-player">
    <div class="columns">
      <div class="column">
        <ActivityVideoPlayer
          class="block"
          ref="activityVideoPlayer"
          :motion="videoEntry"
          :lesson="videoLesson"
          :activity="activeActivity"
          :maxHeight="maxVideoHeight"
          @progress="onProgress"
        />
      </div>
      <div class="column is-narrow">
        <nav class="panel" :style="{
              'max-height':maxVideoHeight,
              'overflow-y': 'scroll',
            }"
            v-if="videoLesson">
          <div class="panel-heading">Activities</div>
          <a class="panel-block is-size-7"
            v-for="(activity, i) in videoLesson.activities" :key="i"
            :class="{'is-active': activeActivityIndex === i}"
            @click="gotoActivity(i)"
            >
            <strong class="panel-icon">{{i+1}}&nbsp;</strong>&nbsp;{{activity.title}}
          </a>
        </nav>
      </div>
    </div>
    <div>
      <SegmentedProgressBar
        class="block"
        :segments="progressSegments"
        :progress="activityProgress"
      />

      <div class="buttons is-centered has-addons">
        <button
          class="button"
          :disabled="!hasPreviousActivity"
          @click="activeActivityIndex -= 1"
        >
          &lt;
        </button>
        <button
          v-show="!needsStartWebcam"
          class="button"
          :class="{
            'is-primary': ($refs.activityVideoPlayer?.awaitingStart ?? false)
          }"
          :disabled="!($refs.activityVideoPlayer?.awaitingStart ?? false)"
          @click="$refs.activityVideoPlayer.play()"
        >
          Play
        </button>
        <button
          class="button is-primary"
          v-show="needsStartWebcam"
          :class="{'is-loading': webcamStatus==='loading'}"
          @click="startWebcam">
          Start Webcam
        </button>
        <button
          class="button"
          :disabled="!($refs.activityVideoPlayer?.activityFinished ?? false)"
          @click="$refs.activityVideoPlayer?.reset()"
        >
          Reset
        </button>
        <button
          class="button"
          :disabled="!hasNextActivity && !enableCompleteLesson"
          :class="{
            'is-primary': (!hasNextActivity && enableCompleteLesson && $refs.activityVideoPlayer?.activityFinished) || ($refs.activityVideoPlayer?.activityFinished ?? false)
          }"
          @click="nextActivity"
        >
          <span v-if="hasNextActivity || !enableCompleteLesson">&gt;</span>
          <span v-else>Complete Lesson</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import VideoLesson, { Activity } from '@/model/VideoLesson';
import { defineComponent } from 'vue';
import ActivityVideoPlayer from '@/components/elements/ActivityVideoPlayer.vue';
import SegmentedProgressBar, { calculateProgressSegments, ProgressSegmentData } from '@/components/elements/SegmentedProgressBar.vue';
import webcamProvider from '@/services/WebcamProvider';

export default defineComponent({
  name: 'VideoLessonPlayer',
  components: {
    SegmentedProgressBar,
    ActivityVideoPlayer,
  },
  props: {
    videoEntry: { type: Object },
    videoLesson: { type: Object },
    maxVideoHeight: { type: String, default: 'none' },
    enableCompleteLesson: { type: Boolean, default: false },
  },
  emits: ['lesson-completed', 'previous-activity', 'next-activity'],
  computed: {
    lesson() {
      const lesson = (this.$props.videoLesson ?? null) as null | VideoLesson;
      return lesson;
    },
    activeActivity() {
      const lesson = (this.$props.videoLesson ?? null) as null | VideoLesson;
      const activityIndex = this.activeActivityIndex as number;
      const activity = lesson?.activities[activityIndex] ?? null as null | Activity;
      return activity;
    },
    progressSegments(): ProgressSegmentData[] {
      if (this.activeActivity && this.lesson) return calculateProgressSegments(this.lesson, this.activeActivity);
      return [];
    },
    hasNextActivity(): boolean {
      return this.activeActivityIndex + 1 < (this.lesson?.activities.length ?? 0);
    },
    hasPreviousActivity(): boolean {
      return this.activeActivityIndex > 0;
    },
    needsStartWebcam(): boolean {
      return this.activeActivity !== null && this.activeActivity?.userVisual !== 'none' && webcamProvider.webcamStatus.value !== 'running';
    },
  },
  data() {
    return {
      activeActivityIndex: 0,
      activityProgress: 0,
      webcamStatus: webcamProvider.webcamStatus,
    };
  },
  methods: {
    onProgress(val: number) { this.activityProgress = val; },
    playActivity() { (this.$refs.activityVideoPlayer as any).play(); },
    nextActivity() {
      if (this.hasNextActivity) this.activeActivityIndex += 1;
      else this.$emit('lesson-completed');
    },
    gotoActivity(i: number) {
      this.activeActivityIndex = i;
    },
    async startWebcam() {
      return (this.$refs.activityVideoPlayer as any)?.startWebcam();
    },
  },
});
</script>

<style lang="scss">
</style>
