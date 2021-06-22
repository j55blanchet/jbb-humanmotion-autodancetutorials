<template>
  <div class="video-lesson-player">
    <div class="columns is-flex-grow-1">
      <!-- <div class="column is-narrow" v-if="videoLesson">
        <div class="tile is-ancestor is-vertical" style="overflow-y:auto;" :style="{
              'max-height':maxVideoHeight
            }">
          <div class="tile is-child box has-text-centered m-4"
               v-for="(activity, i) in videoLesson.activities" :key="i"
               :class="{'is-active': activeActivityIndex === i}"
          >
            <p class="subtitle" v-text="activity.title"></p>
          </div>
        </div> -->
        <!-- <nav class="panel" :style="{
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
      </div> -->
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

    </div>
    <div class="is-flex-grow-0">
      <SegmentedProgressBar
        class="block"
        :segments="progressSegments"
        :progress="activityProgress"
      />

      <div class="buttons is-centered has-addons">
        <button
          v-if="!needsStartWebcam && !$refs.activityVideoPlayer?.activityFinished"
          class="button"
          :class="{
            'is-primary': ($refs.activityVideoPlayer?.awaitingStart ?? false),
            'is-loading': ($refs.activityVideoPlayer?.isPlaying ?? false),
          }"
          :disabled="($refs.activityVideoPlayer?.isPlaying ?? (!$refs.activityVideoPlayer?.awaitingStart) ?? false)"
          @click="$refs.activityVideoPlayer.play()"
        >
          <span class="icon"><i class="fas fa-play"></i></span>
        </button>
        <button
          class="button is-primary"
          v-if="needsStartWebcam"
          :class="{'is-loading': webcamStatus==='loading'}"
          @click="startWebcam">
          Start Webcam
        </button>
        <button
          class="button"
          v-if="$refs.activityVideoPlayer?.activityFinished"
          @click="repeat()"
        >
          <div class="icon"><i class="fas fa-redo fa-flip-horizontal"></i></div>
        </button>
        <button
          class="button"
          v-if="$refs.activityVideoPlayer?.activityFinished && (hasNextActivity || enableCompleteLesson)"
          :class="{
            'is-primary': (!hasNextActivity && enableCompleteLesson && $refs.activityVideoPlayer?.activityFinished) || ($refs.activityVideoPlayer?.activityFinished ?? false)
          }"
          @click="nextActivity"
        >
          <span v-if="hasNextActivity || !enableCompleteLesson" class="icon"><i class="fas fa-step-forward"></i></span>
          <span v-else>
            <span class="icon"><i class="fas fa-check"></i></span>
            <span>Done</span>
          </span>
        </button>
      </div>

      <nav class="pagination is-centered">
        <div class="pagination-list">
          <li  v-for="(activity, i) in videoLesson.activities" :key="i">
            <a class="pagination-link"
               :class="{'is-current': activeActivityIndex === i}"
               @click="gotoActivity(i)">
               {{i+1}}
            </a>
          </li>
        </div>
      </nav>

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
    repeat() {
      const vidPlayer = (this.$refs.activityVideoPlayer as any);
      vidPlayer.reset();
      vidPlayer.play();
    },
  },
});
</script>

<style lang="scss">

.video-lesson-player {
  display: flex;
  flex-flow: column;
  max-height: 100vh;
  max-width: 100vw;
}
</style>
