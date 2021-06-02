import { computed, reactive, ref } from 'vue';
import optionsManager from '@/services/OptionsManager';
import motionDB, { DatabaseEntry } from '@/services/MotionDatabase';
import VideoLesson from '@/model/VideoLesson';
import { Workflow, WorkflowStage, WorkflowStep } from '@/model/Workflow';
import workflowsJson from '@/model/workflows.json';
import eventHub, { EventNames } from './EventHub';
import utils from './Utils';

const defaultWorkflows = workflowsJson as Workflow[];

export interface TrackingWorkflowStep extends WorkflowStep {
  status: 'notstarted' | 'inprogress' | 'completed';
}

export interface TrackingWorkflowStage extends WorkflowStage {
  steps: TrackingWorkflowStep[];
}

export interface TrackingWorkflow extends Workflow {
  stages: TrackingWorkflowStage[];
}

const TestWorkflow = Object.freeze(
  {
    title: 'ExperimentTest',
    id: 'e61789dhgbuiqd6129',
    stages: [{
      title: 'Experiment Introduction',
      steps: [{
        title: 'Welcome',
        type: 'InstructionOnly',
        instructions: {
          heading: 'Test Experiment',
          body: 'This an example experiment. You\'ll be taken through '
          + 'a flow of activites and will be shown instructions '
          + 'along the way.',
        },
      }],
    }, {
      title: 'First Two Dances',
      steps: [{
        title: 'Savage Love',
        type: 'VideoLesson',
        // instructions: {},
        activity: {
          clipName: 'derulo',
          lessonId: 'cde1c09d-299a-4aed-8ad2-efa6c9d1b276',
        },
      }, {
        title: "It's a Fit",
        type: 'VideoLesson',
        // instructions: {},
        activity: {
          clipName: 'itsafit',
          lessonId: '14cac0d6-ec00-41ae-ac80-e738d5cc09a1',
        },
      }],
    }, {
      title: 'Last Two Dances',
      steps: [{
        title: 'Renegade',
        type: 'VideoLesson',
        activity: {
          clipName: 'renegade',
          lessonId: '4ecac1f9-b32c-42de-b290-d97c883437e5',
        },
      }],
    }, {
      title: 'Last Two Dances',
      steps: [{
        title: 'Unh-hunh',
        type: 'VideoLesson',
        activity: {
          clipName: 'unhhunh',
          lessonId: '580baf76-412f-41c3-9f50-54ebf01ace46',
        },
      }],
    }],
  } as Workflow,
);

class WorkflowManager {

  private workflows = reactive(new Map() as Map<string, Workflow>);

  public allWorkflows = computed(() => new Array(...this.workflows.values()))

  public activeFlow = ref(null as TrackingWorkflow | null);

  constructor() {
    this.loadWorkflows();

    const workflowId = optionsManager.workflowId.value;
    if (workflowId) {
      this.setActiveFlow(workflowId);
    }
  }

  private loadWorkflows() {
    for (let i = 0; i < defaultWorkflows.length; i += 1) {
      const workflow = defaultWorkflows[i] as Workflow;
      this.workflows.set(workflow.id, workflow);
    }
    this.workflows.set(TestWorkflow.id, TestWorkflow);
  }

  private setActiveFlow(workflowId: string) {
    const matchingWorkflow = this.workflows.get(workflowId);

    if (!matchingWorkflow) {
      console.error(`setActiveFlow: Couldn't find workflow with id ${workflowId}`);
      return;
    }

    const flow = utils.deepCopy(matchingWorkflow);
    const trackingFlow = {
      ...flow,
      stages: flow.stages.map((stage) => ({
        ...stage,
        steps: stage.steps.map((step) => ({
          ...step,
          status: 'notstarted',
        }) as TrackingWorkflowStep),
      } as TrackingWorkflowStage)),
    } as TrackingWorkflow;

    this.activeFlow.value = trackingFlow;
  }
}

const workflowManager = new WorkflowManager();
export default workflowManager;
