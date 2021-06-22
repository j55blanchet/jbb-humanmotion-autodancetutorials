<template>
  <section class="section create-workflow-screen" :class="{
      'is-clipped': editLessonActive,
    }" :style="{
      'max-height:100vh': editLessonActive,
    }">
    <div class="hero is-primary block">
      <div class="hero-body">
        <div class="container">
          <p class="title">
            Workflow Creation
          </p>
          <p class="subtitle">
            <span v-if="activeWorkflow">{{activeWorkflow.title}}</span>
            <span v-else>Select a starting point...</span>
          </p>
        </div>
      </div>
    </div>

    <div class="container block">
      <div class="buttons is-centered">
        <button class="button" :class="{
          'is-success': !isDirty && activeWorkflow,
        }"
        @click="goBack()">&lt; Back</button>
        <button v-if="activeWorkflow && workflowInDatabase" class="button is-danger" @click="deleteWorkflow">
          Delete
        </button>
        <button v-if="activeWorkflow" class="button" @click="exportWorkflow">Export</button>
        <button v-if="activeWorkflow" class="button"
                :class="{
                  'is-primary': isDirty
                }"
                :disabled="!isDirty"
                @click="saveWorkflow">
          <span v-if="workflowInDatabase">Update</span>
          <span v-else>Save</span>
        </button>
      </div>
    </div>

    <div class="container block has-text-centered" v-if="!activeWorkflow">
      <div class="card block center-block has-text-left is-inline-block">
          <!-- <div class="card-header">
            <h4 class="card-header-title">Pick a template:</h4>
          </div> -->
          <div class="card-content menu">
            <ul class="menu-list">
              <li>
                <a @click="selectingWorkflowIndex = -1"
                  :class="{'is-active': selectingWorkflowIndex === -1}">(start from scratch)</a>
              </li>
              <li v-for="(workflow, i) in availableWorkflows" :key="workflow.id">
                <a @click="selectingWorkflowIndex = i" :class="{'is-active': selectingWorkflowIndex === i}">
                  <strong>#{{i+1}}</strong>&nbsp;{{workflow.title}}
                </a>
              </li>
            </ul>
          </div>
          <div class="card-footer" v-if="canEditWorkflow">
            <a class="card-footer-item" @click="canEditWorkflow && startCreation(false)">Edit</a>
          </div><div class="card-footer">
            <a class="card-footer-item" @click="startCreation(true)">
              <span v-if="selectingWorkflowIndex === -1">Start New</span>
              <span v-else>Use as Template</span>
            </a>
          </div>
        </div>
    </div>
    <div class="block columns" v-else>

      <div class="column">
        <div class="box">
          <p class="title is-5">Workflow</p>

          <div class="field is-horizontal">
            <div class="field-label is-normal">
              <label class="label">ID</label>
            </div>
            <div class="field-body">
              <div class="field">
                <div class="control">
                  <input class="input" disabled type="text" :value="activeWorkflow.id">
                </div>
              </div>
            </div>
          </div>

          <div class="field is-horizontal">
            <div class="field-label is-normal">
              <label class="label">Title</label>
            </div>
            <div class="field-body">
              <div class="field">
                <div class="control">
                  <input class="input" type="text" v-model="activeWorkflow.title">
                </div>
              </div>
            </div>
          </div>

          <div class="field is-horizontal">
            <div class="field-label">
              <label class="label">Stages</label>
            </div>
            <div class="field-body">
              <div class="field">
                <div class="control">
                  <ul class="menu-list">
                    <li v-for="(stage, i) in activeWorkflow.stages" :key="i">
                      <a :class="{'is-active': selectedStageIndex === i}" @click="selectStage(i)"><strong>{{i+1}}&nbsp;</strong>&nbsp;{{stage.title}}</a>
                    </li>
                    <li><a @click="addStage()">&plus; Add Stage</a></li>
                    <li v-if="activeWorkflow.stages.length === 0">No Stages</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="column" v-if="activeStage">
        <div class="box">
          <div class="title is-5">Stage #{{selectedStageIndex + 1}}: <code>{{activeStage.title}}</code></div>

          <div class="field is-horizontal">
            <div class="field-label is-normal">
              <label class="label">Order</label>
            </div>
            <div class="field-body">
              <div class="field has-addons">
                <div class="control">
                  <button class="button" :disabled="!canReorderStage(-1)" @click="reorderStage(-1)">
                    <div class="icon"><i class="fas fa-chevron-down"></i></div>
                  </button>
                </div>
                <div class="control is-expanded">
                  <input class="input" type="text" disabled :value="selectedStageIndex + 1">
                </div>
                <div class="control">
                  <button class="button" :disabled="!canReorderStage(1)" @click="reorderStage(1)">
                    <div class="icon"><i class="fas fa-chevron-up"></i></div>
                  </button>
                </div>
              </div>
            </div>
          </div>

          <div class="field is-horizontal">
            <div class="field-label is-normal">
              <label class="label">Title</label>
            </div>
            <div class="field-body">
              <div class="field">
                <div class="control">
                  <input class="input" type="text" v-model="activeStage.title">
                </div>
              </div>
            </div>
          </div>

          <div class="field is-horizontal">
            <div class="field-label">
              <label class="label">Steps</label>
            </div>
            <div class="field-body">
              <div class="field">
                <div class="control">
                  <ul class="menu-list">
                    <li v-for="(step, i) in activeStage.steps" :key="i">
                      <a :class="{'is-active': selectedStepIndex === i}" @click="selectStep(i)"><strong>{{i+1}}&nbsp;</strong>&nbsp;{{step.title}}</a>
                    </li>
                    <li><a @click="addStep()">&plus; Add Step</a></li>
                    <li v-if="activeStage.steps.length === 0">No Steps</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
          <hr>
          <div class="buttons is-right">
            <button class="button is-danger is-outlined" @click="deleteStage">Delete</button>
          </div>
        </div>
      </div>

      <div class="column" v-if="activeStep">
        <div class="box">
          <div class="title is-5">Step #{{selectedStepIndex + 1}}: <code>{{activeStep.title}}</code></div>

          <div class="field is-horizontal">
            <div class="field-label is-normal">
              <label class="label">Order</label>
            </div>
            <div class="field-body">
              <div class="field has-addons">
                <div class="control">
                  <button class="button" :disabled="!canReorderStep(-1)" @click="reorderStep(-1)">
                    <div class="icon"><i class="fas fa-chevron-down"></i></div>
                  </button>
                </div>
                <div class="control is-expanded">
                  <input class="input" type="text" disabled :value="selectedStepIndex + 1">
                </div>
                <div class="control">
                  <button class="button" :disabled="!canReorderStep(1)" @click="reorderStep(1)">
                    <div class="icon"><i class="fas fa-chevron-up"></i></div>
                  </button>
                </div>
              </div>
            </div>
          </div>

          <div class="field is-horizontal">
            <div class="field-label is-normal">
              <label class="label">Title</label>
            </div>
            <div class="field-body">
              <div class="field">
                <div class="control">
                  <input class="input" type="text" v-model="activeStep.title">
                </div>
              </div>
            </div>
          </div>

          <div class="field is-horizontal">
            <div class="field-label">
              <label class="label">Type</label>
            </div>
            <div class="field-body">
              <div class="field">
                <div class="control">
                  <div class="select">
                    <select v-model="activeStep.type">
                      <option :value="'InstructionOnly'">Instruction</option>
                      <option :value="'VideoLessonReference'">Mini Lesson (Reference)</option>
                      <option :value="'VideoLessonEmbedded'">Mini Lesson (Embedded)</option>
                      <option :value="'UploadTask'">Video Upload</option>
                    </select>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <hr>

          <div v-if="isInstructionStep" class="block">
              <div class="field is-horizontal">
              <div class="field-label is-normal">
                <label class="label">Heading</label>
              </div>
              <div class="field-body">
                <div class="field">
                  <div class="control">
                    <input class="input" type="text" v-model="activeStep.instructions.heading">
                  </div>
                </div>
              </div>
            </div>
            <div class="field is-horizontal">
              <div class="field-label is-normal">
                <label class="label">Text</label>
              </div>
              <div class="field-body">
                <div class="field">
                  <div class="control">
                    <textarea class="textarea" v-model="activeStep.instructions.text"></textarea>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div v-if="isLessonEmbeddedStep" class="block">
            <div v-if="activeStep.videoLessonEmbedded" class="card">
              <header class="card-header">
                <p class="card-header-title">{{activeStep.videoLessonEmbedded.header.lessonTitle}}</p>
              </header>
              <div class="card-content">
                <div class="content" v-if="activeStepLesson.activities">
                  <ol v-if="activeStepLesson.activities.length <= 6">
                    <li v-for="(activity, i) in activeStepLesson.activities" :key="i">
                      {{activity.title}}
                    </li>
                  </ol>
                  <ol v-else>
                      <li v-for="(activity, i) in activeStepLesson.activities.slice(0, 3)" :key="i">{{activity.title}}</li>
                      <li style="list-style:none;">&hellip;</li>
                      <li v-for="(activity, i) in activeStepLesson.activities.slice(-3)" :key="i" :value="activeStepLesson.activities.length - 2 + i">{{activity.title}}</li>
                  </ol>
                </div>
              </div>
              <div class="card-footer">
                <a class="card-footer-item is-danger" @click="removeEmbeddedLesson">Remove</a>
                <a class="card-footer-item" @click="editWorkflowStepLesson">Edit</a>
              </div>
            </div>
            <div v-else class="has-text-centered">
              <p>No Embedded Lesson</p>

              <div class="field has-addons">
                <div class="control is-expanded">
                  <div class="select is-fullwidth">
                    <select class="select" v-model="newEmbeddedLessonClipName">
                      <option disabled value="">Select a clip</option>
                      <option v-for="clipName in availableClips" :key="clipName">{{clipName}}</option>
                    </select>
                  </div>
                </div>
                <div class="control">
                  <button class="button is-primary" :disabled="!canCreateEmbeddedLesson" @click="startCreateEmbeddedLesson">Create</button>
                </div>
              </div>
            </div>
          </div>

          <div v-if="isLessonReferenceStep" class="block">
            <div class="field is-horizontal">
              <div class="field-label">
                <label class="label">Clip</label>
              </div>
              <div class="field-body">
                <div class="field">
                  <div class="control">
                    <div class="select" v-if="activeStep.videoLessonReference">
                      <select v-model="activeStep.videoLessonReference.clipName">
                        <option disabled value="">Select a clip</option>
                        <option v-for="clipName in availableClips" :key="clipName">{{clipName}}</option>
                      </select>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div class="field is-horizontal">
              <div class="field-label">
                <label class="label">Lesson</label>
              </div>
              <div class="field-body">
                <div class="field">
                  <div class="control">
                    <div class="select">
                      <select v-model="activeStep.videoLessonReference.lessonId">
                        <option value="">&plus; Create New</option>
                        <option disabled>──────────</option>
                        <option v-for="lesson in availableReferenceLessons" :key="lesson._id" :value="lesson._id">{{lesson.header.lessonTitle}}</option>
                      </select>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <hr>
            <div v-if="activeStepLesson" class="card">
              <header class="card-header">
                <p class="card-header-title">{{activeStepLesson.header.lessonTitle}}</p>
              </header>
              <div class="card-content">
                <div class="content">
                  <ol v-if="activeStepLesson.activities.length <= 6">
                    <li v-for="(activity, i) in activeStepLesson.activities" :key="i">
                      {{activity.title}}
                    </li>
                  </ol>
                  <ol v-else>
                      <li v-for="(activity, i) in activeStepLesson.activities.slice(0, 3)" :key="i">{{activity.title}}</li>
                      <li style="list-style:none;">&hellip;</li>
                      <li v-for="(activity, i) in activeStepLesson.activities.slice(-3)" :key="i" :value="activeStepLesson.activities.length - 2 + i">{{activity.title}}</li>
                  </ol>
                </div>
              </div>
              <div class="card-footer">
                <a v-if="canEditActiveStepLessonReference" class="card-footer-item" @click="editWorkflowStepLesson">Edit Referenced Lesson</a>
                <p v-else class="card-footer-item">Unable to edit a built-in lesson</p>
              </div>
            </div>
            <div v-else class="buttons is-centered">
              <button class="button is-outlined is-primary" @click="createReferencedLesson"><span class="icon is-small"><i class="fa fa-plus"></i></span><span>Create Referenced Lesson</span></button>
            </div>
          </div>

          <div v-if="isVideoUploadStep" class="block"></div>

          <hr>

          <div class="buttons is-right">
            <button class="button is-danger is-outlined" @click="deleteStep">Delete</button>
          </div>
        </div>
      </div>

      <div class="column">
        <div class="box">
          <div class="title is-5">Demo</div>
        </div>
        <WorkflowMenu :showHeader="true" :showBackButton="false"/>
      </div>
    </div>

    <div v-bind:class="{ 'is-active': editLessonActive }" class="modal">
      <div class="modal-background"></div>
      <div class="modal-content" style="width: 96%; height: 100vh;">
        <div class="box">
          <CreateLessonScreen v-if="editLessonActive"
            :motion="embeddedLessonMotion"
            :lessonToEdit="activeStepLesson"
            @back-selected="editLessonActive = false"
            @lesson-saved="updateWorkflowStepLesson"
            :saveToDatabase="isLessonReferenceStep"
            :showBackButton="false"
            :showCloseButton="true"
            :showExportButton="isLessonReferenceStep"
          />
        </div>
        <!-- <UploadCard
          v-if="uploadUIActive"
          @cancelled="uploadUIActive = false"
          :uploadAccept="'*.json'"
          :onFilesSelected="uploadFiles"
          :savingText="'Loading lessons...'"
          :successText="'Lessons loaded successfully'"
        /> -->
      </div>
    </div>
  </section>
