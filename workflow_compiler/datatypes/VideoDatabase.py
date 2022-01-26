from dataclasses import dataclass, field
from typing import Optional
from dataclasses_json import dataclass_json
from datetime import datetime
from . import CustomSerializable

@dataclass_json
@dataclass
class VideoDatabaseEntry(CustomSerializable):
    title: str
    clipName: str
    clipPath: str
    frameCount: int
    fps: float
    duration: float
    width: int
    height: int
    startTime: float
    endTime: float
    poseUpperBodyOnly: bool
    tags: list
    landmarkScope: list
    thumbnailSrc: Optional[str] = None
    audioSrc: Optional[str] = None


