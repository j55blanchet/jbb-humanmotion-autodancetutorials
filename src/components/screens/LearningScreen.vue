<template>
  <div class="learning-screen"
    >

    <div class="block is-flex is-flex-direction-row is-justify-content-center is-align-items-center  is-align-content-space-evenly" style="gap: 1rem;">
      <button class="button" @click="$emit('back-selected')">&lt; Back</button>
      <span class="tag">{{activityId}} / {{activityCount}}</span>
      <progress class="lessonProgress progress m-0" :max="activityCount" :value="activityId">
      </progress>
      <h3>{{activityTitle}}</h3>
      <span class="tag ml-2">Time: {{videoTime.toFixed(2)}}</span>
    </div>

    <div class="block is-relative" style="width: 100%; max-width: 1280px; height: 80vh;">
      <div class="overlay" v-show="activity && activity.userVisual !== 'none'">
        <WebcamBox :maxHeight="'720px'"/>
      </div>


      <ActivityVideoPlayer
        :motion="targetDance"
        :lesson="targetLesson"
        :activity="activity"
        :maxHeight="'720px'"
        ref="videoPlayer"
        @progress="onTimeChanged" />
        <!-- :drawPoseLandmarks="activity?.demoVisual === 'skeleton'" -->
        <!-- :videoOpacity="activity?.demoVisual === 'video' ? 1 : 0" -->
        <!-- :emphasizedJoints="emphasizedJoints" -->
      <!-- /> -->

      <!-- <div class="overlay overlay-bottom overlay-right mb-6 mr-6" v-show="showPlayGestureIcon">
        <div class="vcenter-parent">
          <div class="content translucent-text activityStartGestureCard is-rounded" >
            <GestureIcon class="activityEndGestureCard" :gesture="'play'" />
            <p>Start Activity</p>
          </div>
        </div>
      </div>
      <div class="overlay overlay-left overlay-bottom mb-6 ml-6" v-show="activityFinished">
        <div class="vcenter-parent ml-2">
          <div class="content translucent-text p-5 is-rounded activityStartGestureCard">
            <GestureIcon class="activityEndGestureCard" :gesture="'backward'" />
            <p>Repeat this activity</p>
          </div>
        </div>
      </div>
      <div class="overlay overlay-right overlay-bottom mb-6 mr-6" v-show="activityFinished">
        <div class="vcenter-parent">
          <div class="content translucent-text p-5 is-rounded activityStartGestureCard">
            <GestureIcon class="activityEndGestureCard" :gesture="'forward'" />
            <p>Advance to next activity</p>
          </div>
        </div>
      </div> -->
    </div>


    <div class="is-flex is-flex-direction-column is-align-items-center is-justify-content-space-between">
      <div class="master-bar mt-4">
        <SegmentedProgressBar
          :segments="progressSegments"
          :progress="videoTime"
        />
      </div>
      <!-- <div class="mt-4 mb-4 buttons is-centered">
        <button
          class="button"
          @click="gotoPreviousActivity"
          :class="{
            'is-white': activityFinished,
            'is-light': !activityFinished,
          }"
          :disabled="activityId === 0">Previous</button>
        <button
            class="button"
          @click="repeatActivity"
          :class="{
            'is-white': activityFinished,
            'is-light': !activityFinished,
          }"
          :disabled="!activityFinished">Repeat <i class="fa fa-repeat" aria-hidden="true"></i>
        </button>
        <button
          class="button"
          :class="{
            'is-white': showPlayGestureIcon,
            'is-light': !showPlayGestureIcon,
          }"
          @click="playActivity(undefined, true)"
          :disabled="!showPlayGestureIcon">Start Activity</button>
        <button
          class="button"
          @click="gotoNextActivity"
          :class="{
            'is-white': activityFinished,
            'is-light': !activityFinished,
          }">
          <span v-if="hasNextActivity">Next</span>
          <span v-else>Finish Lesson</span></button>
        <button
          class="button"
          @click="startSaveFrames"
          :disabled="!canSaveFrame"
          :class="{'is-loading': isSavingFrames}">Save Frames</button> -->
      <!-- </div> -->
    </div>

  </div>
</template>

