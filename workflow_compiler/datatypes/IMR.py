from ..datatypes import CustomSerializable


from typing import Dict, List, Optional

from dataclasses import dataclass, field
from dataclasses_json import dataclass_json

@dataclass_json
@dataclass
class Keyframe(CustomSerializable):
    timestamp: float
    significance: float

@dataclass_json
@dataclass
class MotionTrail(CustomSerializable):
    landmark: int = -1
    times: List[float] = field(default_factory=list)
    x: List[float] = field(default_factory=list)
    y: List[float] = field(default_factory=list)

@dataclass_json
@dataclass
class Motion(CustomSerializable):
    startTime: float
    endTime: float
    emphasis: List[int] = field(default_factory=list)
    
@dataclass_json
@dataclass
class TemporalSegment(CustomSerializable):
    startTime: float = 0.0
    endTime: float = 1.0
    label: Optional[str] = field(default=None)
    motions: Optional[List[Motion]] = field(default_factory=lambda: None)
    keyframes: List[Keyframe] = field(default_factory=list)
    motionTrails: List[MotionTrail] = field(default_factory=list)


class IMR(CustomSerializable):
    def __init__(self, clipName: str, clipPath: str, clipTitle: str, genMethod: str, startTime: float, endTime: float, segments: List[TemporalSegment], fps:  int, landmarkScope: List[str], tempoBPM: float = None, keyframes: Optional[List[Keyframe]] = None, thumbnailSrc: str = None) -> None:
        self.clipName = clipName
        self.clipPath = clipPath
        self.clipTitle = clipTitle
        self.generationMethod = genMethod
        self.startTime = startTime
        self.endTime = endTime
        self.temporalSegments = segments
        self.fps = fps
        self.landmarkScope = landmarkScope
        self.keyframes = keyframes
        self.tempoBPM = tempoBPM
        self.thumbnailSrc = thumbnailSrc
    
    @staticmethod
    def from_json(json: Dict):
        clipName: str = json["clipName"] 
        clipPath: str = json["clipPath"] 
        clipTitle: str = json["clipTitle"]
        genMethod: str = json["generationMethod"]
        startTime: float = json["startTime"]
        endTime: float = json["endTime"]
        temporalSegments: List = json["temporalSegments"]
        fps: int = json["fps"]
        landmarkScope: str = json["landmarkScope"]
        keyframes: Optional[List[float]] = json.get("keyframes", None)
        thumbnailSrc: Optional[str] = json.get("thumbnailSrc", None)
        tempoBPM: Optional[float] = json.get("tempoBPM", None)

        temporalSegments = list(map(TemporalSegment.from_dict, temporalSegments))
        if keyframes is not None:
            keyframes = list(map(Keyframe.from_dict, keyframes))

        return IMR(
            clipName=clipName, 
            clipPath=clipPath, 
            clipTitle=clipTitle,
            genMethod=genMethod, 
            startTime=startTime, 
            endTime=endTime, 
            segments=temporalSegments, 
            fps=fps, 
            landmarkScope=landmarkScope, 
            keyframes=keyframes, 
            tempoBPM=tempoBPM, 
            thumbnailSrc=thumbnailSrc)

    def get_segment_breaks(self):
        breaks = list(map(lambda ts: ts.startTime, self.temporalSegments))
        breaks.append(self.endTime)
        return breaks
    
    def get_segment_labels(self):
        labels = list(map(lambda ts: "" if ts.label is None else ts.label, self.temporalSegments))
        return labels
        
    def get_segment_nobreaks(self):
        return [self.startTime, self.endTime]