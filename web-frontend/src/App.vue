<template>
<div class="app">

  <div id="debugData" v-show="isDebug" class="tags p-2 mb-0 has-background-dark has-text-grey-lighter">
    <span class="tag">ParticipantId: {{participantId ?? 'null'}}</span>
  </div>

  <MainMenu
        v-show="state === State.MainMenu"
        @lesson-selected="lessonSelected"
        @create-lesson-selected="createLessonSelected"
        @workflow-selected="startWorkflow"
        @create-workflow-selected="state = State.CreateWorkflow"
        @keyframeselectortool-selected="startKeyframeSelection"
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

  <KeyframeSelectorTool
        v-if="state === State.KeyframeSelectorTool"
        @back-selected="goHome"
        v-model:modelValue="keyframes"
        :videoEntry="currentVideo"/>

  <div v-bind:class="{ 'is-active': state == State.LessonActive }" class="modal">
    <div class="modal-background"></div>
    <div class="container" style="max-height=100vh; max-width=100vw;">
      <div class="vcenter-parent">
        <div class="box" >
          <MiniLessonPlayer
            v-if="state == State.LessonActive"
            :videoEntry="currentVideo"
            :miniLesson="currentLesson"
            @lesson-completed="goHome"
            :maxVideoHeight="'calc(100vh - 152px - 3.75rem)'"
            :enableCompleteLesson="true"/>
        </div>
      </div>
    </div>
    <button class="modal-close is-large" aria-label="close" @click="goHome"></button>
  </div>
</div>
</template>

<script lang="ts">
import {
  computed, defineComponent, nextTick, ref,
} from 'vue';
import webcamProvider from '@/services/WebcamProvider';
import VideoDatabaseEntry from '@/model/VideoDatabaseEntry';
import WorkflowMenu from '@/components/screens/WorkflowMenu.vue';
import CreateWorkflowScreen from '@/components/screens/CreateWorkflowScreen.vue';
import MiniLessonPlayer from '@/components/elements/MiniLessonPlayer.vue';
import KeyframeSelectorTool from '@/components/tools/KeyframeSelectorTool.vue';
import CameraSurface from './components/CameraSurface.vue';
import OnboardingUI from './components/OnboardingUI.vue';
import MainMenu from './components/screens/MainMenu.vue';
// import LearningScreen from './components/screens/LearningScreen.vue';
import MiniLesson from './model/MiniLesson';

import CreateLessonScreen from './components/screens/CreateLessonScreen.vue';
import workflowManager from './services/WorkflowManager';
import optionsManager from './services/OptionsManager';

const State = {
  MainMenu: 'MainMenu',
  LessonActive: 'LessonActive',
  WorkflowActive: 'WorkflowActive',
  CreateLesson: 'CreateLesson',
  CreateWorkflow: 'CreateWorkflow',
  KeyframeSelectorTool: 'KeyframeSelectorTool',
};

export default defineComponent({
  name: 'App',
  components: {
    MainMenu,
    WorkflowMenu,
    KeyframeSelectorTool,
    CreateLessonScreen,
    CreateWorkflowScreen,
    MiniLessonPlayer,
  },
  setup() {
    const state = ref(State.MainMenu);
    const cameraSurface = ref(null as typeof CameraSurface | null);
    const hasCompletedOnboarding = ref(false);

    const currentVideo = ref(null as VideoDatabaseEntry | null);
    const currentLesson = ref(null as MiniLesson | null);
    const keyframes = ref([] as number[]);

    function lessonSelected(videoEntry: VideoDatabaseEntry, lesson: MiniLesson) {
      currentVideo.value = videoEntry;
      currentLesson.value = lesson;

      state.value = State.LessonActive;
      // if (webcamProvider.webcamStatus.value === 'running') state.value = State.LessonActive;
      // else state.value = State.PromptStartWebcam;
    }

    function startKeyframeSelection(videoEntry: VideoDatabaseEntry, kfs: number[]) {
      console.log('startKeyframeSelection', videoEntry, kfs);
      keyframes.value = kfs;
      currentVideo.value = videoEntry;
      state.value = State.KeyframeSelectorTool;
    }

    function goHome() {
      state.value = State.MainMenu;
      currentVideo.value = null;
      currentLesson.value = null;
    }

    return {
      currentVideo,
      currentLesson,
      lessonSelected,
      goHome,
      keyframes,
      state,
      cameraSurface,
      State,
      startKeyframeSelection,
      startedWithWorkflow: ref(false),
      isDebug: optionsManager.isDebug,
      participantId: optionsManager.participantId,
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
    createLessonSelected(dance: VideoDatabaseEntry) {
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
