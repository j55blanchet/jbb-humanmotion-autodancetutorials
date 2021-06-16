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
  type: 'InstructionOnly' | 'VideoLesson' | 'UploadTask';
  title: string;
  instructions?: Instructions;
  activity?: {
    clipName: string;
    lessonId: string;
  };
  embeddedLesson?: VideoLesson;
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