</template>

<script lang="ts">

import {
  CreateBlankWorkflow, GetVideoEntryForWorkflowStep, Instructions, Workflow, WorkflowStage, WorkflowStep,
} from '@/model/Workflow';
import Utils from '@/services/Utils';
import workflowManager, { WorkflowManager } from '@/services/WorkflowManager';
import WorkflowMenu from '@/components/screens/WorkflowMenu.vue';
import {
  computed, defineComponent, nextTick, ref, watch, watchEffect,
} from 'vue';
import motionDb, { createBlankLesson } from '@/services/MotionDatabase';
import VideoLesson from '@/model/VideoLesson';
import CreateLessonScreen from '@/components/screens/CreateLessonScreen.vue';

export default defineComponent({
  name: 'CreateWorkflowScreen',
  emits: ['back-selected', 'workflow-created'],
  components: {
    WorkflowMenu,
    CreateLessonScreen,
  },
  setup() {

    const isDirty = ref(false);

    const activeWorkflow = ref(null as null | Workflow);
    const selectingWorkflowIndex = ref(-1);
    const canEditWorkflow = computed(() => {
      const workflow = workflowManager.allWorkflows.value[selectingWorkflowIndex.value];
      return workflow && workflowManager.isCustomWorkflow(workflow.id);
    });
    const workflowInDatabase = computed(() => activeWorkflow.value?.id && WorkflowManager.hasSavedCustomLesson(activeWorkflow.value.id));
    const selectedStageIndex = ref(-1);
    const activeStage = computed(() => activeWorkflow.value?.stages[selectedStageIndex.value] ?? null);
    const selectedStepIndex = ref(-1);
    const activeStep = computed(() => activeStage.value?.steps[selectedStepIndex.value] ?? null);
    const isVideoUploadStep = computed(() => activeStep.value?.type === 'UploadTask');
    const isLessonReferenceStep = computed(() => activeStep.value?.type === 'VideoLessonReference');
    const isLessonEmbeddedStep = computed(() => activeStep.value?.type === 'VideoLessonEmbedded');
    const isInstructionStep = computed(() => activeStep.value?.type === 'InstructionOnly');
    const availableReferenceLessons = computed(() => {
      if (!activeStep.value) return [] as VideoLesson[];
      if (!activeStep.value.videoLessonReference?.clipName) return [] as VideoLesson[];
      return motionDb.lessonsByVideo.get(activeStep.value.videoLessonReference.clipName) ?? [];
    });
    const embeddedLessonMotion = computed(() => (activeStep.value ? GetVideoEntryForWorkflowStep(motionDb, activeStep.value) : null));
    const activeStepLesson = computed(() => {
      if (!activeStep.value) return null;
      if (isLessonReferenceStep.value && activeStep.value.videoLessonReference?.lessonId) return motionDb.lessonsById.get(activeStep.value.videoLessonReference.lessonId) ?? null;
      if (isLessonEmbeddedStep.value) return activeStep.value.videoLessonEmbedded ?? null;
      return null;
    });
    const canEditActiveStepLessonReference = computed(() => activeStepLesson.value?.source === 'custom');
    const newEmbeddedLessonClipName = ref('');
    const newEmbeddedLessonMotion = computed(() => motionDb.motionsMap.get(newEmbeddedLessonClipName.value) ?? null);
    const canCreateEmbeddedLesson = computed(() => newEmbeddedLessonMotion.value !== null);
    const editLessonActive = ref(false);

    watchEffect(() => {
      if (activeWorkflow.value) {
        workflowManager.setActiveFlow(activeWorkflow.value.id);
        workflowManager.completeActivitesPriorToStageAndStep(selectedStageIndex.value, selectedStepIndex.value);
        // TODO: improve logic to keep status of intra-stage workflow steps.
      }
    });

    watchEffect(() => {
      if (!activeStep.value) return;
      if (isInstructionStep.value) {
        activeStep.value.instructions = activeStep.value.instructions ?? {
          heading: 'Instructions Heading',
          text: '',
        } as Instructions;
      } else if (isLessonReferenceStep.value) {
        activeStep.value.videoLessonReference = activeStep.value.videoLessonReference ?? {} as any;
        //  ?? {

        // };
      } else if (isLessonEmbeddedStep.value) {
        // activeStep.value.videoLessonEmbedded = activeStep.value.videoLessonEmbedded;
        //  ?? {

        // };
      } else if (isVideoUploadStep.value) {
        activeStep.value.upload = activeStep.value.upload ?? {
          identifier: activeStep.value.title,
          prompt: 'Upload your video here',
        };
      }
    });

    return {
      selectingWorkflowIndex,
      activeWorkflow,
      canEditWorkflow,
      workflowInDatabase,
      availableWorkflows: workflowManager.allWorkflows,
      selectedStageIndex,
      activeStage,

      selectedStepIndex,
      activeStep,
      isVideoUploadStep,
      isLessonReferenceStep,
      isLessonEmbeddedStep,
      isInstructionStep,
      availableClips: motionDb.motionNames,
      availableReferenceLessons,
      newEmbeddedLessonClipName,
      newEmbeddedLessonMotion,
      embeddedLessonMotion,
      canCreateEmbeddedLesson,
      editLessonActive,
      activeStepLesson,
      canEditActiveStepLessonReference,

      isDirty,
    };
  },
  data() {
    return {
    };
  },
  watch: {
    activeWorkflow: {
      handler(newVal) {
        this.isDirty = !!newVal;
      },
      deep: true,
    },
  },
  computed: {
  },
  methods: {
    goBack(skipPrompt?: boolean) {
      if (!this.activeWorkflow) {
        this.$emit('back-selected');
        return;
      }

      if (skipPrompt || !this.isDirty) {
        this.activeWorkflow = null;
        return;
      }

      // eslint-disable-next-line no-alert
      if (window.confirm('Go back without saving changes?')) {
        workflowManager.reloadCustomWorkflow(this.activeWorkflow.id);
        this.activeWorkflow = null;
      }
    },
    deleteWorkflow() {
      if (!this.activeWorkflow) return;

      // eslint-disable-next-line no-alert
      if (!window.confirm('Are you sure you want to delete this lesson?')) {
        return;
      }

      workflowManager.deleteCustomWorkflow(this.activeWorkflow.id);
      this.goBack(true);
    },
    exportWorkflow() {
      if (!this.activeWorkflow) return;
      Utils.PromptDownloadFile(`${this.activeWorkflow.title}.workflow.json`, JSON.stringify(this.activeWorkflow));
    },
    saveWorkflow() {
      if (!this.activeWorkflow) return;
      workflowManager.upsertCustomWorkflow(this.activeWorkflow);
      this.isDirty = false;
    },
    startCreation(asTemplate: boolean) {
      const existingWorkflow = this.availableWorkflows[this.selectingWorkflowIndex];
      if (existingWorkflow && asTemplate) {
        this.activeWorkflow = Utils.deepCopy(existingWorkflow);
        this.activeWorkflow.id = Utils.uuidv4();
      } else if (existingWorkflow && !asTemplate) {
        this.activeWorkflow = existingWorkflow;
        nextTick(() => {
          this.isDirty = false;
        });

      } else {
        this.activeWorkflow = CreateBlankWorkflow();
      }

      workflowManager.addSessionWorkflow(this.activeWorkflow);
      workflowManager.setActiveFlow(this.activeWorkflow.id);
    },
    selectStage(stageIndex: number) {

      // Clear selection if this stage was already selected
      if (stageIndex === this.selectedStageIndex) {
        this.selectedStageIndex = -1;
        this.selectedStepIndex = -1;
        return;
      }

      this.selectedStageIndex = stageIndex;
      this.selectedStepIndex = -1;
      workflowManager.completeActivitesPriorToStageAndStep(stageIndex, this.selectedStepIndex);
    },
    canReorderStage(increment: number) {
      const workflow = this.activeWorkflow;
      if (!workflow) return false;
      const { stages } = workflow;
      const curStage = stages[this.selectedStageIndex];
      const swapStage = stages[this.selectedStageIndex + increment];
      return (curStage !== undefined) && (swapStage !== undefined);
    },
    reorderStage(increment: number) {
      const workflow = this.activeWorkflow;
      if (!workflow) return;
      const { stages } = workflow;
      const swapIndex = this.selectedStageIndex + increment;
      const curSelected = stages[this.selectedStageIndex];
      const toSwap = stages[swapIndex];
      if ((curSelected === undefined) || (toSwap === undefined)) {
        console.warn(`Unable to swap stages ${this.selectedStageIndex} and ${swapIndex}`);
        return;
      }
      stages[this.selectedStageIndex] = toSwap;
      stages[swapIndex] = curSelected;
      this.selectedStageIndex = swapIndex;
      workflow.stages = stages;
    },
    addStage() {
      const workflow = this.activeWorkflow;
      if (!workflow) return;

      workflow.stages.push({
        title: `New-Stage-${workflow.stages.length + 1}`,
        steps: [],
      } as WorkflowStage);
      this.selectStage(workflow.stages.length - 1);
    },
    deleteStage() {
      const workflow = this.activeWorkflow;
      if (!workflow) return;
      // eslint-disable-next-line no-alert
      if (!window.confirm(`Are you sure you want to delete Stage #${this.selectedStageIndex + 1}?`)) return;

      const { stages } = workflow;
      stages.splice(this.selectedStageIndex, 1);
      workflow.stages = stages;
      this.selectedStageIndex = Math.min(this.selectedStageIndex, stages.length - 1);
    },
    selectStep(stepIndex: number) {

      // Clear selectedStep if already selected
      if (this.selectedStepIndex === stepIndex) {
        this.selectedStepIndex = -1;
        return;
      }
      this.selectedStepIndex = stepIndex;

      workflowManager.completeActivitesPriorToStageAndStep(this.selectedStageIndex, this.selectedStepIndex);
    },
    canReorderStep(increment: number) {
      const workflow = this.activeWorkflow;
      if (!workflow) return false;
      const steps = workflow.stages[this.selectedStageIndex]?.steps;
      if (!steps) return false;
      const curStep = steps[this.selectedStepIndex];
      const swapStep = steps[this.selectedStepIndex + increment];
      return (curStep !== undefined) && (swapStep !== undefined);
    },
    reorderStep(increment: number) {
      const workflow = this.activeWorkflow;
      if (!workflow) return;
      const steps = workflow.stages[this.selectedStageIndex]?.steps;
      if (!steps) return;
      const swapIndex = this.selectedStepIndex + increment;
      const curStep = steps[this.selectedStepIndex];
      const swapStep = steps[swapIndex];
      if ((curStep === undefined) || (swapStep === undefined)) {
        console.warn(`Unable to swap steps ${this.selectedStepIndex} and ${swapIndex}`);
        return;
      }
      steps[this.selectedStageIndex] = swapStep;
      steps[swapIndex] = curStep;
      this.selectedStepIndex = swapIndex;
      workflow.stages[this.selectedStageIndex].steps = steps;
    },
    addStep() {
      const stage = this.activeStage;
      if (!stage) return;

      stage.steps.push({
        title: `New-Step-${stage.steps.length + 1}`,
        type: 'InstructionOnly',
      } as WorkflowStep);
      this.selectStep(stage.steps.length - 1);
    },
    deleteStep() {
      const stage = this.activeStage;
      if (!stage) return;
      // eslint-disable-next-line no-alert
      if (!window.confirm(`Are you sure you want to delete Step #${this.selectedStepIndex + 1}?`)) return;

      const { steps } = stage;
      steps.splice(this.selectedStepIndex, 1);
      stage.steps = steps;
      this.selectedStepIndex = Math.min(this.selectedStepIndex, steps.length - 1);
    },
    updateWorkflowStepLesson(lesson: VideoLesson) {
      if (!this.activeStep) return;
      if (this.isLessonEmbeddedStep) {
        this.activeStep.videoLessonEmbedded = lesson;
        console.log('Updated embedded lesson', lesson.header.lessonTitle);
      }
      if (this.isLessonReferenceStep && this.activeStep.videoLessonReference) {
        this.activeStep.videoLessonReference.lessonId = lesson._id;
        console.log('Updated reference lesson', lesson);
      }
    },
    startCreateEmbeddedLesson() {
      if (!this.activeStep) return;
      if (!this.newEmbeddedLessonMotion) return;
      this.activeStep.videoLessonEmbedded = createBlankLesson(this.newEmbeddedLessonMotion);
      this.activeStep.videoLessonEmbedded.header.lessonTitle = this.activeStep.title;
      this.editLessonActive = true;
    },
    createReferencedLesson() {
      if (!this.isLessonReferenceStep) return;
      if (this.activeStep?.videoLessonReference?.lessonId === '') {
        this.editLessonActive = true;
      }
    },
    editWorkflowStepLesson() {
      if (!this.activeStepLesson) return;
      this.editLessonActive = true;
    },
    removeEmbeddedLesson() {
      if (!this.activeStep?.videoLessonEmbedded) return;
      // eslint-disable-next-line no-alert
      if (window.confirm(`Are you sure you want to delete the embedded lesson ${this.activeStep.videoLessonEmbedded.header.lessonTitle}?`)) {
        this.activeStep.videoLessonEmbedded = undefined;
      }
    },
  },
});
</script>

<style lang="sass">

</style>
