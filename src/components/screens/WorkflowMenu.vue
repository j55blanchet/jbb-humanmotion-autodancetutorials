<template>

  <teleport to="#testData" v-if="optionsManager.isTest">
    <span class="tag">Workflow Id: {{workflow?.id ?? 'null'}}</span>
    <span class="tag">Experiment Mode: <input type="checkbox" v-model="enableExperimentMode"></span>

    <span class="tag">
      Workflow: {{Math.round(workflowSecsElapsed)}}s elapsed, {{workflowSecondsRemainingString}} remaining
    </span>
    <span class="tag">
      Stage: {{Math.round(stageSecsElapsed)}}s, {{stageSecondsRemainingString}} remaining
    </span>
  </teleport>

  <section class="section workflow-menu">

    <div class="hero is-primary block" v-if="showHeader">
      <div class="hero-body">
        <div class="container">
          <p class="title">
            {{workflow?.title}}
          </p>
        </div>
      </div>
    </div>

    <div class="container block" v-if="showBackButton">
      <button class="button" @click="$emit('back-selected')">&lt; Back</button>
    </div>

    <div class="block" v-for="(stage, i) in workflow?.stages ?? []" :key="i">

      <p class="subtitle has-text-centered">
        <span class="icon-text">
          <span v-text="stage.title"></span>
          <span class="icon" v-if="isStageCompleted(stage)"><i class="fa fa-check"></i></span>

          <span
            v-if="activeStageIndex === i && stageSecondsRemaining !== Infinity"
            class="is-size-6"
            >
            &nbsp;
            {{stageSecondsRemainingString}} Remaining
          </span>
        </span>
      </p>

      <div class="grid-menu container block">
        <div class="box m-4"
            :class="{
                  'is-clickable': stepInfo.isClickable,
                  'hover-expand': stepInfo.isClickable,
                  'has-text-grey': !stepInfo.isClickable,
                  'has-background-grey-lighter': !stepInfo.isClickable,
                  'has-background-white-ter': stepInfo.isClickable && !stepInfo.isNextStep,
                  'has-border-success': stepInfo.step.status === 'completed',
                  'has-border-info': stepInfo.step === nextStepInStage,
                  'has-border-grey': stepInfo.isClickable && stepInfo.step !== nextStepInStage && stepInfo.step.status !== 'completed'
                }"
            @click="stepInfo.isClickable && startWorkflowStep(stepInfo.step)"
            v-for="(stepInfo, j) in getStepInfo(stage)" :key="j">
          <article
            class="level"
          >
            <div class="level-left">
              <div class="level-item">
                <p class="image is-48x48" v-if="stepInfo.dbEntry?.thumbnailSrc">
                  <img class="is-100percent is-contain" :src="stepInfo.dbEntry?.thumbnailSrc" :alt="stepInfo.step.title">
                </p>
                <p class="icon is-large" v-else>
                  <i class="fas fa-2x fa-align-center" v-if="stepInfo.step.type === 'InstructionOnly'"></i>
                  <i class="fas fa-2x fa-images" v-if="stepInfo.step.type === 'MiniLessonEmbedded' || stepInfo.step.type === 'MiniLessonnReference'"></i>
                  <i class="fas fa-2x fa-camera" v-if="stepInfo.step.type === 'UploadTask'"></i>
                </p>
              </div>
              <div class="level-item">
                <div>
                  <p v-text="stepInfo.step.title"></p>
                  <p v-if="stepInfo.waitingForTimeExpiration" class="is-size-7">&nbsp;in {{stageSecondsRemainingString}}</p>
                  <p v-if="stepInfo.isClickable" class="is-size-7">
                    <span v-if="stepInfo.isComplete">Click to repeat</span>
                    <span v-if="stepInfo.isNextStep">Next Up</span>
                  </p>
                </div>
              </div>
            </div>
            <div class="level-right">
              <div class="level-item">
                <span class="icon is-large">
                  <i class="far fa-check-circle has-text-success" v-if="stepInfo.step.status==='completed'"></i>
                  <i class="far fa-play-circle" v-if="stepInfo.step===nextStepInStage"></i>
                  <i class="far fa-circle" v-if="stepInfo.step !== nextStepInStage && stepInfo.step.status==='notstarted'"></i>
                </span>
              </div>
            </div>
          </article>
        </div>
      </div>

      <div v-bind:class="{ 'is-active': instructionsActive }" class="modal">
        <div class="modal-background"></div>
        <div class="modal-content">
          <div class="box content">
            <h3>{{currentStep?.instructions?.heading}}</h3>
            <p style="white-space: pre-wrap;">{{currentStep?.instructions?.text}}</p>
            <div class="buttons is-right">
              <button class="button is-primary" @click="instructionsFinished">OK</button>
            </div>
          </div>
        </div>
        <button class="modal-close" @click="instructionsActive = false" aria-label="close"></button>
      </div>

      <div v-bind:class="{ 'is-active': lessonActive }" class="modal">
        <div class="modal-background"></div>
        <div class="container" style="max-width: 100vw; max-height: 100vh;">
          <div class="box" style="height:min(90vw, 90vh);width:min(90vh, 90vw);margin-top:calc((100vh - min(90vh, 90vw)) / 2)" >
            <MiniLessonPlayer
              v-if="lessonActive"
              :videoEntry="currentVideoEntry"
              :miniLesson="currentLesson"
              @lesson-completed="lessonCompleted"
              :maxVideoHeight="'calc(100vh - 152px - 3.75rem)'"
              :enableCompleteLesson="true"/>
          </div>
        </div>
        <button class="modal-close is-large" aria-label="close" @click="lessonActive=false"></button>
      </div>

      <div :class="{'is-active': uploadActive}" class="modal">
        <div class="modal-background"></div>
        <div class="modal-content">
          <div class="container">
            <div class="box">
              <FeedbackUploadScreen
                :prompt="currentStep?.upload?.prompt"
                :title="workflow?.title"
                :subtitle="currentStep?.title"
                :uploadFilename="uploadFilename"
                @upload-canceled="uploadActive = false"
                @upload-completed="uploadComplete"
              />
            </div>
          </div>
        </div>
      </div>

      <div :class="{'is-active': timingNotStarted}" class="modal">
        <div class="modal-background"></div>
        <div class="modal-content">
          <div class="container">
            <div class="box">
              <div class="content">
                <h3>Start Timing</h3>
                <button class="button" @click="startTiming">Start</button>
              </div>
            </div>
          </div>
        </div>
      </div>

    </div>

  </section>
