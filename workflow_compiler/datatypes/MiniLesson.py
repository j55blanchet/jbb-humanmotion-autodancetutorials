from itertools import chain
from typing import List, Literal, Optional, Union

import uuid
import numpy as np

from . import CustomSerializable, MotionLessonHeader
from .IMR import *
from .SheetMotion import MotionFrame, MotionPhrase, SheetMotion

from dataclasses import dataclass, field
from dataclasses_json import dataclass_json

class TimedInstruction(CustomSerializable):
    def __init__(self, startTime: float, endTime: float, text: str) -> None:
        self.startTime = startTime
        self.endTime = endTime
        self.text = text
        super().__init__()


class ActivityPause(CustomSerializable):
    def __init__(self, time: float, pauseDuration: float = None, instruction: str = None, manualResume: bool = None) -> None:
        self.time = time
        self.pauseDuration = pauseDuration
        self.instruction = instruction
        self.manualResume = manualResume
        super().__init__()

@dataclass_json
@dataclass
class RecordInfo(CustomSerializable):
    identifier: str
    includeAudio: bool = True
    maxAllowedAttempts: Optional[int] = None

@dataclass_json
@dataclass
class ReviewInfo(CustomSerializable):
    showModelSkeleton: bool = True
    showUserSkeleton: bool = False

class MiniLessonActivity(CustomSerializable):

    @staticmethod
    def from_temporal_segment(seg: TemporalSegment, title: str, speed: float, is_skeleton: bool = False, override_start_time: float = None, **kwargs):
        return MiniLessonActivity(
            title=title,
            startTime=seg.startTime if override_start_time is None else override_start_time,
            endTime=seg.endTime,
            demoVisual='skeleton' if is_skeleton else 'video',
            userVisual='video' if is_skeleton else 'none',
            practiceSpeed=speed,
            **kwargs
        )

    def __init__(
            self,
            title: str,
            startTime: float,
            endTime: float,
            userVisual: Literal['none', 'skeleton', 'video'] = 'none',
            demoVisual: Literal['none', 'skeleton', 'video'] = 'video',
            keyframeVisual: Literal['none', 'skeleton', 'video'] = 'none',
            keyframes: List[float] = None,
            sheetMotionVisual: Literal['none', 'skeleton', 'video'] = 'none',
            sheetMotion: SheetMotion = None,
            focusedSegments: List[float] = None,
            pauses: List[ActivityPause] = [],
            practiceSpeed: float = 1,
            startInstruction: str = None, 
            playingInstruction: str = None, 
            staticInstruction: str = None, 
            endInstruction: str = None, 
            timedInstructions: List[TimedInstruction] = [],
            showVideoControls: bool = False,
            motionTrails: List[MotionTrail] = [],
            motionTrailBreaks: List[float] = None,
            recording: Optional[RecordInfo] = None,
            reviewing: Optional[ReviewInfo] = None,
    ):

        assert isinstance(pauses, list) 
        if timedInstructions is None: timedInstructions = []
        assert isinstance(timedInstructions, list)

        self.title = title
        self.startTime = startTime
        self.endTime = endTime
        self.userVisual = userVisual
        self.demoVisual = demoVisual
        self.keyframeVisual = keyframeVisual
        self.keyframes = keyframes
        self.sheetMotion = sheetMotion
        self.sheetMotionVisual = sheetMotionVisual
        self.focusedSegments = focusedSegments
        self.pauses = pauses
        self.practiceSpeed = practiceSpeed        
        self.staticInstruction = staticInstruction
        self.playingInstruction = playingInstruction
        self.startInstruction = startInstruction
        self.endInstruction = endInstruction
        self.timedInstructions = timedInstructions
        self.showVideoControls = showVideoControls
        self.motionTrails = motionTrails
        self.motionTrailBreaks = motionTrailBreaks
        self.recording = recording
        self.reviewing = reviewing
        super().__init__()

    class VisualType:
        NONE = 'none'
        SKELETON = 'skeleton'
        VIDEO = 'video'

