<template>
<div class="app">
   <div id="aboveSurface">
     <span id="topbarLeft"></span>
     <span class="spacer"></span>
     <span style="color:transparent">{{state}}</span>
     <span class="spacer"></span>
     <span id="topbarRight"></span>

  </div>

  <DanceMenu
        v-on:dance-selected="danceSelected"
        v-if="state === State.DanceMenu"
      />

  <CameraSurface
    ref="cameraSurface"
    @tracking-attained="onTrackingAttained()"
    v-show="state !== State.DanceMenu">

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

      <div class="vcenter-parent" v-if="state === State.LoadingTracking">
        <div class="loader-wrapper">
          <div class="loader is-loading"></div>
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
import { defineComponent, ref } from 'vue';
import CameraSurface from './components/CameraSurface.vue';
import OnboardingUI from './components/OnboardingUI.vue';
import DanceMenu from './components/screens/DanceMenu.vue';
import LearningScreen from './components/screens/LearningScreen.vue';
import DanceEntry, { LessonSelection } from './model/DanceEntry';
import DanceLesson from './model/DanceLesson';
import WebcamPromptCard from './components/elements/WebcamPromptCard.vue';

const State = {
  DanceMenu: 'DanceMenu',
  PromptStartWebcam: 'PromptStartWebcam',
  LoadingTracking: 'OnboardingLoading',
  Onboarding: 'Onboarding',
  LessonActive: 'LessonActive',
};

export default defineComponent({
  name: 'App',
  components: {
    CameraSurface,
    OnboardingUI,
    DanceMenu,
    LearningScreen,
    WebcamPromptCard,
  },
  setup() {
    const state = ref(State.DanceMenu);
    const cameraSurface = ref(null as typeof CameraSurface | null);
    const hasStartedWebcam = ref(false);
    const hasCompletedOnboarding = ref(false);

    const currentDance = ref(null as DanceEntry | null);
    const currentLesson = ref(null as DanceLesson | null);

    function danceSelected(sel: LessonSelection) {
      state.value = State.LoadingTracking;
      currentDance.value = sel.dance;
      currentLesson.value = sel.lesson;

      if (hasStartedWebcam.value) state.value = State.LessonActive;
      else state.value = State.PromptStartWebcam;
    }

    function goHome() {
      state.value = State.DanceMenu;
      currentDance.value = null;
      currentLesson.value = null;
    }

    function startWebcam() {
      console.log('Starting Webcam');
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const camSurface: any = cameraSurface.value;
      hasStartedWebcam.value = true;
      camSurface.startTracking();
      state.value = State.LoadingTracking;
    }

    function onTrackingAttained() {
      console.log('Tracking attained');

      if (hasCompletedOnboarding.value) state.value = State.LessonActive;
      else state.value = State.Onboarding;
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

.loader-wrapper {
  width: 200px;
  height: 200px;
  background: rgba(0, 0, 0, 0.3);
  padding: 3em;
  border-radius: 9999px;

  .loader {
    width: 100%;
    height: 100%;
  }
}

#aboveSurface {
  padding: 1rem;
  // margin-top: 1rem;
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
  border-radius: 0 0 0.5rem 0.5rem;
}

#topbarLeft {
  display: flex;
  flex-direction: row;
}
#topbarRight {
  display: flex;
  flex-direction: row-reverse;
}

.background-blur {
  backdrop-filter: blur(4px);
  background: rgba(0, 0, 0, 0.3);
}
</style>
