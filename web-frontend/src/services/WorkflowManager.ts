import { computed, reactive, ref } from 'vue';
import workflowsJson from
  // 'data/workflows/all_workflows.json';
  '../../../data/workflows/all_workflows.json';
import optionsManager from '@/services/OptionsManager';
import motionDB, { DatabaseEntry, MotionDatabase } from '@/services/MotionDatabase';
import MiniLesson from '@/model/MiniLesson';
import { Workflow, WorkflowStage, WorkflowStep } from '@/model/Workflow';
// import workflowsJson from '@/model/all_workflows.json';
import customWorkflowsJson from '@/model/customWorkflows.json';
import eventHub, { EventNames } from './EventHub';
import Utils from './Utils';

const thumbnailRootDir = 'thumbs/';

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

  public workflows = reactive(new Map() as Map<string, Workflow>);

  public allWorkflows = computed(() => new Array(...this.workflows.values()));

  public activeFlow = ref(null as TrackingWorkflow | null);

  constructor() {
    this.loadWorkflows();
  }

  private loadWorkflows() {
    for (let i = 0; i < defaultWorkflows.length; i += 1) {
      const workflow = defaultWorkflows[i] as Workflow;
      workflow.created = new Date(workflow.created);
      if (workflow.thumbnailSrc) workflow.thumbnailSrc = thumbnailRootDir + workflow.thumbnailSrc;
      this.addSessionWorkflow(workflow);
      this.bakedInWorkflows.add(workflow.id);
    }
    for (let i = 0; i < customWorkflows.length; i += 1) {
      const workflow = customWorkflows[i];
      workflow.created = new Date(workflow.created);
      if (workflow.thumbnailSrc) workflow.thumbnailSrc = thumbnailRootDir + workflow.thumbnailSrc;
      this.addSessionWorkflow(workflow);
      this.bakedInWorkflows.add(workflow.id);
    }

    const customWorkflowIds = WorkflowManager.getCustomWorkflowIdsList();
    for (let i = 0; i < customWorkflowIds.length; i += 1) {
      this.tryLoadCustomWorkflow(customWorkflowIds[i]);
    }
  }

  public isCustomWorkflow(id: string) {
    return !this.bakedInWorkflows.has(id);
  }

  public hasWorkflow(id: string) {
    return this.workflows.has(id);
  }

  public hasBakedInWorkflow(id: string) {
    return this.bakedInWorkflows.has(id);
  }

  public reloadCustomWorkflow(id: string) {
    if (!this.isCustomWorkflow(id)) return;

    if (!WorkflowManager.hasSavedCustomLesson(id)) {
      this.workflows.delete(id);
    } else {
      this.tryLoadCustomWorkflow(id);
    }
  }

  private static getCustomWorkflowIdsList(): Array<string> {
    return JSON.parse(window.localStorage.getItem('custom-workflows') ?? '[]');
  }

  private static saveCustomWorkflowIdsList(customLessonIds: Array<string>) {
    window.localStorage.setItem('custom-workflows', JSON.stringify(customLessonIds));
  }

  private static updateToLatestWorkflowFormat(workflow: Workflow) {
    const updatedWorkflow = workflow;
    updatedWorkflow.stages = updatedWorkflow.stages.map((stage) => ({
      ...stage,
      steps: stage.steps.map((step) => {
        const stepAny = step as any;
        const newStep = step;
        const newStepAny = newStep as any;

        // Renaming videoLesson -> miniLesson
        if (stepAny.videoLessonReference) {
          newStep.miniLessonReference = stepAny.videoLessonReference;
          delete newStepAny.videoLessonReference;
        }
        if (stepAny.videoLessonEmbedded) {
          newStep.miniLessonEmbedded = stepAny.videoLessonEmbedded;
          delete newStepAny.videoLessonEmbedded;
        }
        if (newStepAny.type === 'VideoLessonReference') newStep.type = 'MiniLessonReference';
        if (newStepAny.type === 'VideoLessonEmbedded') newStep.type = 'MiniLessonEmbedded';

        // Refactoring any embedded mini-lessons
        if (newStep.miniLessonEmbedded) {
          newStep.miniLessonEmbedded = MotionDatabase.updateLessonFormat(newStep.miniLessonEmbedded);
        }

        return newStep;
      }),
    }));

    return updatedWorkflow;
  }

  public static hasSavedCustomLesson(id: string) {
    const custWorkflowIds = WorkflowManager.getCustomWorkflowIdsList();
    return custWorkflowIds.indexOf(id) !== -1;
  }

  public addSessionWorkflow(workflow: Workflow) {
    const updatedWorkflow = WorkflowManager.updateToLatestWorkflowFormat(workflow);
    this.workflows.set(updatedWorkflow.id, updatedWorkflow);
  }

  public tryLoadCustomWorkflow(id: string) {
    try {
      const workflowRaw = window.localStorage.getItem(`workflow-${id}`);
      if (!workflowRaw) throw new Error(`No workflow found with id: ${id}`);
      const workflow = JSON.parse(workflowRaw);
      workflow.created = new Date(workflow.created);
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

  public static validateWorkflow(workflow: Workflow) {
    if (!workflow?.id) throw new Error('Workflow must have an id');
    if (!workflow?.title) throw new Error('Workflow must have an title');
    if (!Array.isArray(workflow.stages)) throw new Error('Workflow must have stages');
    workflow.stages.forEach((stage) => {
      WorkflowManager.validateWorkflowStage(stage);
    });
  }

  public static validateWorkflowStage(stage: WorkflowStage) {
    if (!stage.title) throw new Error('Stage must have a title');
    if (!Array.isArray(stage.steps)) throw new Error('Stage must have steps');
    stage.steps.forEach((step) => {
      WorkflowManager.validateWorkflowStep(step);
    });
  }

  public static validateWorkflowStep(step: WorkflowStep) {
    if (!step.title) throw new Error('Step must have a title');
    if (!step.type) throw new Error('Step must have a type');

    if (step.type === 'InstructionOnly') {
      if (!step.instructions) throw new Error('Step must have an instruction');
      if (!step.instructions.text) throw new Error('Step instruction must have a text');
      if (!step.instructions.heading) throw new Error('Step instruction must have a heading');

    } else if (step.type === 'MiniLessonReference') {
      if (!step.miniLessonReference) throw new Error('Step must have a referenced lesson');
      if (!motionDB.lessonsById.has(step.miniLessonReference.lessonId)) throw new Error(`Step's referenced lesson id ${step.miniLessonReference.lessonId} does not exist`);
      if (!motionDB.lessonsByVideo.has(step.miniLessonReference.clipName)) throw new Error(`Step's referenced lesson clipName ${step.miniLessonReference.clipName} does not exist`);

    } else if (step.type === 'MiniLessonEmbedded') {
      if (!step.miniLessonEmbedded) throw new Error('Step must have a embedded lesson');

      try {
        motionDB.validateLesson(step.miniLessonEmbedded);
      } catch (e) {
        throw new Error(`Step ${step.title} has an invalid embedded lesson. Error: ${e}`);
      }

    } else if (step.type === 'UploadTask') {
      if (!step.upload) throw new Error('Step must have an upload task');

    } else {
      throw new Error(`Step type ${step.type} is not supported`);
    }
  }
}

const workflowManager = new WorkflowManager();
export default workflowManager;
