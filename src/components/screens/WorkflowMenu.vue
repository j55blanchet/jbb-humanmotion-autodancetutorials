<template>
  <section class="section workflow-menu">

    <div class="hero is-primary block">
      <div class="hero-body">
        <div class="container">
          <p class="title">
            {{workflow?.title}}
          </p>
        </div>
      </div>
    </div>

    <div class="container block">
      <button class="button" @click="$emit('back-selected')">&lt; Back</button>
    </div>

    <div class="block" v-for="(stage, i) in workflow?.stages ?? []" :key="i">
      <p class="subtitle has-text-centered">{{stage.title}}</p>

      <div class="grid-menu container block">
        <div class="box m-4"
            :class="{
                  'is-clickable': isClickable(stepInfo.step),
                  'hover-expand': isClickable(stepInfo.step),
                  'has-text-grey': !isClickable(stepInfo.step),
                  'has-background-grey-lighter': !isClickable(stepInfo.step),
                  'has-border-success': stepInfo.step.status === 'completed',
                  'has-border-grey': stepInfo.step === nextStep
                }"
            @click="startWorkflowStep(stepInfo.step)"
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
                  <i class="fas fa-2x photo-video" v-if="stepInfo.step.type === 'VideoLesson'"></i>
                  <i class="fas fa-2x fa-camera" v-if="stepInfo.step.type === 'UploadTask'"></i>
                </p>
              </div>
              <div class="level-item">
                <span v-text="stepInfo.step.title"></span>
              </div>
            </div>
            <div class="level-right">
              <div class="level-item">
                <span class="icon is-large">
                  <i class="far fa-check-circle has-text-success" v-if="stepInfo.step.status==='completed'"></i>
                  <i class="far fa-play-circle" v-if="stepInfo.step===nextStep"></i>
                  <i class="far fa-circle" v-if="stepInfo.step !== nextStep && stepInfo.step.status==='notstarted'"></i>
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
            <p>{{currentStep?.instructions?.body}}</p>
            <div class="has-text-right">
              <button class="button" @click="instructionsFinished">Continue</button>
            </div>
          </div>
        </div>
      </div>

        <div v-bind:class="{ 'is-active': lessonActive }" class="modal">
        <div class="modal-background"></div>
        <div class="container">
          <div class="box" style="max-width: 100%; max-height: 100%;">
            <VideoLessonPlayer
              v-if="lessonActive"
              :videoEntry="currentVideoEntry"
              :videoLesson="currentLesson"
              @lesson-completed="lessonCompleted"
              :maxVideoHeight="'80vh'"
              :enableCompleteLesson="true"/>
          </div>
        </div>
        <button class="modal-close is-large" aria-label="close" @click="lessonActive=false"></button>
      </div>

      <!-- <div
        class="dance-card card is-clickable hover-expand"
        v-for="dance in motionList"
        :key="dance.title"
        @mouseover="hover = dance.hovering = true"
        @mouseleave="hover = dance.hovering = false"
        @click="selectedDance = dance"
      >
        <div class="card-image">
          <figure class="image is-2by3">
            <video :src="dance.videoSrc" />
          </figure>
        </div>
        <div class="card-content">
          {{ dance.title }}
        </div>
      </div> -->
    </div>

  </section>
</template>

<script lang="ts">
import { computed, defineComponent, ref } from 'vue';
import VideoLessonPlayer from '@/components/elements/VideoLessonPlayer.vue';
import db, { DatabaseEntry } from '@/services/MotionDatabase';
import VideoLesson from '@/model/VideoLesson';
import workflowManager, { TrackingWorkflowStage, TrackingWorkflowStep } from '@/services/WorkflowManager';

export default defineComponent({
  name: 'WorkflowMenu',
  props: {
  },
  emits: [
    'back-selected',
  ],
  components: {
    VideoLessonPlayer,
  },
  computed: {
    stages() { return ((this as any).workflow?.stages ?? []) as TrackingWorkflowStage[]; },
    nextStep() {
      for (let i = 0; i < this.stages.length; i += 1) {
        const stage = (this as any).stages[i];
        for (let j = 0; j < stage.steps.length; j += 1) {
          const step = stage.steps[j];
          if (step.status !== 'completed') return step as TrackingWorkflowStep;
        }
      }
      return null;
    },
    currentVideoEntry(): DatabaseEntry | null {
      if (this.currentStep?.activity) {
        return db.motionsMap.get(this.currentStep.activity.clipName) ?? null;
      }
      return null;
    },
    currentLesson(): VideoLesson | null {
      if (this.currentStep?.activity) {
        return db.lessonsById.get(this.currentStep.activity.lessonId) ?? null;
      }
      return null;
    },
  },
  setup(props, ctx) {
    const currentStep = ref(null as null | TrackingWorkflowStep);
    const instructionsActive = ref(false);
    const lessonActive = ref(false);
    const uploadActive = ref(false);
    return {
      currentStep,
      instructionsActive,
      lessonActive,
      uploadActive,
      workflow: workflowManager.activeFlow,
    };
  },
  methods: {
    getStepInfo(stage: TrackingWorkflowStage) {

      return stage.steps.map((step) => ({
        step,
        dbEntry: db.motionsMap.get(step.activity?.clipName ?? '') ?? null,
      }));
    },
    instructionsFinished() {
      this.instructionsActive = false;
      const step = this.currentStep;
      if (!step) return;
      step.status = 'inprogress';
      this.continueWorkflowStep(step);
    },
    isClickable(step: TrackingWorkflowStep) {
      return this.nextStep === step
      || (step.type === 'InstructionOnly' && step.status === 'completed');
    },
    startWorkflowStep(item: TrackingWorkflowStep) {
      if (!this.isClickable(item)) return;
      this.currentStep = item;
      if ((item.status === 'notstarted' && item.instructions) || (item.type === 'InstructionOnly')) {
        this.instructionsActive = true;
        return;
      }
      this.continueWorkflowStep(item);
    },
    continueWorkflowStep(item: TrackingWorkflowStep) {
      if (item.type === 'InstructionOnly') {
        // Instructions only - there's nothing else to do. Move to next activity!
        item.status = 'completed';
      } else if (item.type === 'VideoLesson') {
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
  },
});
</script>

<style lang="scss">

</style>
