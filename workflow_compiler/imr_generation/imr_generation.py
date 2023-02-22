
from typing import *
from ..datatypes import IMR

def create_imr(
    clipName: str,
    clipPath: str,
    clipTitle: str,
    fps: float,
    landmarkScope: List[str],
    tempoBPM: Optional[float],
    thumbnailSrc: str,
    segmentation: List[float],
    genMethod: str,
    keyframes: List[IMR.Keyframe],
) -> IMR:

    imr = IMR.IMR(
        clipName, 
        clipPath,
        clipTitle,
        genMethod=genMethod,
        startTime=segmentation[0],
        endTime=segmentation[-1],
        segments=[
            IMR.TemporalSegment(
                startTime=tempSegStart,
                endTime=tempSegEnd,
                motions=[],
                keyframes=[kf for kf in keyframes if kf.timestamp >= tempSegStart and kf.timestamp < tempSegEnd],
                motionTrails=[],
            )
            for (tempSegStart, tempSegEnd) in zip(
                segmentation[:-1],
                segmentation[1:],
            )
        ],
        fps=fps,
        landmarkScope=landmarkScope,
        tempoBPM=tempoBPM,
        keyframes=keyframes,
        thumbnailSrc=thumbnailSrc,
    )

    return imr