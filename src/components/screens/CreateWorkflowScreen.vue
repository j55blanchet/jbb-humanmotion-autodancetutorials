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
          <!-- <span v-if="workflowInDatabase">Update</span> -->
          <span>Save</span>
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
    <div class="block columns is-multiline" v-else>

      <div class="column is-narrow">
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
                    <li v-if="activeStage"><a @click="duplicateStage()"><span class="icon"><i class="far fa-copy"></i></span><span>Duplicate</span></a></li>
                    <li><a @click="addStage()"><span class="icon">&plus;</span><span>Add Stage</span></a></li>
                    <li v-if="activeWorkflow.stages.length === 0">No Stages</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="column is-narrow" v-if="activeStage">
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
                    <li v-if="activeStep"><a @click="duplicateStep()"><span class="icon"><i class="far fa-copy"></i></span><span>Duplicate</span></a></li>
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

      <div class="column is-narrow" v-if="activeStep">
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
                      <option :value="'MiniLessonReference'">Mini Lesson (Reference)</option>
                      <option :value="'MiniLessonEmbedded'">Mini Lesson (Embedded)</option>
                      <option :value="'UploadTask'">Video Upload</option>
                    </select>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="field is-grouped is-grouped-right" v-if="(activeWorkflow?.stages ?? []).length > 1">
            <div class="control">
              <div class="dropdown is-right" :class="{'is-active': isMoveStepDropdownActive}">
                <div class="dropdown-trigger">
                  <button class="button" @click="isMoveStepDropdownActive = !isMoveStepDropdownActive">
                    <span>Move to stage&hellip;</span>
                    <span class="icon is-small" v-if="!isMoveStepDropdownActive"><i class="fas fa-angle-down" aria-hidden="true"></i></span>
                    <span class="icon is-small" v-if="isMoveStepDropdownActive"><i class="fas fa-angle-up" aria-hidden="true"></i></span>
                  </button>
                </div>
                <div class="dropdown-menu">
                  <div class="box has-background-white">
                    <div class="menu">
                      <p class="menu-label">Move to stage:</p>
                      <ul class="menu-list">
                        <li v-for="(stage, stageI) in this.activeWorkflow?.stages ?? []" :key="stageI">
                          <a @click="moveStep(stageI)" :class="{'is-active': selectedStageIndex === stageI }">
                            <strong>{{stageI + 1}}</strong>&nbsp;&nbsp;{{stage.title}}
                          </a>
                        </li>
                      </ul>
                    </div>
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
            <div v-if="activeStep.miniLessonEmbedded" class="card">
              <header class="card-header">
                <p class="card-header-title">{{activeStep.miniLessonEmbedded.header.lessonTitle}}</p>
              </header>
              <div class="card-content">
                <div class="content" v-if="activeStepLesson.activities">
                  <p>Activities</p>
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
                <a class="card-footer-item has-text-danger" @click="removeEmbeddedLesson">Remove</a>
                <a class="card-footer-item" @click="convertEmbeddedLessonToReference">Make Reference</a>
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
                    <div class="select" v-if="activeStep.miniLessonReference">
                      <select v-model="activeStep.miniLessonReference.clipName">
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
                      <select v-model="activeStep.miniLessonReference.lessonId">
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
                  <p>Activities</p>
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
            :disableEditingExisting="true"
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
  computed, defineComponent, nextTick, ref, watchEffect,
} from 'vue';
import motionDb from '@/services/MotionDatabase';
import MiniLesson from '@/model/MiniLesson';
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
    const selectedStageIndex = ref(0);
    const activeStage = computed(() => activeWorkflow.value?.stages[selectedStageIndex.value] ?? null);
    const selectedStepIndex = ref(0);
    const activeStep = computed(() => activeStage.value?.steps[selectedStepIndex.value] ?? null);
    const isVideoUploadStep = computed(() => activeStep.value?.type === 'UploadTask');
    const isLessonReferenceStep = computed(() => activeStep.value?.type === 'MiniLessonReference');
    const isLessonEmbeddedStep = computed(() => activeStep.value?.type === 'MiniLessonEmbedded');
    const isInstructionStep = computed(() => activeStep.value?.type === 'InstructionOnly');
    const availableReferenceLessons = computed(() => {
      if (!activeStep.value) return [] as MiniLesson[];
      if (!activeStep.value.miniLessonReference?.clipName) return [] as MiniLesson[];
      return motionDb.lessonsByVideo.get(activeStep.value.miniLessonReference.clipName) ?? [];
    });
    const activeStepLesson = computed(() => {
      if (!activeStep.value) return null;
      if (isLessonReferenceStep.value && activeStep.value.miniLessonReference?.lessonId) return motionDb.lessonsById.get(activeStep.value.miniLessonReference.lessonId) ?? null;
      if (isLessonEmbeddedStep.value) return activeStep.value.miniLessonEmbedded ?? null;
      return null;
    });
    const canEditActiveStepLessonReference = computed(() => activeStepLesson.value?.source === 'custom');
    const newEmbeddedLessonClipName = ref('');
    const newEmbeddedLessonMotion = computed(() => motionDb.motionsMap.get(newEmbeddedLessonClipName.value) ?? null);
    const canCreateEmbeddedLesson = computed(() => newEmbeddedLessonMotion.value !== null);
    const editLessonActive = ref(false);
    const embeddedLessonMotion = computed(() => {
      if (!activeStep.value) return null;
      if (isLessonEmbeddedStep.value && activeStep.value.miniLessonEmbedded) return GetVideoEntryForWorkflowStep(motionDb, activeStep.value);
      if (isLessonEmbeddedStep.value) return newEmbeddedLessonMotion.value;
      if (isLessonReferenceStep.value) return GetVideoEntryForWorkflowStep(motionDb, activeStep.value);
      return null;
    });

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
        activeStep.value.miniLessonReference = activeStep.value.miniLessonReference ?? {} as any;
        //  ?? {

        // };
      } else if (isLessonEmbeddedStep.value) {
        // activeStep.value.miniLessonEmbedded = activeStep.value.miniLessonEmbedded;
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
      isMoveStepDropdownActive: ref(false),

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
        console.log('Workflow now dirty');
        this.isDirty = ((newVal ?? null) !== null);
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
      console.log('Saving workflow');
      workflowManager.upsertCustomWorkflow(this.activeWorkflow);
      nextTick(() => {
        this.isDirty = false;
        console.log('Workflow saved; not dirty now');
      });
      // window.setTimeout(() => {
      // }, 200);
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
    duplicateStage() {
      const workflow = this.activeWorkflow;
      if (!workflow) return;
      const { stages } = workflow;
      const curStage = stages[this.selectedStageIndex];
      if (!curStage) return;
      stages.splice(this.selectedStageIndex, 0, Utils.deepCopy(curStage));
      workflow.stages = stages;
      this.selectedStageIndex += 1;
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
    duplicateStep() {
      const workflow = this.activeWorkflow;
      if (!workflow) return;
      const curStep = this.activeWorkflow?.stages[this.selectedStageIndex]?.steps[this.selectedStepIndex];
      if (!curStep) return;
      const { steps } = workflow.stages[this.selectedStageIndex];
      steps.splice(this.selectedStepIndex, 0, Utils.deepCopy(curStep));
      workflow.stages[this.selectedStageIndex].steps = steps;
      this.selectedStepIndex += 1;
    },
    moveStep(targetStageIndex: number) {
      if (targetStageIndex === this.selectedStageIndex) return;
      const stage = this.activeStage;
      const stepToMove = this.activeStep;
      const targetPhase = this.activeWorkflow?.stages[targetStageIndex];
      if (!stage || !stepToMove || !targetPhase) return;
      const { steps } = stage;
      steps.splice(this.selectedStepIndex, 1);
      stage.steps = steps;
      targetPhase.steps.push(stepToMove);
      this.selectedStageIndex = targetStageIndex;
      this.selectedStepIndex = this.activeStage?.steps.length ?? 0;
      this.isMoveStepDropdownActive = false;
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
    updateWorkflowStepLesson(lesson: MiniLesson) {
      if (!this.activeStep) return;
      if (this.isLessonEmbeddedStep) {
        this.activeStep.miniLessonEmbedded = lesson;
        console.log('Updated embedded lesson', lesson.header.lessonTitle);
      }
      if (this.isLessonReferenceStep && this.activeStep.miniLessonReference) {
        this.activeStep.miniLessonReference.lessonId = lesson._id;
        console.log('Updated reference lesson', lesson);
      }
    },
    startCreateEmbeddedLesson() {
      if (!this.activeStep) return;
      if (!this.newEmbeddedLessonMotion) return;
      // this.activeStep.miniLessonEmbedded = createBlankLesson(this.newEmbeddedLessonMotion);
      // this.activeStep.miniLessonEmbedded.header.lessonTitle = this.activeStep.title;
      this.editLessonActive = true;
    },
    createReferencedLesson() {
      if (!this.isLessonReferenceStep) return;
      if (this.activeStep?.miniLessonReference?.lessonId === '') {
        this.editLessonActive = true;
      }
    },
    editWorkflowStepLesson() {
      if (!this.activeStepLesson) return;
      this.editLessonActive = true;
    },
    removeEmbeddedLesson() {
      if (!this.activeStep?.miniLessonEmbedded) return;
      // eslint-disable-next-line no-alert
      if (window.confirm(`Are you sure you want to delete the embedded lesson ${this.activeStep.miniLessonEmbedded.header.lessonTitle}?`)) {
        this.activeStep.miniLessonEmbedded = undefined;
      }
    },
    convertEmbeddedLessonToReference() {
      if (!this.activeStep?.miniLessonEmbedded) return;
      // eslint-disable-next-line no-alert
      if (!window.confirm('Are you sure you want to save this lesson into a new file and convert this to a reference?'
                         + '\n\nNote: be sure to save the lesson.json!')
      ) return;

      motionDb.saveCustomLesson(this.activeStep.miniLessonEmbedded);
      this.activeStep.miniLessonReference = {
        clipName: this.activeStep.miniLessonEmbedded.header.clipName,
        lessonId: this.activeStep.miniLessonEmbedded._id,
      };
      const exportLessonData = this.activeStep.miniLessonEmbedded;
      this.activeStep.type = 'MiniLessonReference';
      this.activeStep.miniLessonEmbedded = undefined;
      Utils.PromptDownloadFile(`${exportLessonData.header.lessonTitle}.lesson.json`, JSON.stringify(exportLessonData));
    },
  },
});
</script>

<style lang="sass">

</style>
