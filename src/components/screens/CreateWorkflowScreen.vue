<template>
  <section class="section create-workflow-screen">
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
      <button class="button" :class="{
        'is-danger': isDirty,
        'is-inverted': isDirty,
      }"
      @click="goBack()">&lt; Back</button>
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

          <div class="field is-grouped is-grouped-right">
            <div class="control" v-if="workflowInDatabase">
              <button class="button is-danger is-outlined" @click="deleteWorkflow">
                Delete
              </button>
            </div>
            <div class="control">
              <button class="button" @click="exportWorkflow">Export</button>
            </div>
            <div class="control">
              <button class="button is-primary"
                :disabled="!isDirty"
                @click="saveWorkflow">
                <span v-if="workflowInDatabase">Update</span>
                <span v-else>Save</span>
              </button>
            </div>
          </div>

        </div>
      </div>

      <div class="column" v-if="activeStage">
        <div class="box">
          <div class="title is-5">Stage #{{selectedStageIndex + 1}}: &quot;{{activeStage.title}}&quot;</div>

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
        </div>
      </div>

      <div class="column" v-if="activeStep">
        <div class="box">
          <div class="title is-5">Step #{{selectedStepIndex + 1}}: &quot;{{activeStep.title}}&quot;</div>

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
                    <option :value="'VideoLesson'">Mini Lesson</option>
                    <option :value="'UploadTask'">Video Upload</option>
                  </select>
                </div>
              </div>
            </div>
          </div>
        </div>

        <hr>
        <div v-if="isInstructionStep">
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
        <div v-if="isLessonStep"></div>
        <div v-if="isVideoUploadStep"></div>
        </div>
      </div>

      <div class="column">
        <div class="box">
          <div class="title is-5">Demo</div>
        </div>
        <WorkflowMenu :showHeader="true" :showBackButton="false"/>
      </div>
    </div>
  </section>
</template>

<script lang="ts">

import {
  CreateBlankWorkflow, Instructions, Workflow, WorkflowStage, WorkflowStep,
} from '@/model/Workflow';
import Utils from '@/services/Utils';
import workflowManager, { WorkflowManager } from '@/services/WorkflowManager';
import WorkflowMenu from '@/components/screens/WorkflowMenu.vue';
import {
  computed, defineComponent, nextTick, ref, watch, watchEffect,
} from 'vue';

export default defineComponent({
  name: 'CreateWorkflowScreen',
  emits: ['back-selected', 'workflow-created'],
  components: {
    WorkflowMenu,
  },
  setup() {

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
    const isLessonStep = computed(() => activeStep.value?.type === 'VideoLesson');
    const isInstructionStep = computed(() => activeStep.value?.type === 'InstructionOnly');
    const isDirty = ref(false);

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
        activeStep.value.activity = undefined;
        activeStep.value.upload = undefined;
        activeStep.value.embeddedLesson = undefined;
      } else if (isLessonStep.value) {

      } else if (isInstructionStep.value) {

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
      isLessonStep,
      isInstructionStep,

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
      this.selectedStageIndex = stageIndex;
      this.selectedStepIndex = -1;
      workflowManager.completeActivitesPriorToStageAndStep(stageIndex, this.selectedStepIndex);
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
    selectStep(stepIndex: number) {
      this.selectedStepIndex = stepIndex;
      workflowManager.completeActivitesPriorToStageAndStep(this.selectedStageIndex, this.selectedStepIndex);
    },
    addStep() {
      const stage = this.activeStage;
      if (!stage) return;

      stage.steps.push({
        title: `New-Step-${stage.steps.length + 1}`,
        type: 'InstructionOnly',
      } as WorkflowStep);
    },
  },
});
</script>

<style lang="sass">

</style>