<script lang="ts">
import Constants from '@/services/Constants';
import DanceLesson, { Activity, PauseInfo, DanceUtils } from '@/model/VideoLesson';
import {
  computed, ComputedRef, defineComponent, nextTick, onBeforeUnmount, onMounted, Ref, ref, toRefs, watch,
} from 'vue';
import {
  GestureNames, setupGestureListening, setupMediaPipeListening, TrackingActions,
} from '@/services/EventHub';
import { DatabaseEntry } from '@/services/MotionDatabase';
import motionRecorder from '@/services/MotionRecorder';
import InstructionCarousel, { Instruction } from '@/components/elements/InstructionCarousel.vue';
import { Landmark } from '@/services/MediaPipeTypes';
import Utils from '@/services/Utils';
import SegmentedProgressBar, { ProgressSegmentData, calculateProgressSegments } from '../elements/SegmentedProgressBar.vue';
import ActivityVideoPlayer from '@/components/elements/ActivityVideoPlayer.vue';
import WebcamBox from '../elements/WebcamBox.vue';
import GestureIcon from '../elements/GestureIcon.vue';

const { DefaultPauseDuration } = Constants; // 1.5 seconds

const ActivityPlayState = Object.freeze({
  AwaitingPlayGesture: 'AwaitingPlayGesture',
  PendingStart: 'PendingStart',
  Playing: 'Playing',
  ActivityEnded: 'ActivityEnded',
});

//
// TODO!
//   * Update segment breaks in activity to have the first activity
//     start time and the last activity end time.
//

const TRACKING_ID = 'LearningScreen';

