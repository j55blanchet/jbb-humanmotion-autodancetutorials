from .CustomSerializable import CustomSerializable
from dataclasses import dataclass
from dataclasses_json import dataclass_json

@dataclass_json
@dataclass
class MotionLessonHeader(CustomSerializable):
    clipName: str
    lessonTitle: str
