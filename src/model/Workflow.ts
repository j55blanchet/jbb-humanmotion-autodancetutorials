import { DatabaseEntry } from '@/services/MotionDatabase';
import Utils from '@/services/Utils';
import MiniLesson from './MiniLesson';

/**
 * Userflow.ts
 *
 * Data types that represent a specific workflow in the app
 */
export interface Instructions {
  heading: string;
  text: string;
}

export interface WorkflowStep {
  type: 'InstructionOnly' | 'MiniLessonReference' | 'MiniLessonEmbedded' | 'UploadTask';
  title: string;
  instructions?: Instructions;
  miniLessonReference?: {
    clipName: string;
    lessonId: string;
  };
  miniLessonEmbedded?: MiniLesson;
  upload?: {
    identifier: string;
    prompt: string;
  };
  experiment?: {
    showInExperimentOnly?: boolean;
    // disableRepitition?: boolean;
    isTimeExpiredTask?: boolean;
  };
}

export interface WorkflowStage {
  title: string;
  steps: WorkflowStep[];
  shuffle?: {
    startIndex: number;
    endIndex: number;
  };
  maxStageTimeSecs?: number;
}

export interface Workflow {
  title: string;
  creationMethod: string;
  id: string;
  stages: WorkflowStage[];
  experimentMaxTimeSecs?: number;
}

export function CreateBlankWorkflow() {
  return {
    title: 'New Workflow',
    id: Utils.uuidv4(),
    creationMethod: 'User Created',
    stages: [],
  } as Workflow;
}

export function IsMiniLessonStep(step: WorkflowStep) {
  return step.type === 'MiniLessonReference' || step.type === 'MiniLessonEmbedded';
}
export function GetWorkflowStepVideoClipName(step: WorkflowStep) {
  return IsMiniLessonStep(step)
    ? (step.type === 'MiniLessonReference'
      ? step.miniLessonReference?.clipName ?? null
      : step.miniLessonEmbedded?.header.clipName) ?? null
    : null;
}
export function GetVideoEntryForWorkflowStep(db: any, step: WorkflowStep): DatabaseEntry | null{
  if (!IsMiniLessonStep(step)) return null;
  return db.motionsMap.get(GetWorkflowStepVideoClipName(step));
}