function setupFrameRecording(activity: ComputedRef<Activity | null>, videoTime: Ref<number>, videoPlayer: Ref<null | typeof ActivityVideoPlayer>, playActivity: Function) {
  const isSavingFrames = ref(false);
  let recordingSessionId = -1;

  const lastPose = {
    frameId: -1,
    pose: null as null | Landmark[],
    timestamp: 0,
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
          lastPose.timestamp,
          mpResults,
          { poseLandmarks: lastPose.pose ?? undefined },
        );
      }
    },
    (frameId) => {
      lastPose.frameId = frameId;
      lastPose.pose = videoPlayer.value?.currentPose ?? null;
      lastPose.timestamp = videoTime.value;
    },
  );
  const canSaveFrame = computed(() => {
    if (isSavingFrames.value) return false;
    if (!activity.value) return false;
    return activity.value.demoVisual === 'skeleton' && activity.value.userVisual !== 'none';
  });
  async function startSaveFrames() {
    recordingSessionId = await motionRecorder.startRecordingSession(
      { width: 640, height: 480 },
      videoPlayer.value?.getVideoDimensions(),
    );

    isSavingFrames.value = true;

    playActivity(5, true);
  }
  async function concludeSaveFrames() {

    await Utils.sleep(1.5);

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
    ActivityVideoPlayer,
    InstructionCarousel,
    WebcamBox,
    GestureIcon,
  },
  props: {
    targetDance: Object,
    targetLesson: Object,
  },
  setup(props, { emit }) {

    const { targetLesson, targetDance } = toRefs(props);

    const activityState = ref(ActivityPlayState.AwaitingPlayGesture);
    const showPlayGestureIcon = computed(() => activityState.value === ActivityPlayState.AwaitingPlayGesture);

    const videoPlayer = ref(null as null | typeof ActivityVideoPlayer);
    const videoTime = ref(0);

    const activityId = ref(0);
    const activity = computed(() => {
      const lesson = targetLesson?.value as unknown as DanceLesson | null;
      return lesson?.activities[activityId.value] ?? null;
    });

    const emphasizedJoints = computed(() => activity.value?.emphasizedJoints ?? []);
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

      if ((state === ActivityPlayState.AwaitingPlayGesture || state === ActivityPlayState.PendingStart) && mActivity.startInstruction) {
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
      const curActivity = activity.value;
      if (lesson && curActivity) return calculateProgressSegments(lesson, curActivity);
      return [];
    });

    function playVideo(vidActivity: Activity, pause?: number | undefined) {
      const vidPlayer = videoPlayer.value;
      if (!vidPlayer) {
        console.error('LEARNING SCREEN:: Aborting video playback: vidPlayer is null');
        return;
      }

      activityState.value = ActivityPlayState.PendingStart;

      vidPlayer.play(
        vidActivity.startTime,
        vidActivity.endTime,
        vidActivity.practiceSpeed ?? 1,
        vidActivity.pauses ?? [],
        pause ?? DefaultPauseDuration,
        () => {
          activityState.value = ActivityPlayState.Playing;
        },
      );
    }

    function playActivity(pause?: number | undefined, forcePlay?: boolean | undefined) {

      pauseInstructs.value.splice(0);
      activityState.value = ActivityPlayState.AwaitingPlayGesture;
      const vidActivity = activity.value;
      const vidPlayer = videoPlayer.value;
      if (!vidPlayer || !vidActivity) {
        console.error('LEARNING SCREEN:: Aborting video playback: vidPlayer or lessonActivity is null', vidPlayer, vidActivity);
        return;
      }
      // const startingNow = forcePlay || (activityId.value !== 0 && !DanceUtils.shouldPauseBeforeActivity(vidActivity));

      // vidPlayer.setTime(vidActivity.startTime);

      // if (startingNow) {
      //   playVideo(vidActivity, pause);
      //   console.log(`LEARNING SCREEN:: Scheduling playback for activity ${activityId.value}`);
      // } else {
      //   console.log(`LEARNING SCREEN:: Setting start & pausing for userinput for activity ${activityId.value}`);
      // }
    }

    function gotoActivity(delta: number) {
      activityState.value = ActivityPlayState.AwaitingPlayGesture;
      if (!hasNextActivity.value) {
        emit('lesson-completed');
        return;
      }
      if (activityId.value === 0 && delta < 0) {
        // Don't adjust activityId - we can't go back (simply repeat).
        playActivity();
        return;
      }
      activityId.value += delta;
      playActivity();
    }
    function repeatActivity() {
      gotoActivity(0);
    }
    function gotoPreviousActivity() {
      gotoActivity(-1);
    }

    function gotoNextActivity() {
      gotoActivity(1);
    }

    const {
      isSavingFrames, canSaveFrame, startSaveFrames, concludeSaveFrames,
    } = setupFrameRecording(activity, videoTime, videoPlayer, playActivity);

    function onActivityFinished() {
      activityState.value = ActivityPlayState.ActivityEnded;
      console.log('LEARNING SCREEN:: Activity finished');

      if (isSavingFrames.value) concludeSaveFrames();
    }

    const isTrackingUser = computed(() => {
      if (activity.value?.userVisual === 'skeleton') return true;
      if (activityState.value === ActivityPlayState.ActivityEnded || activityState.value === ActivityPlayState.AwaitingPlayGesture) return true;
      if (isSavingFrames.value) return true;
      return false;
    });
    watch(isTrackingUser, (val) => {
      if (val) TrackingActions.requestTracking(TRACKING_ID);
      else TrackingActions.endTrackingRequest(TRACKING_ID);
    });

    onMounted(() => {
      nextTick(() => {
        if (isTrackingUser.value) TrackingActions.requestTracking(TRACKING_ID);
        else TrackingActions.endTrackingRequest(TRACKING_ID);
      });
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
      [GestureNames.namaste]: () => {
        if (activityState.value === ActivityPlayState.AwaitingPlayGesture) {
          playActivity(undefined, true);
        }
      },
    });
    onBeforeUnmount(() => {
      TrackingActions.endTrackingRequest(TRACKING_ID);
    });

    onMounted(() => {
      playActivity();
    });

    return {
      activityState,
      ActivityPlayState,
      showPlayGestureIcon,
      playActivity,
      progressSegments,
      activity,
      activityId,
      activityCount,
      activityTitle,
      emphasizedJoints,
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
      repeatActivity,
      gotoNextActivity,
      hasNextActivity,

      canSaveFrame,
      isSavingFrames,
      startSaveFrames,
      isTrackingUser,
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
  width: 100%;
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

.activityEndGestureCard {
  max-width: 4rem;
}

.activityStartGestureCard {
  max-width: 8rem;
}
</style>
