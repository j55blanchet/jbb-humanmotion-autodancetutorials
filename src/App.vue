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

      <div class="vcenter-parent" v-if="state === State.StartingWebcam">
        <div class="translucent-text is-rounded">
          <div class="loader is-loading"></div>
        </div>
      </div>

      <div class="vcenter-parent" v-if="state === State.LoadingTracking">
        <div class="translucent-text is-rounded">
          <progress class="loader-progress progress is-primary m-4"></progress>
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
import webcamProvider from '@/services/WebcamProvider';
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
  StartingWebcam: 'StartingWebcam',
  LoadingTracking: 'LoadingTracking',
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
    const hasCompletedOnboarding = ref(false);

    const currentDance = ref(null as DanceEntry | null);
    const currentLesson = ref(null as DanceLesson | null);

    function danceSelected(sel: LessonSelection) {
      currentDance.value = sel.dance;
      currentLesson.value = sel.lesson;

      if (webcamProvider.hasStartedWebcam()) state.value = State.LessonActive;
      else state.value = State.PromptStartWebcam;
    }

    function goHome() {
      state.value = State.DanceMenu;
      currentDance.value = null;
      currentLesson.value = null;
    }

    async function startTracking() {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const camSurface: any = cameraSurface.value;
      state.value = State.LoadingTracking;
      camSurface.startTracking();
    }

    async function startWebcam() {
      console.log('Starting Webcam');

      if (!webcamProvider.hasStartedWebcam()) {
        state.value = State.StartingWebcam;

        try {
          await webcamProvider.startWebcam();
        } catch (e) {
          console.error("Couldn't start webcam", e);
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

.loader {
  width: 200px;
  height: 200px;
}

.loader-progress {
  width: 200px;
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
