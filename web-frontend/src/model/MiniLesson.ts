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

export type MotionTrail = Array<[number, number, number]>;
// export interface Keyframe {
//     time: number;
//     time2?: number;
// }

export interface SheetMotionFrame {
  timestamp: number;
  type: 'move' | 'pause';
  motionTrails?: Array<MotionTrail>;
}
export interface SheetMotionPhrase {
  frames: SheetMotionFrame[];
}
export interface SheetMotion {
  phrases: SheetMotionPhrase[];
  variableLength: boolean;
}

export interface MiniLessonActivity {
  title: string;
  startTime: number;
  endTime: number;
  demoVisual: 'video' | 'skeleton' | 'none';
  userVisual: 'video' | 'skeleton' | 'none'; // If the user's webcam should be on
  keyframeVisual?: 'video' | 'skeleton' | 'none'; // If the keyframe should be on
  keyframes?: number[];
  sheetMotionVisual?: 'video' | 'skeleton' | 'none';
  sheetMotion?: SheetMotion;
  emphasizedJoints?: number[];
  focusedSegments?: number[];
  pauses?: Array<PauseInfo>;
  practiceSpeed?: number;
  startInstruction?: string;
  playingInstruction?: string;
  staticInstruction?: string;
  timedInstructions?: Array<TimedInstruction>;
  endInstruction?: string;
  motionTrails?: Array<MotionTrail>;
  motionTrailBreaks?: Array<number>;
  showVideoControls?: boolean;
  recording?: {
    identifier: string;
    includeAudio: boolean;
    maxAllowedAttempts?: number;
  };
  reviewing?: {
    showModelSkeleton: boolean;
    showUserSkeleton: boolean;
  }
}

export default interface MiniLesson {
  _id: string;
  source: 'builtin' | 'custom';
  header: {
    clipName: string;
    lessonTitle: string;
  };
  segmentBreaks: number[];
  segmentLabels?: string[];
  activities: Array<MiniLessonActivity>;

  // fps: number;
  // poseScope: 'all' | 'upperBody';
  // eslint-disable-next-line
}

export class DanceUtils {
  static shouldPauseBeforeActivity(activity: MiniLessonActivity) {
    return activity.userVisual !== 'none';
  }
}
