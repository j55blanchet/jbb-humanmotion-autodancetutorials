export interface TimedInstruction {
  startTime: number;
  endTime: number;
  text: string;
}

export interface PauseInfo {
    time: number;
    pauseDuration?: number;
    instruction?: string;
    manualResume?: boolean;
}

export interface Activity {
  title: string;
  startTime: number;
  endTime: number;
  demoType?: 'video' | 'skeleton' | 'none';
  videoActive?: boolean;
  focusedSegments?: number[];
  pauses?: Array<PauseInfo>;
  practiceSpeeds?: Array<number>;
  startInstruction?: string;
  playingInstruction?: string;
  staticInstruction?: string;
  timedInstructions?: Array<TimedInstruction>;
}

export default interface DanceLesson {
  _id: string;
  header: {
    clipName: string;
    lessonTitle: string;
  };
  segmentBreaks: number[];
  activities: Array<Activity>;
  fps: number;
  poseScope: 'all' | 'upperBody';
  // eslint-disable-next-line
}
