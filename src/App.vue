<template>
<div class="app">

  <MainMenu
        v-show="state === State.MainMenu"
        @pose-drawer-selected="poseDrawerSelected"
        @lesson-selected="lessonSelected"
        @create-lesson-selected="createLessonSelected"
        @workflow-selected="startWorkflow"
        @create-workflow-selected="state = State.CreateWorkflow"
      />

  <CreateLessonScreen
        v-if="state === State.CreateLesson"
          :motion="currentVideo"
          @back-selected="goHome"
          @lesson-created="goHome" />

  <CreateWorkflowScreen
    v-if="state === State.CreateWorkflow"
    @back-selected="goHome"
    @workflow-created="goHome"
    />

  <WorkflowMenu
        v-if="state === State.WorkflowActive"
        @back-selected="goHome"
        :showBackButton="!startedWithWorkflow"/>

  <PoseDrawerTest
        v-if="state === State.PoseDrawingTester"
        @back-selected="goHome" />

  <div v-bind:class="{ 'is-active': state == State.LessonActive }" class="modal">
    <div class="modal-background"></div>
    <div class="container" style="max-height=100vh; max-width=100vw;">
      <div class="vcenter-parent">
        <div class="box" >
          <VideoLessonPlayer
            v-if="state == State.LessonActive"
            :videoEntry="currentVideo"
            :videoLesson="currentLesson"
            @lesson-completed="goHome"
            :maxVideoHeight="'calc(100vh - 152px - 3.75rem)'"
            :enableCompleteLesson="true"/>
        </div>
      </div>
    </div>
    <button class="modal-close is-large" aria-label="close" @click="goHome"></button>
  </div>

  <div id="aboveSurface" class="pb-4 pt-4">
     <span id="topbarLeft"></span>
     <span class="spacer"></span>
     <span id="topbarCenter"></span>
     <span class="spacer"></span>
     <span id="topbarRight"></span>
  </div>
  <CameraSurface
    ref="cameraSurface"
    @tracking-attained="onTrackingAttained()"
    v-show="showCameraSurface">

    <template v-slot:background>
      <img v-show="state == State.OnboardingLoading"
      src="./assets/tiktokdances.jpg"
      alt="Background Image">
    </template>

    <template v-slot:ui>

      <!-- <LearningScreen v-if="state == State.LessonActive"
        :target-dance="currentVideo"
        :target-lesson="currentLesson"
        @lesson-completed="goHome"
        @back-selected="goHome"
        style="width: 1280px"
        height="auto"
      /> -->

     <WebcamPromptCard v-if="state === State.PromptStartWebcam"
      @cancel-selected="state = State.MainMenu"
      @startWebcamSelected="startWebcam"
     />

      <div class="vcenter-parent" v-if="state === State.StartingWebcam">
        <div class="translucent-text is-rounded has-text-centered">
          <div class="content">
            <h3 class="has-text-white m-2">Starting Webcam...</h3>
          </div>
          <div class="loader-progress loader is-loading mt-5 mb-5"></div>
        </div>
      </div>

      <div class="vcenter-parent" v-if="state === State.LoadingTracking">
        <div class="translucent-text is-rounded has-text-centered">
          <div class="content has-text-white m-2 has-text-centered">
            <h3 class="has-text-white">Starting Gestures...</h3>
          </div>
          <div class="loader-progress loader is-loading mt-5 mb-5"></div>
        </div>
      </div>

      <OnboardingUI v-if="state == State.Onboarding"
        @onboarding-complete="state= State.LessonActive "/>
    </template>

  </CameraSurface>
  <div id="belowSurface"></div>
</div>
</template>

<script lang="ts">
import {
  computed, defineComponent, nextTick, ref,
} from 'vue';
import webcamProvider from '@/services/WebcamProvider';
import { DatabaseEntry } from '@/services/MotionDatabase';
import WorkflowMenu from '@/components/screens/WorkflowMenu.vue';
import CreateWorkflowScreen from '@/components/screens/CreateWorkflowScreen.vue';
import VideoLessonPlayer from '@/components/elements/VideoLessonPlayer.vue';
import CameraSurface from './components/CameraSurface.vue';
import OnboardingUI from './components/OnboardingUI.vue';
import MainMenu from './components/screens/MainMenu.vue';
// import LearningScreen from './components/screens/LearningScreen.vue';
import VideoLesson from './model/MiniLesson';
import WebcamPromptCard from './components/elements/WebcamPromptCard.vue';

import PoseDrawerTest from './components/screens/PoseDrawerTest.vue';
import CreateLessonScreen from './components/screens/CreateLessonScreen.vue';
import workflowManager from './services/WorkflowManager';
import optionsManager from './services/OptionsManager';

const State = {
  MainMenu: 'MainMenu',
  PromptStartWebcam: 'PromptStartWebcam',
  StartingWebcam: 'StartingWebcam',
  LoadingTracking: 'LoadingTracking',
  Onboarding: 'Onboarding',
  LessonActive: 'LessonActive',
  WorkflowActive: 'WorkflowActive',
  PoseDrawingTester: 'PoseDrawingTester',
  CreateLesson: 'CreateLesson',
  CreateWorkflow: 'CreateWorkflow',
};

