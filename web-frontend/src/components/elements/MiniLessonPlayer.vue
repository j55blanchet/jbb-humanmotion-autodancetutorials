<template>
  <div class="mini-lesson-player">
    <div class="block is-flex-grow-0 is-flex-shrink-0 is-relative is-flex">
      <SegmentedProgressBar
        :segments="progressSegments"
        :progress="activityProgress"
        class="is-flex-grow-1 is-flex-shrink-1"
      />
      <div class="is-flex-grow-0 is-flex-grow-0 ml-2 has-text-grey" v-if="timeRemaining !== null">
        {{timeRemaining}}
      </div>
    </div>
    <div class="video-container">
      <ActivityVideoPlayer
        ref="activityVideoPlayer"
        :motion="videoEntry"
        :activity="activeActivity"
        @progress="onProgress"
      />
    </div>
    <div class="is-flex-grow-0 is-flex-shrink-0">
      <div class="block"></div>
      <!-- <SegmentedProgressBar
        class="block"
        :segments="progressSegments"
        :progress="activityProgress"
      /> -->
      <nav class="pagination is-centered" v-if="miniLesson">
        <div class="pagination-list" style="max-width:calc(100vw - 2.5rem);">
          <li  v-for="(i, index) in nearbyActivityIndices" :key="index">
            <span class="pagination-ellipses">
              <button
                class="button"
                :class="{'is-primary': activityVideoPlayer?.activityFinished && activeActivityIndex + 1 === i}"
                @click="gotoActivity(i)"
                v-if="i >= 0 && i !== activeActivityIndex">
                <span class="icon" v-if="activityVideoPlayer?.activityFinished && activeActivityIndex + 1 === i"><i class="fas fa-step-forward"></i></span>
                <span><strong>{{i+1}}</strong>&nbsp;|&nbsp;<span>{{activities[i]?.title}}</span></span>
              </button>
            </span>
            <span class="pagination-ellipses" v-if="i<0">
              &hellip;
            </span>
            <span class="pagination-ellipses buttons has-addons" v-if="i===activeActivityIndex">
              <button
                v-if="!activityVideoPlayer?.activityFinished"
                class="button"
                :class="{
                  'is-primary': (activityVideoPlayer?.awaitingStart ?? false) || (activityVideoPlayer?.isPendingStart ?? false),
                  'is-loading': (!activityVideoPlayer) || (activityVideoPlayer?.isPlaying ?? false) || (activityVideoPlayer?.isPendingStart ?? false),
                }"
                :disabled="needsStartWebcam || !(activityVideoPlayer?.awaitingStart ?? false)"
                @click="activityVideoPlayer.play()"
              >
                <strong>{{i+1}}</strong>&nbsp;|&nbsp;
                <span>{{activeActivity?.title}}</span>
                <span class="icon"><i class="fas fa-play"></i></span>
              </button>
              <button
                class="button is-warning"
                v-if="activityVideoPlayer?.activityFinished"
                @click="repeat()"
              >
                <strong>{{i+1}}</strong>&nbsp;|&nbsp;
                <span>{{activeActivity?.title}}</span>
                <span class="icon"><i class="fas fa-redo fa-flip-horizontal"></i></span>
                <!-- <span>Repeat</span> -->
              </button>
              <!-- <button
                class="button is-primary"
                v-if="activityVideoPlayer?.activityFinished && hasNextActivity"
                @click="nextActivity"
              >
                <span>Next </span>
                <span class="icon"><i class="fas fa-step-forward"></i></span>
              </button> -->
            </span>
          </li>
          <li>
            <span class="pagination-ellipses" v-if="enableCompleteLesson">
              <button class="button"
                :class="{ 'is-primary': activityVideoPlayer?.activityFinished && !hasNextActivity}"
                @click="completeLesson">
                <span class="icon"><i class="fas fa-check"></i></span>
                <span>Done</span>
              </button>
            </span>
          </li>
        </div>
      </nav>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, nextTick } from 'vue';
