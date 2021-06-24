import { computed, reactive, ref } from 'vue';
import optionsManager from '@/services/OptionsManager';
import motionDB, { DatabaseEntry, MotionDatabase } from '@/services/MotionDatabase';
import MiniLesson from '@/model/MiniLesson';
import { Workflow, WorkflowStage, WorkflowStep } from '@/model/Workflow';
import workflowsJson from '@/model/workflows.json';
import customWorkflowsJson from '@/model/customWorkflows.json';
import eventHub, { EventNames } from './EventHub';
import Utils from './Utils';

const defaultWorkflows = workflowsJson as Workflow[];
const customWorkflows = customWorkflowsJson as Workflow[];

export interface TrackingWorkflowStep extends WorkflowStep {
  status: 'notstarted' | 'inprogress' | 'completed';
}

export interface TrackingWorkflowStage extends WorkflowStage {
  steps: TrackingWorkflowStep[];
}

export interface TrackingWorkflow extends Workflow {
  stages: TrackingWorkflowStage[];
}

export class WorkflowManager {

  private bakedInWorkflows = new Set<string>();

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
      this.bakedInWorkflows.add(workflow.id);
    }
    for (let i = 0; i < customWorkflows.length; i += 1) {
      const workflow = customWorkflows[i];
      this.workflows.set(workflow.id, workflow);
      this.bakedInWorkflows.add(workflow.id);
    }

    const customWorkflowIds = WorkflowManager.getCustomWorkflowIdsList();
    for (let i = 0; i < customWorkflowIds.length; i += 1) {
      this.tryLoadCustomLesson(customWorkflowIds[i]);
    }
  }

  public isCustomWorkflow(id: string) {
    return !this.bakedInWorkflows.has(id);
  }

  public reloadCustomWorkflow(id: string) {
    if (!this.isCustomWorkflow(id)) return;

    if (!WorkflowManager.hasSavedCustomLesson(id)) {
      this.workflows.delete(id);
    } else {
      this.tryLoadCustomLesson(id);
    }
  }

  private static getCustomWorkflowIdsList(): Array<string> {
    return JSON.parse(window.localStorage.getItem('custom-workflows') ?? '[]');
  }

  private static saveCustomWorkflowIdsList(customLessonIds: Array<string>) {
    window.localStorage.setItem('custom-workflows', JSON.stringify(customLessonIds));
  }

  public static hasSavedCustomLesson(id: string) {
    const custWorkflowIds = WorkflowManager.getCustomWorkflowIdsList();
    return custWorkflowIds.indexOf(id) !== -1;
  }

  public addSessionWorkflow(workflow: Workflow) {
    this.workflows.set(workflow.id, workflow);
  }

  public tryLoadCustomLesson(id: string) {
    try {
      const workflowRaw = window.localStorage.getItem(`workflow-${id}`);
      if (!workflowRaw) throw new Error(`No workflow found with id: ${id}`);
      const workflow = JSON.parse(workflowRaw);
      this.addSessionWorkflow(workflow);
    } catch (e) {
      console.warn('Error loading custom lesson', id, e);
    }
  }

  public deleteCustomWorkflow(id: string) {
    this.workflows.delete(id);
    window.localStorage.removeItem(`workflow-${id}`);
    const custWorkflowIds = WorkflowManager.getCustomWorkflowIdsList();
    const index = custWorkflowIds.indexOf(id);
    if (index !== -1) {
      custWorkflowIds.splice(index, 1);
      WorkflowManager.saveCustomWorkflowIdsList(custWorkflowIds);
    }
  }

  public upsertCustomWorkflow(workflow: Workflow) {
    this.addSessionWorkflow(workflow);
    this.workflows.set(workflow.id, workflow);
    window.localStorage.setItem(`workflow-${workflow.id}`, JSON.stringify(workflow));

    const custWorkflowIds = WorkflowManager.getCustomWorkflowIdsList();
    if (!WorkflowManager.hasSavedCustomLesson(workflow.id)) {
      console.log(`Added custom lesson ${workflow.title} id=${workflow.id} to localstorage`);
      custWorkflowIds.push(workflow.id);
    } else {
      console.log(`Updated custom lesson ${workflow.title} id=${workflow.id} in localstorage`);
    }
    WorkflowManager.saveCustomWorkflowIdsList(custWorkflowIds);
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

  public completeActivitesPriorToStageAndStep(stageIndex: number, stepIndex: number) {
    if (!this.activeFlow.value) return;
    const { stages } = this.activeFlow.value;
    for (let i = 0; i < stages.length; i += 1) {
      const { steps } = stages[i];
      for (let j = 0; j < steps.length; j += 1) {
        steps[j].status = i < stageIndex ? 'completed' : 'notstarted';
        if (i === stageIndex) {
          steps[j].status = j < stepIndex ? 'completed' : 'notstarted';
        }
      }
    }
  }
}

const workflowManager = new WorkflowManager();
export default workflowManager;
