<template>
  <div class="learning-screen background-blur"
    >
    <teleport to="#topbarLeft">
      <button class="button" @click="$emit('back-selected')">&lt; Back</button>
    </teleport>
    <teleport to="#topbarRight">
      <span class="tag">{{activityId}} / {{activityCount}}</span>
      <progress class="lessonProgress progress ml-2" :max="activityCount" :value="activityId">
      </progress>
    </teleport>
    <teleport to="#topbarCenter">
        <h3>{{activityTitle}}</h3>
    </teleport>

    <div class="overlay" v-show="activity && activity.userVisual !== 'none'">
      <WebcamBox style="width:1280px;height:720px;"/>
    </div>

    <div class="overlay">
      <PausingVideoPlayer
        :videoSrc="targetDance.videoSrc"
        :height="'720px'"
        ref="videoPlayer"
        @progress="onTimeChanged"
        @playback-completed="onActivityFinished"
        @pause-hit="onPauseHit"
        @pause-end="onPauseEnded"
        :drawPoseLandmarks="activity?.demoVisual === 'skeleton'"
        :videoOpacity="activity?.demoVisual === 'video' ? 1 : 0"
      />
    </div>

    <div class="overlay instructions-overlay mb-4">
      <InstructionCarousel v-show="activityFinished" :instructions="[{id:0, text:'Use a gesture to proceed'}]" class="m-2"/>
      <InstructionCarousel v-show="!activityFinished && timedInstructions.length > 0" :instructions="timedInstructions" class="m-2"/>
      <InstructionCarousel v-show="instructions.length > 0" :instructions="instructions" class="m-2"/>
      <InstructionCarousel v-show="activity.staticInstruction" :instructions="[{id:0, text:activity.staticInstruction}]" class="m-2"/>
    </div>

    <div class="overlay overlay-left" v-show="activityFinished">
      <div class="vcenter-parent">
        <div class="content translucent-text p-5 is-size-5 is-rounded">
          <p class="mb-0">Repeat</p>
            <span class="icon is-large fa-flip-horizontal">
              <i class="fas fa-2x fa-hand-paper fa-rotate-90"></i>
            </span>
            <!-- <br>
            <p class="mt-4 has-text-grey-lighter">{{activityTitle}}</p> -->
        </div>
      </div>
    </div>
    <div class="overlay overlay-right" v-show="activityFinished">
      <div class="vcenter-parent">
        <div class="content translucent-text p-5 is-size-5 is-rounded">
          <p class="mb-0">Next</p>
          <span class="icon is-large" >
            <i class="fas fa-2x fa-hand-paper fa-rotate-90"></i>
          </span>
          <!-- <br>
          <p class="mt-4 has-text-grey-lighter">{{nextActivityTitle}}</p> -->
        </div>
      </div>
    </div>

    <teleport to="#belowSurface">
      <div>
        <div class="master-bar mt-4">
          <SegmentedProgressBar
            :segments="progressSegments"
            :progress="videoTime"
          />
        </div>
        <div class="mt-4 mb-4 buttons is-centered">
          <button class="button" @click="gotoPreviousActivity">Previous</button>
          <button class="button" @click="gotoNextActivity">Next</button>
          <button class="button"
            @click="startSaveFrames"
            :disabled="!canSaveFrame"
            :class="{'is-loading': isSavingFrames}">Save Frames</button>
        </div>
      </div>
    </teleport>
  </div>
</template>

<script lang="ts">
import DanceLesson, { Activity, PauseInfo } from '@/model/DanceLesson';
import {
  computed, ComputedRef, defineComponent, onBeforeUnmount, onMounted, Ref, ref, toRefs, watch,
} from 'vue';
import {
  GestureNames, setupGestureListening, setupMediaPipeListening, TrackingActions,
} from '@/services/EventHub';
import DanceEntry from '@/model/DanceEntry';
import motionRecorder from '@/services/MotionRecorder';
import InstructionCarousel, { Instruction } from '@/components/elements/InstructionCarousel.vue';
import { Landmark } from '@/services/MediaPipeTypes';
import SegmentedProgressBar, { ProgressSegmentData } from '../elements/SegmentedProgressBar.vue';
import PausingVideoPlayer from '../elements/PausingVideoPlayer.vue';
import WebcamBox from '../elements/WebcamBox.vue';

const DefaultPauseDuration = 1.5; // 1.5 seconds

const ActivityPlayState = Object.freeze({
  NotStarted: 'NotStarted',
  Playing: 'Playing',
  ActivityEnded: 'ActivityEnded',
});