export default defineComponent({
  name: 'App',
  components: {
    CameraSurface,
    OnboardingUI,
    MainMenu,
    WorkflowMenu,
    // LearningScreen,
    WebcamPromptCard,
    PoseDrawerTest,
    CreateLessonScreen,
    CreateWorkflowScreen,
    VideoLessonPlayer,
  },
  setup() {
    const state = ref(State.MainMenu);
    const cameraSurface = ref(null as typeof CameraSurface | null);
    const hasCompletedOnboarding = ref(false);

    const currentVideo = ref(null as DatabaseEntry | null);
    const currentLesson = ref(null as VideoLesson | null);

    const showCameraSurface = computed(() => [
      State.PromptStartWebcam,
      State.StartingWebcam,
      State.LoadingTracking,
      State.Onboarding,
      // State.LessonActive,
    ].indexOf(state.value) !== -1);

    function lessonSelected(videoEntry: DatabaseEntry, lesson: VideoLesson) {
      currentVideo.value = videoEntry;
      currentLesson.value = lesson;

      state.value = State.LessonActive;
      // if (webcamProvider.webcamStatus.value === 'running') state.value = State.LessonActive;
      // else state.value = State.PromptStartWebcam;
    }

    function goHome() {
      state.value = State.MainMenu;
      currentVideo.value = null;
      currentLesson.value = null;
    }

    async function startTracking() {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      nextTick(() => {
        const camSurface: any = cameraSurface.value;
        state.value = State.LoadingTracking;
        camSurface.startTracking();
      });
    }

    async function startWebcam() {
      console.log('Starting Webcam');

      if (webcamProvider.webcamStatus.value !== 'running') {
        state.value = State.StartingWebcam;

        try {
          await webcamProvider.startWebcam();
        } catch (e) {
          console.error('Error starting webcam: ', e);
          // eslint-disable-next-line no-alert
          alert('Failed to start the webcam\n\nPlease ensure this is the only app using the camera and that you\'ve allowed camera access in your browser.');
          state.value = State.MainMenu;
          return;
        }
      }

      state.value = State.LoadingTracking;
      try {
        await startTracking();
      } catch (e) {
        console.error("Couldn't start tracking", e);
      }
    }

    function onTrackingAttained() {
      console.log('Tracking attained');
      if (hasCompletedOnboarding.value) {
        state.value = State.LessonActive;
      } else state.value = State.Onboarding;
    }

    return {
      showCameraSurface,
      currentVideo,
      currentLesson,
      lessonSelected,
      goHome,
      startWebcam,
      onTrackingAttained,
      state,
      cameraSurface,
      State,
      startedWithWorkflow: ref(false),
    };
  },
  mounted() {
    // If app was launched with a workflowId, skip straight
    // to that workflow
    if (optionsManager.workflowId.value) {
      if (this.startWorkflow(optionsManager.workflowId.value)) {
        this.startedWithWorkflow = true;
      }
    }
  },
  methods: {
    poseDrawerSelected() {
      this.state = State.PoseDrawingTester;
    },
    createLessonSelected(dance: DatabaseEntry) {
      this.currentVideo = dance;
      this.state = State.CreateLesson;
    },
    startWorkflow(workflowId: string) {
      console.log('Starting workflow', workflowId);
      if (workflowManager.setActiveFlow(workflowId)) {
        this.state = State.WorkflowActive;
        return true;
      }
      return false;
    },
  },
});
</script>

<style lang="scss">

body, html {
  margin: 0;
  padding: 0;
  width: 100%;
  background-color: #00d1b2;
  // background-image: linear-gradient(45deg, #00d1b2 0%, #3475da 100%);

  // background-color: #FF9A8B;
  // background-image: linear-gradient(135deg, #B721FF 0%, #145eb3 100%);

  background-image: linear-gradient(120deg, #daece1 0%, #d1d1d1 100%);

  background-size: 100vw 100vh;
  background-attachment: fixed;
}

.vcenter-parent {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 100%;
}

.loader-progress {
  width: 100px;
  height: 100px;
  margin: auto;
}

#aboveSurface {
  display: flex;
  flex-direction: row;
  flex-wrap: wrap;

  span {
    flex: 0 0 auto;
  }
  .spacer {
    flex: 1 1 0;
  }

  width: 1280px;
  margin: auto;
}

#belowSurface {
  width: 1280px;
  margin: auto;
}

#topbarLeft, #topbarRight, #topbarCenter {
  display: flex;
  flex-direction: row;
  align-items: center;
}

.background-blur {
  backdrop-filter: blur(4px);
  background: rgba(0, 0, 0, 0.75);
}

.translucent-text {
  backdrop-filter: blur(4px);
  color: white;
  padding: 10px 20px;
  background: rgba(0, 0, 0, 0.55);
}

.translucent-text.is-rounded {
  border-radius: 0.25rem;
}

.is-slightly-rounded {
  border-radius: 0.25rem;
}

</style>
