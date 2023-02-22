from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
from datetime import datetime
from .MiniLesson import *
from typing import Optional, Literal, List
from . import CustomSerializable
from .IMR import IMR

@dataclass_json
@dataclass
class WorkflowStepInstructions(CustomSerializable):
    heading: str
    text: str

@dataclass_json
@dataclass
class WorkflowStepActivityReference(CustomSerializable):
    clipName: str
    lessonId: str

@dataclass_json
@dataclass
class WorkflowStepUploadDataFollowAlong(CustomSerializable):
    clipName: str
    visualMode: Literal['none', 'skeleton', 'video']
    clipSpeed: float
    startTime: float
    endTime: float

@dataclass_json
@dataclass
class WorkflowStepUploadData(CustomSerializable):
    identifier: str
    prompt: str
    activityLogUploadIdentifier: Optional[str] = None
    maxAllowedAttempts: int = -1
    followAlong: Optional[WorkflowStepUploadDataFollowAlong] = field(default=None)

@dataclass_json
@dataclass
class WorkflowStepExperimentData(CustomSerializable):
    showInExperimentOnly: Optional[bool] = field(default=None)
    disableRepitition: Optional[bool] = field(default=None)
    isTimeExpiredTask: Optional[bool] = field(default=None)
    isBeforeTimeStartTask: Optional[bool] = field(default=None)

@dataclass_json
@dataclass
class WorkflowStep(CustomSerializable):
    type: Literal['InstructionOnly', 'MiniLessonReference', 'MiniLessonEmbedded', 'UploadTask']
    title: str
    instructions: Optional[WorkflowStepInstructions] = field(default=None)
    miniLessonReference: Optional[WorkflowStepActivityReference] = field(default=None)
    miniLessonEmbedded: Optional[MiniLesson] = field(default=None)
    upload: Optional[WorkflowStepUploadData] = field(default=None)
    experiment: Optional[WorkflowStepExperimentData] = field(default=None)
    
    @staticmethod
    def with_instructions(stepTitle: str, heading: str, text: str, **kwargs):
        experiment = None
        if 'experiment' in kwargs:
            experiment = kwargs['experiment']

        return WorkflowStep(
            type='InstructionOnly', 
            title=stepTitle, 
            instructions=WorkflowStepInstructions(
                heading=heading, 
                text=text
            ),
            experiment=experiment,
        )

    @staticmethod
    def with_minilesson(stepTitle: str, lesson: MiniLesson):
        return WorkflowStep(
            type="MiniLessonEmbedded",
            title=stepTitle,
            miniLessonEmbedded=lesson
        )

    @staticmethod
    def with_lessonactivities(
        imr: IMR, 
        stepTitle: str, 
        activities: List[MiniLessonActivity], 
        disableSegmentation: bool = False,
        hideSegmentLabels: bool = False
    ):
        return WorkflowStep(
            type="MiniLessonEmbedded",
            title=stepTitle,
            miniLessonEmbedded=MiniLesson(
                segmentBreaks= [imr.startTime, imr.endTime] if disableSegmentation else imr.get_segment_breaks(),
                segmentLabels= 
                    [""] if disableSegmentation else 
                        (["" for _ in imr.temporalSegments] if hideSegmentLabels else
                        imr.get_segment_labels()),
                clipName=imr.clipName,
                lessonTitle=stepTitle,
                activities=activities,
            )
        )

@dataclass_json
@dataclass
class WorkflowStage(CustomSerializable):
    title: str
    steps: List[WorkflowStep] = field(default_factory=list)
    maxStageTimeSecs: Optional[int] = field(default=None)

@dataclass_json
@dataclass
class Workflow(CustomSerializable):
    title: str
    userTitle: str
    creationMethod: str
    learningScheme: str
    associatedClip: Optional[str] = field(default=None)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    stages: List[WorkflowStage] = field(default_factory=list)
    created: Optional[datetime] = field(default_factory=datetime.utcnow)
    experimentMaxTimeSecs: int = field(default=None)
    thumbnailSrc: Optional[str] = field(default=None)

if __name__ == '__main__':
    s = WorkflowStep('InstructionOnly', 'my title')
    print(s.to_json())
    print(s)

    