class MiniLesson(CustomSerializable):
    def __init__(self, segmentBreaks: List[float], _id: str = None, segmentLabels: Optional[List[str]] = None, header: MotionLessonHeader = None, activities: List[MiniLessonActivity] = [] , landmarkScope: Optional[List[str]] = None, clipName: Optional[str] = None, lessonTitle: Optional[str] = None) -> None:

        self._id = str(uuid.uuid4()) if _id is None else _id
        self.id = _id
        self.header = MotionLessonHeader(clipName, lessonTitle) if header is None else header
        self.clipName = self.header.clipName
        self.lessonTitle = self.header.lessonTitle
        self.segmentBreaks = segmentBreaks
        self.segmentLabels = segmentLabels
        self.activities = activities
        self.landmarkScope = landmarkScope
        self.source = 'builtin'

        super().__init__()
    
    @staticmethod
    def construct_imr_preview(
        imr: IMR, 
        lessonTitle: str = 'Preview', 
        # activityTitle: str = 'Preview',
        disableSegmentation: bool=False,
        hideSegmentLabels: bool=False,
        endInstruction: str=None,
    ):
        activities = []

        disableSegmentation = disableSegmentation or len(imr.temporalSegments) == 1

        fast_preview = MiniLessonActivity(
            title="Fast Preview",
            startTime=imr.startTime,
            endTime=imr.endTime,
            practiceSpeed=1.5,
            startInstruction="Here's a sped-up version of the dance",
            playingInstruction="Sped-up version",
            endInstruction="Click a button below to continue"
        )
        activities.append(fast_preview)

        preview_activity = MiniLessonActivity(
            title="Slow Preview" if disableSegmentation else "Split into parts",
            startTime=imr.startTime,
            endTime=imr.endTime,
            practiceSpeed=1.0,
            startInstruction=
                "Here's the dance at a normal speed" + (
                    "" if disableSegmentation 
                    else f". The dance is split into {len(imr.temporalSegments)} parts"
                ),
            playingInstruction=f"Normal speed" if disableSegmentation else None,
            endInstruction=endInstruction,
            timedInstructions=[] if disableSegmentation else [  
                TimedInstruction(
                    seg.startTime, 
                    seg.endTime,
                    f"Part {i+1}" if seg.label is None else seg.label,
                )
                for i, seg in enumerate(imr.temporalSegments)
            ],
            pauses=[] if disableSegmentation else [
                ActivityPause(
                    time=seg.startTime,
                    instruction=f"Now, Part {i+1}" if seg.label is not None else None,
                ) for i, seg in enumerate(imr.temporalSegments)
            ],
            # keyframes= keyframes, 
            # keyframeVisual='skeleton' if keyframes is not None else 'none',
        )
        activities.append(preview_activity)

        # sheetmusic_activity = MiniLessonActivity(
        #     title=f"{activityTitle} Sheet Music",
        #     startTime=imr.startTime,
        #     endTime=imr.endTime,
        #     practiceSpeed=speed,
        # sheetMotion=SheetMotion(
        #     phrases=[
        #         MotionPhrase(frames=[
        #             MotionFrame(
        #                 timestamp=kf.timestamp,
        #                 type='move' if kf.significance > 2.0 else 'pause',
        #             )
        #             for kf in imr.keyframes
        #             if kf.timestamp >= seg.startTime and kf.timestamp <= seg.endTime
        #         ])
        #         for seg in imr.temporalSegments
        #     ]
        # ),
        #     sheetMotionVisual='video',
        #     demoVisual='none',
        # )
        # if len(imr.keyframes) > 0:
        #     activities.append(sheetmusic_activity)

        return MiniLesson(
            lessonTitle=lessonTitle,
            clipName=imr.clipName,
            segmentBreaks=[imr.startTime, imr.endTime] if disableSegmentation else imr.get_segment_breaks(),
            segmentLabels=[""] if disableSegmentation else 
                    (["" for _ in imr.temporalSegments] if hideSegmentLabels else imr.get_segment_labels()),
            activities=activities
        )