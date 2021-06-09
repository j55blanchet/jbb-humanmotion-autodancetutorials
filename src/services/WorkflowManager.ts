import { computed, reactive, ref } from 'vue';
import optionsManager from '@/services/OptionsManager';
import motionDB, { DatabaseEntry } from '@/services/MotionDatabase';
import VideoLesson from '@/model/VideoLesson';
import { Workflow, WorkflowStage, WorkflowStep } from '@/model/Workflow';
import workflowsJson from '@/model/workflows.json';
import eventHub, { EventNames } from './EventHub';
import Utils from './Utils';

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
    title: '4-Tiktoks (Example Workflow)',
    id: 'e61789dhgbuiqd6129',
    stages: [{
      title: 'Introduction',
      steps: [{
        title: 'Welcome',
        type: 'InstructionOnly',
        instructions: {
          heading: 'Test Experiment',
          paragraphs: ['This an example experiment. You\'ll be taken through '
          + 'a flow of activites and will be shown instructions '
          + 'along the way.', "First, you'll learn 4 dances", "Then, you'll be asked to upload a video of you performing the dances"],
        },
      }],
    }, {
      title: 'Learning Phase',
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
      }, {
        title: 'Renegade',
        type: 'VideoLesson',
        activity: {
          clipName: 'renegade',
          lessonId: '4ecac1f9-b32c-42de-b290-d97c883437e5',
        },
      }, {
        title: 'Unh-hunh',
        type: 'VideoLesson',
        activity: {
          clipName: 'unhhunh',
          lessonId: '580baf76-412f-41c3-9f50-54ebf01ace46',
        },
      }],
    }, {
      title: 'Feedback',
      steps: [{
        title: 'Performance',
        type: 'UploadTask',
        upload: {
          identifier: 'end-upload',
          prompt: 'Upload yourself performing all these dances in order',
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
  }

  private loadWorkflows() {
    for (let i = 0; i < defaultWorkflows.length; i += 1) {
      const workflow = defaultWorkflows[i] as Workflow;
      this.workflows.set(workflow.id, workflow);
    }
    this.workflows.set(TestWorkflow.id, TestWorkflow);
  }

  public setActiveFlow(workflowId: string) {
    const matchingWorkflow = this.workflows.get(workflowId);

    if (!matchingWorkflow) {
      console.error(`setActiveFlow: Couldn't find workflow with id ${workflowId}`);
      return false;
    }

    const flow = Utils.deepCopy(matchingWorkflow);
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

    trackingFlow.stages.forEach((stage) => {
      const { steps } = stage;
      const shuffleInfo = (stage as any).shuffle;
      if (shuffleInfo) {
        // Shuffle the sequences of steps, as appropiate
        Utils.shuffleArray(steps, shuffleInfo.startIndex, shuffleInfo.endIndex);
      }
      stage.steps = steps;
    });

    this.activeFlow.value = trackingFlow;
    return true;
  }
}

const workflowManager = new WorkflowManager();
export default workflowManager;
