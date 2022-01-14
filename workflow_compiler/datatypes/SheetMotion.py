import math
from typing import *
from itertools  import chain
from dataclasses import dataclass, field, InitVar
from dataclasses_json import dataclass_json

from .IMR import MotionTrail as IMRMotionTrail


from . import CustomSerializable

MotionTrail = List[Tuple[float, float, float]]

class SimplifyOptions(TypedDict):
    max_samples_per_sec: Optional[int]
    dist_threshold_combine: Optional[float]

@dataclass_json
@dataclass
class MotionFrame(CustomSerializable):
    timestamp: float
    type: Literal['move', 'pause'] = 'move'
    motionTrails: List[MotionTrail] = field(default_factory=list)
    simplify: InitVar[Optional[SimplifyOptions]] = None
    
    @staticmethod
    def simplify_trails(trails: Sequence[MotionTrail], options: SimplifyOptions):
        if len(trails) > 0 and isinstance(trails[0], IMRMotionTrail):
            trails = [
                [
                    (trail.times[j], trail.x[j], trail.y[j]) 
                    for j in range(len(trail.times))
                ]
                for trail in trails
            ]
        return list(MotionFrame.simplify_trails_helper(trails, options))

    @staticmethod
    def simplify_trails_helper(trails: Sequence[MotionTrail], options: SimplifyOptions):
        if not options:
            return trails
        
        max_samples_per_sec = options['max_samples_per_sec']
        dist_threshold_combine = options['dist_threshold_combine']
        if max_samples_per_sec is not None or dist_threshold_combine is not None:
            for i in range(len(trails)):
                yield list(MotionFrame.reduce_trail(max_samples_per_sec, dist_threshold_combine, trails[i]))

    @staticmethod
    def reduce_trail(max_samples_per_sec: Optional[int], dist_threshold_combine: Optional[float], trail: List[Tuple[float, float, float]]):

        min_time_passing = -math.inf if max_samples_per_sec in (None, 0) else 1.0 / max_samples_per_sec
        dist_threshold_combine = math.inf if dist_threshold_combine is None else dist_threshold_combine

        pt, px, py = -math.inf, math.inf, math.inf

        for t, x, y in trail:
            d = math.dist((t, x, y), (pt, px, py))
            if t - pt > min_time_passing or d > dist_threshold_combine:
                yield (t, x, y)
                pt, px, py = t, x, y
    
    def __post_init__(self, simplify: Optional[SimplifyOptions]):
        self.motionTrails = MotionFrame.simplify_trails(self.motionTrails, simplify)

@dataclass_json
@dataclass
class MotionPhrase(CustomSerializable):
    frames: List[MotionFrame] = field(default_factory=list)

@dataclass_json
@dataclass
class SheetMotion(CustomSerializable):
    phrases: List[MotionPhrase] = field(default_factory=list)
    variableLength: bool = False
    
