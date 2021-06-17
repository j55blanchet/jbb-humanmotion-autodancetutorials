import { DatabaseEntry } from '@/services/MotionDatabase';
import Utils from '@/services/Utils';
import VideoLesson from './VideoLesson';

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
  type: 'InstructionOnly' | 'VideoLessonReference' | 'VideoLessonEmbedded' | 'UploadTask';
  title: string;
  instructions?: Instructions;
  videoLessonReference?: {
    clipName: string;
    lessonId: string;
  };
  videoLessonEmbedded?: VideoLesson;
  upload?: {
    identifier: string;
    prompt: string;
  };
}

export interface WorkflowStage {
  title: string;
  steps: WorkflowStep[];
  shuffle?: {
    startIndex: number;
    endIndex: number;
  };
}

export interface Workflow {
  title: string;
  // instructions?: Instructions;
  id: string;
  stages: WorkflowStage[];
}

export function CreateBlankWorkflow() {
  return {
    title: 'New Workflow',
    id: Utils.uuidv4(),
    stages: [],
  } as Workflow;
}

export function IsVideoLessonStep(step: WorkflowStep) {
  return step.type === 'VideoLessonReference' || step.type === 'VideoLessonEmbedded';
}
export function GetWorkflowStepVideoClipName(step: WorkflowStep) {
  return IsVideoLessonStep(step)
    ? (step.type === 'VideoLessonReference'
      ? step.videoLessonReference?.clipName ?? null
      : step.videoLessonEmbedded?.header.clipName) ?? null
    : null;
}
export function GetVideoEntryForWorkflowStep(db: any, step: WorkflowStep): DatabaseEntry | null{
  if (!IsVideoLessonStep(step)) return null;
  return db.motionsMap.get(GetWorkflowStepVideoClipName(step));
}
