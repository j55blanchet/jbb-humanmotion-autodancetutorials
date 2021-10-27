<template>
  <div
    class="box m-4"
    :class="{
      'is-clickable': stepInfo.isClickable,
      'hover-expand': stepInfo.isClickable,
      'has-text-grey': !stepInfo.isClickable,
      'has-background-grey-lighter': !stepInfo.isClickable,
      'has-background-white-ter':
        stepInfo.isClickable && stepInfo.isNextStep,
      'has-border-success': stepInfo.step.status === 'completed',
      'has-border-info': stepInfo.isNextStep,
      'has-border-grey':
        stepInfo.isClickable &&
        !stepInfo.isNextStep &&
        stepInfo.step.status !== 'completed',
    }"
    @click="stepInfo.isClickable && $emit('card-selected', stepInfo.step)"
  >
    <article class="level">
      <div class="level-left">
        <div class="level-item">
          <p class="image is-48x48" v-if="stepInfo.dbEntry?.thumbnailSrc">
            <img
              class="is-100percent is-contain"
              :src="stepInfo.dbEntry?.thumbnailSrc"
              :alt="stepInfo.step.title"
            />
          </p>
          <p class="icon is-large" v-else>
            <i
              class="fas fa-2x fa-align-center"
              v-if="stepInfo.step.type === 'InstructionOnly'"
            ></i>
            <i
              class="fas fa-2x fa-images"
              v-if="
                stepInfo.step.type === 'MiniLessonEmbedded' ||
                stepInfo.step.type === 'MiniLessonnReference'
              "
            ></i>
            <i
              class="fas fa-2x fa-camera"
              v-if="stepInfo.step.type === 'UploadTask'"
            ></i>
          </p>
        </div>
        <div class="level-item">
          <div>
            <p v-text="stepInfo.step.title"></p>
            <p v-if="stepInfo.waitingForTimeExpiration" class="is-size-7">
              &nbsp;in {{ stageSecondsRemainingString }}
            </p>
            <p v-if="stepInfo.isClickable" class="is-size-7">
              <span v-if="stepInfo.isComplete">Click to repeat</span>
              <span v-if="stepInfo.step === nextStepInStage">Up Next</span>
            </p>
          </div>
        </div>
      </div>
      <div class="level-right">
        <div class="level-item">
          <span class="icon is-large">
            <i
              class="far fa-check-circle has-text-success"
              v-if="stepInfo.step.status === 'completed'"
            ></i>
            <i
              class="far fa-play-circle"
              v-if="stepInfo.step === nextStepInStage"
            ></i>
            <i
              class="far fa-circle"
              v-if="
                stepInfo.step !== nextStepInStage &&
                stepInfo.step.status === 'notstarted'
              "
            ></i>
          </span>
        </div>
      </div>
    </article>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import { WorkflowStep } from '@/model/Workflow';
import { DatabaseEntry } from '@/services/MotionDatabase';

export interface WorkflowStepCardInfo {
  step: WorkflowStep;
  isComplete: boolean;
  dbEntry: DatabaseEntry | null;
  isExpired: boolean;
  isClickable: boolean;
  isValidAfterExpiredTask: boolean;
  isNextStep: boolean;
  waitingForTimeExpiration: boolean;
  stageIndex: number;
  stepIndex: number;
}

export default defineComponent({
  name: 'WorkflowStepCard',
  props: {
    stepInfo: {
      type: Object as () => WorkflowStepCardInfo,
      required: true,
    },
    stageSecondsRemainingString: {
      type: String,
      required: true,
    },
    nextStepInStage: {
      type: Object,
      default: null,
    },
  },
  emits: ['card-selected'],
});
</script>

<style>
</style>