import MiniLesson, { MiniLessonActivity } from '@/model/MiniLesson';
import ActivityVideoPlayer from '@/components/elements/ActivityVideoPlayer.vue';
import SegmentedProgressBar, { calculateProgressSegments, ProgressSegmentData } from '@/components/elements/SegmentedProgressBar.vue';
import webcamProvider from '@/services/WebcamProvider';
import Utils from '@/services/Utils';
import eventLogger from '@/services/EventLogger';

export default defineComponent({
  name: 'MiniLessonPlayer',
  components: {
    SegmentedProgressBar,
    ActivityVideoPlayer,
  },
  props: {
    videoEntry: { type: Object },
    miniLesson: { type: Object },
    // maxVideoHeight: { type: String, default: 'none' },
    enableCompleteLesson: { type: Boolean, default: false },
    timeRemaining: { type: String, default: null },
  },
  setup() {
    const activityVideoPlayer = ref(null as null | typeof ActivityVideoPlayer);
    return {
      activityVideoPlayer,
    };
  },
  emits: ['lesson-completed', 'activity-changed'],
  computed: {
    nearbyActivityIndices(): number[] {
      const margin = 1;
      const minIndex = Math.max(0, this.activeActivityIndex - margin);
      const maxActivityIndex = (this.lesson?.activities.length ?? 0) - 1;
      const maxIndex = Math.min(maxActivityIndex, this.activeActivityIndex + margin);
      const count = (maxIndex + 1) - minIndex;
      let indices: number[] = [];
      if (minIndex > 0) {
        if (minIndex === 1) {
          indices.push(0);
        } else {
          indices.push(0, -1);
        }
        // indices = indices.concat([0, -1]);
      }
      indices = indices.concat(Utils.range(count, minIndex));
      if (maxIndex < maxActivityIndex) {
        if (maxIndex === maxActivityIndex - 1) {
          indices.push(maxActivityIndex);
        } else {
          indices.push(-1, maxActivityIndex);
        }
      }
      return indices;
    },
    lesson() {
      const lesson = (this.$props.miniLesson ?? null) as null | MiniLesson;
      return lesson;
    },
    activities(): MiniLessonActivity[] {
      return (this.lesson as any)?.activities ?? [];
    },
    activeActivity() {
      const lesson = (this.$props.miniLesson ?? null) as null | MiniLesson;
      const activityIndex = this.activeActivityIndex as number;
      const activity = lesson?.activities[activityIndex] ?? null as null | MiniLessonActivity;
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
      return this.activeActivity !== null && (this.activityVideoPlayer as typeof ActivityVideoPlayer)?.needsToStartWebcam;
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
    autoPlay() {
      nextTick(() => {
        if (!this.needsStartWebcam) {
          this.playActivity();
        }
      });
    },
    playActivity() {
      (this.$refs.activityVideoPlayer as any).play();
    },
    nextActivity() {
      if (this.hasNextActivity) this.activeActivityIndex += 1;
      nextTick(() => {
        if (!this.needsStartWebcam) this.playActivity();
      });
    },
    completeLesson() {
      this.$emit('lesson-completed');
    },
    gotoActivity(i: number) {
      this.activeActivityIndex = i;
      this.autoPlay();
    },
    async startWebcam() {
      return (this.$refs.activityVideoPlayer as any)?.startWebcam();
    },
    repeat() {
      const vidPlayer = (this.$refs.activityVideoPlayer as any);
      eventLogger.log(`Repeating lesson activity ${this.activeActivity?.title}`);
      vidPlayer.reset();
      vidPlayer.play();
    },
  },
  watch: {
    activeActivityIndex(newVal: number) {
      this.$emit('activity-changed', newVal);
    },
  },
});
</script>

<style lang="scss">

.mini-lesson-player {
  display: flex;
  flex-flow: column;
  height: 100%;
  width: 100%;

  .video-container {
    flex: 1 1 0;
    // background: lightblue;

    display: flex;
    flex-flow: column nowrap;
    justify-content: center;
    align-items: center;
    height: 0px;
  }
}
</style>
