<template>
<div class="app">
   <div id="aboveSurface" class="pb-4 pt-4">
     <span id="topbarLeft"></span>
     <span class="spacer"></span>
     <span id="topbarCenter"></span>
     <span class="spacer"></span>
     <span id="topbarRight"></span>
  </div>

  <DanceMenu
        v-show="state === State.DanceMenu"
        @pose-drawer-selected="poseDrawerSelected"
        @dance-selected="danceSelected"
        @create-lesson-selected="createLessonSelected"
      />

  <CreateLessonScreen
        v-if="state === State.CreateLesson"
          :motion="currentDance"
          @back-selected="goHome"
          @lesson-created="goHome" />

  <PoseDrawerTest
        v-if="state === State.PoseDrawingTester"
        @back-selected="goHome" />

  <CameraSurface
    ref="cameraSurface"
    @tracking-attained="onTrackingAttained()"
    v-show="[State.DanceMenu, State.CreateLesson, State.PoseDrawingTester].indexOf(state) === -1">

    <template v-slot:background>
      <img v-show="state == State.OnboardingLoading"
      src="./assets/tiktokdances.jpg"
      alt="Background Image">
    </template>

    <template v-slot:ui>

      <LearningScreen v-if="state == State.LessonActive"
        :target-dance="currentDance"
        :target-lesson="currentLesson"
        @lesson-completed="goHome"
        @back-selected="goHome"
      />

     <WebcamPromptCard v-if="state === State.PromptStartWebcam"
      @cancel-selected="state = State.DanceMenu"
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
import { defineComponent, nextTick, ref } from 'vue';
import webcamProvider from '@/services/WebcamProvider';
import { DatabaseEntry } from '@/services/MotionDatabase';
import CameraSurface from './components/CameraSurface.vue';
import OnboardingUI from './components/OnboardingUI.vue';
import DanceMenu from './components/screens/DanceMenu.vue';
import LearningScreen from './components/screens/LearningScreen.vue';
import DanceLesson from './model/DanceLesson';
import WebcamPromptCard from './components/elements/WebcamPromptCard.vue';

import PoseDrawerTest from './components/screens/PoseDrawerTest.vue';
import CreateLessonScreen from './components/screens/CreateLessonScreen.vue';

const State = {
  DanceMenu: 'DanceMenu',
  PromptStartWebcam: 'PromptStartWebcam',
  StartingWebcam: 'StartingWebcam',
  LoadingTracking: 'LoadingTracking',
  Onboarding: 'Onboarding',
  LessonActive: 'LessonActive',
  PoseDrawingTester: 'PoseDrawingTester',
  CreateLesson: 'CreateLesson',
};

export default defineComponent({
  name: 'App',
  components: {
    CameraSurface,
    OnboardingUI,
    DanceMenu,
    LearningScreen,
    WebcamPromptCard,
    PoseDrawerTest,
    CreateLessonScreen,
  },
  setup() {
    const state = ref(State.DanceMenu);
    const cameraSurface = ref(null as typeof CameraSurface | null);
    const hasCompletedOnboarding = ref(false);

    const currentDance = ref(null as DatabaseEntry | null);
    const currentLesson = ref(null as DanceLesson | null);

    function danceSelected(dance: DatabaseEntry, lesson: DanceLesson) {
      currentDance.value = dance;
      currentLesson.value = lesson;

      if (webcamProvider.webcamStatus.value === 'running') state.value = State.LessonActive;
      else state.value = State.PromptStartWebcam;
    }

    function goHome() {
      state.value = State.DanceMenu;
      currentDance.value = null;
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
          state.value = State.DanceMenu;
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
      currentDance,
      currentLesson,
      danceSelected,
      goHome,
      startWebcam,
      onTrackingAttained,
      state,
      cameraSurface,
      State,
    };
  },
  methods: {
    poseDrawerSelected() {
      this.state = State.PoseDrawingTester;
    },
    createLessonSelected(dance: DatabaseEntry) {
      this.currentDance = dance;
      this.state = State.CreateLesson;
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

  background-image: linear-gradient(120deg, #84fab0 0%, #8fd3f4 100%);

  background-size: 100vw 100vh;
  background-attachment: fixed;
}

.card {
  display: inline-block;
  max-width: 90%;
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