</template>

<script lang="ts">
import {
  computed, defineComponent, onBeforeUnmount, onMounted, ref, toRefs, watch, watchEffect,
} from 'vue';
import MiniLessonPlayer from '@/components/elements/MiniLessonPlayer.vue';
import db, { DatabaseEntry } from '@/services/MotionDatabase';
import MiniLesson from '@/model/MiniLesson';
import workflowManager, { TrackingWorkflowStage, TrackingWorkflowStep } from '@/services/WorkflowManager';
import FeedbackUploadScreen from '@/components/screens/FeedbackUploadScreen.vue';
import optionsManager from '@/services/OptionsManager';
import { GetVideoEntryForWorkflowStep, IsMiniLessonStep } from '@/model/Workflow';

function getDurationString(seconds: number) {
  if (seconds === Infinity) return 'Unlimited';
  if (Number.isNaN(seconds)) return 'Unknown';

  const secsRemainingConstrained = Math.max(0, seconds);

  if (secsRemainingConstrained < 3600) {
    return new Date(secsRemainingConstrained * 1000).toISOString().substr(14, 5);
  }
  return new Date(secsRemainingConstrained * 1000).toISOString().substr(11, 8);
}

export default defineComponent({
  name: 'WorkflowMenu',
  props: {
    showHeader: {
      type: Boolean,
      default: true,
    },
    showBackButton: {
      type: Boolean,
      default: true,
    },
    enableTiming: {
      type: Boolean,
      default: false,
    },
    experiment: {
      type: Object,
      required: false,
      default: null,
    },
  },
  emits: [
    'back-selected',
  ],
  components: {
    MiniLessonPlayer,
    FeedbackUploadScreen,
  },
  computed: {
    stages() { return ((this as any).workflow?.stages ?? []) as TrackingWorkflowStage[]; },
    nextStepInStage() {
      // for (let i = 0; i < this.stages.length; i += 1) {
      const stage = (this as any).stages[(this as any).activeStageIndex];
      for (let j = 0; j < stage.steps.length; j += 1) {
        const step = stage.steps[j];
        if (step.status !== 'completed') return step as TrackingWorkflowStep;
      }
      // }
      return null;
    },
    currentVideoEntry(): DatabaseEntry | null {
      if (this.currentStep?.type === 'MiniLessonReference' && this.currentStep?.miniLessonReference) {
        return db.motionsMap.get(this.currentStep.miniLessonReference.clipName) ?? null;
      }
      if (this.currentStep?.type === 'MiniLessonEmbedded' && this.currentStep?.miniLessonEmbedded?.header.clipName) {
        return db.motionsMap.get(this.currentStep.miniLessonEmbedded.header.clipName) ?? null;
      }
      return null;
    },
    currentLesson(): MiniLesson | null {
      if (this.currentStep?.type === 'MiniLessonReference' && this.currentStep?.miniLessonReference) {
        return db.lessonsById.get(this.currentStep.miniLessonReference.lessonId) ?? null;
      }
      if (this.currentStep?.type === 'MiniLessonEmbedded' && this.currentStep?.miniLessonEmbedded) {
        return this.currentStep.miniLessonEmbedded;
      }
      return null;
    },
    uploadFilename(): string {
      const uploadId = this.currentStep?.upload?.identifier ?? 'NoIdentifier';
      const participantId = optionsManager.participantId.value ?? 'Anonomous';
      const workflowId = this.workflow?.id ?? 'NullWorkflow';

      return `${workflowId}-${participantId}-${uploadId}`;
    },
  },
  setup(props, ctx) {

    const currentStep = ref(null as null | TrackingWorkflowStep);
    const instructionsActive = ref(false);
    const lessonActive = ref(false);
    const uploadActive = ref(false);
    const workflow = workflowManager.activeFlow;

    const workflowStartTime = ref(new Date());
    const workflowStageStartTime = ref(new Date());
    const enableExperimentMode = ref(!optionsManager.isTest.value);
    const isTiming = ref(!optionsManager.isTest.value);
    const timingNotStarted = computed(() => isTiming.value && !workflowStartTime.value);

    const activeStageIndex = ref(1);
    const activeStage = computed(() => workflow.value?.stages[activeStageIndex.value] ?? null);
    onMounted(() => {
      workflowStartTime.value = new Date();
      workflowStageStartTime.value = new Date();
    });
    let stageTimer = -1;
    const workflowSecsElapsed = ref(Infinity);
    const workflowSecondsRemaining = computed(() => {
      if (!workflow.value?.experimentMaxTimeSecs) return Infinity;
      return workflow.value.experimentMaxTimeSecs - workflowSecsElapsed.value;
    });
    const workflowSecondsRemainingString = computed(() => getDurationString(workflowSecondsRemaining.value));
    const stageSecsElapsed = ref(Infinity);
    const stageSecondsRemaining = computed(() => {
      if (!activeStage.value?.maxStageTimeSecs) return Infinity;
      return activeStage.value.maxStageTimeSecs - stageSecsElapsed.value;
    });
    const stageSecondsRemainingString = computed(() => getDurationString(stageSecondsRemaining.value));
    onMounted(() => {
      stageTimer = window.setInterval(() => {

        const now = Date.now();
        workflowSecsElapsed.value = (now - workflowStartTime.value.getTime()) / 1000;
        stageSecsElapsed.value = (now - workflowStageStartTime.value.getTime()) / 1000;

      }, 1000);
    });
    onBeforeUnmount(() => {
      clearInterval(stageTimer);
    });

    watch(workflow, () => {
      currentStep.value = null;
    });

    return {
      activeStage,
      activeStageIndex,
      currentStep,
      instructionsActive,
      lessonActive,
      uploadActive,
      workflow,
      optionsManager,

      workflowStartTime,
      timingNotStarted,
      isTiming,
      enableExperimentMode,
      workflowSecsElapsed,
      workflowSecondsRemaining,
      workflowSecondsRemainingString,
      stageSecsElapsed,
      stageSecondsRemaining,
      stageSecondsRemainingString,
    };
  },
  methods: {
    startTiming() {
      this.workflowStartTime = new Date();
    },
    getStepInfo(stage: TrackingWorkflowStage) {

      return stage.steps
        .filter((step) => this.enableExperimentMode || !(step.experiment?.showInExperimentOnly ?? false))
        .map((step) => {

          const isTestMode = !this.enableExperimentMode;
          const isInActiveStage = this.activeStage === stage;
          const isTimeExpiredTask = step.experiment?.isTimeExpiredTask ?? false;
          const stageTimeExpired = this.stageSecondsRemaining <= 0;
          const waitingForTimeExpiration = isTimeExpiredTask && !stageTimeExpired;

          return {
            step,
            isComplete: step.status === 'completed',
            isNextStep: step === this.nextStepInStage,
            dbEntry: GetVideoEntryForWorkflowStep(db, step),
            isClickable: (isTestMode || isInActiveStage)
                        && (!isTimeExpiredTask || !stageTimeExpired)
                        && !waitingForTimeExpiration,
            waitingForTimeExpiration,
          };
        });
    },
    instructionsFinished() {
      this.instructionsActive = false;
      const step = this.currentStep;
      if (!step) return;
      step.status = 'inprogress';
      this.continueWorkflowStep(step);
    },
    startWorkflowStep(item: TrackingWorkflowStep) {
      // if (!this.isClickable(item)) return;
      this.currentStep = item;
      if (item.type === 'InstructionOnly') {
        this.instructionsActive = true;
        return;
      }
      this.continueWorkflowStep(item);
    },
    continueWorkflowStep(item: TrackingWorkflowStep) {
      if (item.type === 'InstructionOnly') {
        // Instructions only - there's nothing else to do. Move to next activity!
        item.status = 'completed';
      } else if (item.type === 'MiniLessonReference' || item.type === 'MiniLessonEmbedded') {
        this.lessonActive = true;
      } else if (item.type === 'UploadTask') {
        this.uploadActive = true;
      } else {
        console.error(`Item type ${item.type} not supported`);
      }
    },
    lessonCompleted() {
      this.lessonActive = false;
      if (this.currentStep) this.currentStep.status = 'completed';
    },
    uploadComplete() {
      this.uploadActive = false;
      if (this.currentStep) this.currentStep.status = 'completed';
    },
    isStageCompleted(stage: TrackingWorkflowStage) {
      return stage.steps.reduce((wasTrue: boolean, thisStep: TrackingWorkflowStep) => wasTrue && thisStep.status === 'completed', true);
    },
  },
});
</script>

<style lang="scss">

</style>