//
// TODO!
//   * Update segment breaks in activity to have the first activity
//     start time and the last activity end time.
//

function calculateProgressSegments(dance: DanceEntry, lesson: DanceLesson, activity: Activity) {
  if (!lesson) return [];

  let last = undefined as undefined | number;
  const segs = lesson.segmentBreaks.map((timestamp, i) => {
    let segData = undefined as undefined | ProgressSegmentData;
    if (last !== undefined) {
      segData = {
        min: last,
        max: timestamp,
        enabled: activity.focusedSegments ? activity.focusedSegments.indexOf(i - 1) !== -1 : true,
      };
    }
    last = timestamp;
    return segData;
  }).filter((x) => x !== undefined);

  return segs;
}

const TRACKING_ID = 'LearningScreen';

function setupFrameRecording(activity: ComputedRef<Activity | null>, activityFinished: Ref<boolean>, videoPlayer: Ref<null | typeof PausingVideoPlayer>, playActivity: Function) {
  const isSavingFrames = ref(false);
  let recordingSessionId = -1;

  const lastPose = {
    frameId: -1,
    pose: null as null | Landmark[],
  };

  setupMediaPipeListening(
    (mpResults, frameId) => {
      // console.log('Got mp result');
      if (frameId !== lastPose.frameId) {
        console.warn(`Skipping motion recording frame -- proceesed frameId ${frameId} doesn't match stored pose with id: ${lastPose.frameId}`);
        return;
      }
      if (isSavingFrames.value) {
        motionRecorder.saveMotionFrame(
          recordingSessionId,
          mpResults,
          { poseLandmarks: lastPose.pose ?? undefined },
        );
      }
    },
    (frameId) => {
      lastPose.frameId = frameId;
      lastPose.pose = videoPlayer.value?.currentPose ?? null;
    },
  );
  const canSaveFrame = computed(() => {
    if (isSavingFrames.value) return false;
    if (!activity.value) return false;
    // if (!activityFinished.value) return false;
    return activity.value.demoVisual === 'skeleton' && activity.value.userVisual !== 'none';
  });
  async function startSaveFrames() {
    recordingSessionId = await motionRecorder.startRecordingSession(
      { width: 640, height: 480 },
      videoPlayer.value?.getVideoDimensions(),
    );

    isSavingFrames.value = true;

    playActivity(5);
  }
  async function concludeSaveFrames() {
    isSavingFrames.value = false;

    await motionRecorder.endRecordingSession(
      recordingSessionId,
      activity.value?.startTime ?? -1,
      activity.value?.endTime ?? -1,
    );
  }

  return {
    isSavingFrames, canSaveFrame, startSaveFrames, concludeSaveFrames,
  };
}

