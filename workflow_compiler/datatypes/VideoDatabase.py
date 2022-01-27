from dataclasses import dataclass, field
from pathlib import Path
from typing import IO, List, Optional, Dict
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
    tags: List[str]
    landmarkScope: List[str]
    thumbnailSrc: Optional[str] = None
    audioSrc: Optional[str] = None


class VideoDatabase():

    def __init__(self, filepath: Path) -> None:
        self.entries: Dict[str, VideoDatabaseEntry] = {}
        with open(filepath) as file:
            jsonstr = file.read()
            entries_list: List[VideoDatabaseEntry] = VideoDatabaseEntry.schema().loads(jsonstr, many=True)
            del jsonstr
            kv_pairs = map(lambda entry: (entry.clipName, entry), entries_list)
            self.entries = dict(kv_pairs)
            
        