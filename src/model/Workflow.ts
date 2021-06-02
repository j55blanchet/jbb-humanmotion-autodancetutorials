/**
 * Userflow.ts
 *
 * Data types that represent a specific workflow in the app
 */
export interface Instructions {
  heading: string;
  body: string;
}

export interface WorkflowStep {
  type: 'InstructionOnly' | 'VideoLesson' | 'UploadTask';
  title: string;
  instructions?: Instructions;
  activity?: {
    clipName: string;
    lessonId: string;
  };
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
  id: string;
  stages: WorkflowStage[];
}