export default defineComponent({
  components: {
    SegmentedProgressBar,
    PausingVideoPlayer,
    InstructionCarousel,
    WebcamBox,
  },
  props: {
    targetDance: Object,
    targetLesson: Object,
  },
  setup(props, { emit }) {

    const { targetLesson, targetDance } = toRefs(props);

    const activityState = ref(ActivityPlayState.NotStarted);

    const videoPlayer = ref(null as null | typeof PausingVideoPlayer);
    const videoTime = ref(0);

    const activityId = ref(0);
    const activity = computed(() => {
      const lesson = targetLesson?.value as unknown as DanceLesson | null;
      return lesson?.activities[activityId.value] ?? null;
    });

    const activityTitle = computed(() => activity.value?.title ?? '');
    const activityCount = computed(() => {
      const lesson = targetLesson?.value as unknown as DanceLesson | null;
      return lesson?.activities?.length ?? 0;
    });
    const hasNextActivity = computed(() => activityCount.value > activityId.value + 1);
    // eslint-disable-next-line max-len
    const activityFinished = computed(() => activityState.value === ActivityPlayState.ActivityEnded);
    const nextActivityTitle = computed(() => {
      if (!hasNextActivity.value) return 'Finish Lesson';
      const lesson = targetLesson?.value as unknown as DanceLesson | null;

      const nextActivity = lesson?.activities[activityId.value + 1];
      return nextActivity?.title ?? 'Unknown';
    });

    const pauseInstructs = ref([] as Instruction[]);
    function onPauseHit(pause: PauseInfo) {
      if (pause.instruction) {
        pauseInstructs.value.push({
          id: pause.time,
          text: pause.instruction,
        });
      }
    }
    function onPauseEnded() {
      // Remove all pause instructions
      pauseInstructs.value.splice(0);
    }

    const instructions = computed(() => {
      const mActivity = activity.value;
      const state = activityState.value;
      if (!mActivity) return [];

      const instructs: Instruction[] = [];

      if (state === ActivityPlayState.NotStarted && mActivity.startInstruction) {
        instructs.push({
          id: 1,
          text: mActivity.startInstruction,
        });
      } else if (state === ActivityPlayState.Playing && mActivity.playingInstruction) {
        instructs.push({
          id: 2,
          text: mActivity.playingInstruction,
        });
      } else if (state === ActivityPlayState.ActivityEnded && mActivity.endInstruction) {
        instructs.push({
          id: 2,
          text: mActivity.endInstruction,
        });
      }

      return instructs;
    });
    const timedInstructions = computed(() => {
      const mActivity = activity.value;
      const time = videoTime.value;
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
    });

    const progressSegments = computed(() => {
      const lesson = targetLesson?.value as DanceLesson | undefined;
      const dance = targetDance?.value as DanceEntry | undefined;
      const curActivity = activity.value;
      if (lesson && dance && curActivity) return calculateProgressSegments(dance, lesson, curActivity);
      return [];
    });

    function playActivity(pause?: number | undefined) {
      console.log(`LEARNING SCREEN:: Starting playback (activityId: ${activityId.value})`);
      pauseInstructs.value.splice(0);
      activityState.value = ActivityPlayState.Playing;
      const vidPlayer = videoPlayer.value;
      const vidActivity = activity.value;
      if (!vidPlayer || !vidActivity) {
        console.error('LEARNING SCREEN:: Aborting video playback: videoElement or lessonActivity is null', vidPlayer, vidActivity);
        return;
      }

      vidPlayer.play(
        vidActivity.startTime,
        vidActivity.endTime,
        (vidActivity.practiceSpeeds ?? [1])[0] ?? 1,
        vidActivity.pauses ?? [],
        pause ?? DefaultPauseDuration,
      );
    }

    function gotoActivity(delta: number) {
      activityState.value = ActivityPlayState.NotStarted;
      if (!hasNextActivity.value) {
        emit('lesson-completed');
        return;
      }
      if (activityId.value === 0 && delta < 0) {
        playActivity(0);
        return;
      }
      activityId.value += delta;
      playActivity();
    }
    function gotoPreviousActivity() {
      gotoActivity(-1);
    }

    function gotoNextActivity() {
      gotoActivity(1);
    }

    const {
      isSavingFrames, canSaveFrame, startSaveFrames, concludeSaveFrames,
    } = setupFrameRecording(activity, activityFinished, videoPlayer, playActivity);

    function onActivityFinished() {
      activityState.value = ActivityPlayState.ActivityEnded;
      console.log('LEARNING SCREEN:: Activity finished');

      if (isSavingFrames.value) concludeSaveFrames();
    }

    const isTrackingUser = computed(() => {
      if (activity.value?.userVisual === 'skeleton') return true;
      if (activityState.value === ActivityPlayState.ActivityEnded) return true;
      if (isSavingFrames.value) return true;
      return false;
    });
    watch(isTrackingUser, (val) => {
      if (val) TrackingActions.requestTracking(TRACKING_ID);
      else TrackingActions.endTrackingRequest(TRACKING_ID);
    });

    setupGestureListening({
      [GestureNames.pointRight]: () => {
        if (!activityFinished.value) return;
        gotoNextActivity();
      },
      [GestureNames.pointLeft]: () => {
        if (!activityFinished.value) return;
        playActivity();
      },
    });
    onBeforeUnmount(() => {
      TrackingActions.endTrackingRequest(TRACKING_ID);
    });

    onMounted(() => {
      playActivity(2.5);
    });

    return {
      activityState,
      progressSegments,
      activity,
      activityId,
      activityCount,
      activityTitle,
      nextActivityTitle,
      instructions,
      timedInstructions,
      videoPlayer,
      activityFinished,
      videoTime,
      onActivityFinished,

      onPauseHit,
      onPauseEnded,

      gotoPreviousActivity,
      gotoNextActivity,

      canSaveFrame,
      isSavingFrames,
      startSaveFrames,
    };
  },
  methods: {
    onTimeChanged(time: number) {
      this.videoTime = time;
    },
  },
});
</script>

<style lang="scss">

.learning-screen {
  position: relative;
  width: 100%;
  height: 100%;
}

.master-bar {
  width: 1280px;
  // margin: 0 auto;
  // padding: 1rem 1rem 1rem 1rem;
  // border-radius: 0 0 0.5rem 0.5rem;
}

.instructions-overlay {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-end;
}

.lessonProgress {
  width: 128px;
}
</style>
