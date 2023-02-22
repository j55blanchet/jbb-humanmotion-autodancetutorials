
from datetime import timedelta
from itertools import chain
import itertools
from typing import *
from ..datatypes.MiniLesson import *
from ..datatypes.IMR import IMR, Keyframe
from ..datatypes.Workflow import *
import uuid
from ..datatypes import Instructions

MOTION_TRAILS_SIMPLIFY_OPTIONS = {
    'max_samples_per_sec': 4,
    'dist_threshold_combine': 25,
}

def create_learningstep(imr: IMR, segment_i: int, speed: float) -> WorkflowStep:

    COMBINE_PREV_SEGMENT_THRESHOLD = 1.0

    i = segment_i
    start_overlap = 1 if i > 0 else 0
    
    seg = imr.temporalSegments[i]
    target_start_time = seg.startTime - start_overlap
    prev_seg_start_time = imr.temporalSegments[i-1].startTime if i > 0 else imr.startTime
    start_time = prev_seg_start_time if prev_seg_start_time > target_start_time - COMBINE_PREV_SEGMENT_THRESHOLD else target_start_time
    end_time = seg.endTime

    keyframes = [kf.timestamp for kf in imr.keyframes if kf.timestamp >= start_time and kf.timestamp <= end_time]
    keyframes = list(chain([start_time], keyframes, [end_time]))
    keyframes.sort()

    return WorkflowStep.with_lessonactivities(
        imr,
        f"Segment {i+1}",
        [
            MiniLessonActivity.from_temporal_segment(
                imr.temporalSegments[i],
                title="Demo",
                speed=speed,
                is_skeleton=False,
                startInstruction=f"Let's learn part {i+1}",
                playingInstruction="Follow along!",
                endInstruction="Repeat if you need to -- next up we'll try with just a skeleton",
                override_start_time=start_time,
                motionTrails=MotionFrame.simplify_trails(seg.motionTrails, MOTION_TRAILS_SIMPLIFY_OPTIONS),
                motionTrailBreaks=[kf.timestamp for kf in seg.keyframes],
                timedInstructions=[
                    TimedInstruction(s, e, f'Beat {i+1}')
                    for i, (s, e) in enumerate(zip(keyframes, chain(keyframes[1:], [end_time])))
                ]
                # pauses=[ActivityPause(time=kf, instruction=f"Keyframe {j +1 }") for j, kf in enumerate(imr.keyframes or []) if start_time < kf < imr.temporalSegments[i].endTime]
            ),
        ] +
        [
            MiniLessonActivity.from_temporal_segment(
                imr.temporalSegments[i],
                title="Practice",
                speed=speed,
                is_skeleton=True,
                startInstruction=f"Let's practice part {i+1}",
                playingInstruction="Follow along!",
                endInstruction="Memorize this! Next, you'll try this part from memory!",
                override_start_time=start_time,
            )
        ] +
        [
            MiniLessonActivity(
                title="Test & Review",
                startTime=start_time,
                endTime=end_time,
                userVisual='video',
                demoVisual='none',
                practiceSpeed=speed,
                startInstruction="Do you have it? Let's try without the skeleton.",
                playingInstruction="(feel free to go back to the previous activity if you need to)",
                endInstruction=f"Next up: combining this what you learned earlier",
                recording=None,
                reviewing=ReviewInfo(
                    showModelSkeleton=True,
                    showUserSkeleton=False,
                )
                # recordBehavior="video-only",
                # reviewBehavior="video"
            ),
        ]
        + (
            [] if i == 0 or start_time - COMBINE_PREV_SEGMENT_THRESHOLD < imr.startTime else 
            [
                MiniLessonActivity(
                    title="Full Practice",
                    startTime=imr.startTime,
                    endTime=imr.temporalSegments[i].endTime,
                    userVisual='video',
                    demoVisual='skeleton',
                    practiceSpeed=speed,
                    startInstruction="Now try everything we learned so far",
                    endInstruction=f"Nice job!"
                )
            ]
        )
    )

def create_simple_lesson(imr: IMR, lessonIdCache: Dict[str, str]) -> Workflow:

    compilationMethod = 'RuleBasedV2',
    fullCreationMethod = f'{compilationMethod} ({imr.generationMethod})'
    idEntry = imr.clipName + "-" + fullCreationMethod
    workflowId = lessonIdCache.get(idEntry, str(uuid.uuid4()))
    lessonIdCache[idEntry] = workflowId
    workflow = Workflow(
        title=f"{imr.clipName}",
        userTitle=f'Learn "{imr.clipTitle}"',
        id=workflowId,
        creationMethod=fullCreationMethod,
        thumbnailSrc=imr.thumbnailSrc,
        associatedClip=imr.clipName,
    )
    
    learning_speeds = [0.5]
    workflow.stages.extend([
        WorkflowStage(
            title=f'Learning ({int(speed * 100)}% speed)',

            steps=[
                Instructions.generate_instructionstep(
                    dance_title=imr.clipTitle, 
                    position=Instructions.InstructionPosition.LEARNING_INTRODUCTION,
                    type=Instructions.WorkflowType.CURRENT_MERGED,
                    time_alloted=timedelta(seconds=60*12)
                ),
                WorkflowStep.with_minilesson(
                    stepTitle='Preview',
                    lesson=MiniLesson.construct_imr_preview(imr)
                )
            ] + [
                create_learningstep(imr, i, speed)
                for i in range(len(imr.temporalSegments))
            ] + [
                # WorkflowStep.with_lessonactivities(
                #     imr=imr,
                #     stepTitle='Review',
                #     activities=[
                #         MiniLessonActivity(
                #             title="Half Speed",
                #             startTime=imr.startTime,
                #             endTime=imr.endTime,
                #             userVisual='video',
                #             startInstruction="Now try everything we learned so far at {spdName}}",
                #             practiceSpeed=spd,
                #             recordBehavior="video-only",
                #             reviewBehavior="video",
                #         )
                #         for spd, spdName in [(0.5, "half speed"), (0.75, "3/4 speed"), (1.0, "full speed")]
                #     ]
                # ),
                Instructions.generate_instructionstep(
                    dance_title=imr.clipTitle, 
                    position=Instructions.InstructionPosition.LEARNING_PREPERFORMANCE,
                    type=Instructions.WorkflowType.CURRENT_MERGED,
                )
            ] + [
                WorkflowStep(
                    type='UploadTask',
                    title=f'Check-In Performance ({int(perfspeed * 100)}% speed)',
                    upload=WorkflowStepUploadData(
                        identifier=f'{imr.clipName}-{workflow.id}-initial-{perfspeed}',
                        prompt=f"Show us what you've learned so far!",
                        maxAllowedAttempts=2,
                        followAlong=WorkflowStepUploadDataFollowAlong(
                            clipName=imr.clipName,
                            visualMode='none',
                            clipSpeed=perfspeed,
                            startTime=imr.startTime,
                            endTime=imr.endTime,
                        )
                    ),
                    experiment=WorkflowStepExperimentData(
                        showInExperimentOnly=True,
                        disableRepitition=True,
                        isTimeExpiredTask=True,
                    )                    
                )
                for perfspeed in [speed, 1.0]
            ],
            maxStageTimeSecs=60*12
        )
        for speed in learning_speeds
    ])    

    mastery_speeds = [0.5, 0.75, 1]
    workflow.stages.extend([
        WorkflowStage(
            title=f'Mastery',
            maxStageTimeSecs=60*8,
            steps=[
                Instructions.generate_instructionstep(
                    dance_title=imr.clipTitle, 
                    position=Instructions.InstructionPosition.MASTERY_INTRODUCTION,
                    type=Instructions.WorkflowType.CURRENT_MERGED,
                    time_alloted=timedelta(seconds=60*8)
                )
            ] + 
            [
                WorkflowStep.with_lessonactivities(
                    imr=imr,
                    stepTitle=f'Full Dance @ {int(speed * 100)}%',
                    activities=[
                        MiniLessonActivity(
                            title="With Video",
                            startTime=imr.startTime,
                            endTime=imr.endTime,
                            userVisual='none',
                            demoVisual='video',
                            practiceSpeed=speed,
                            startInstruction=f"Let's perform the whole thing now!",
                            endInstruction=f"Next up: just using the skeleton"
                        ),
                    ] +
                    [
                        MiniLessonActivity(
                            title="Skeleton Only",
                            startTime=imr.startTime,
                            endTime=imr.endTime,
                            userVisual='video',
                            demoVisual='skeleton',
                            practiceSpeed=speed,
                            startInstruction=f"Now try it with just the skeleton",
                            endInstruction=f"Next up: doing it from memory. You got this!"
                        ),
                    ] + 
                    [
                        MiniLessonActivity(
                            title="From Memory",
                            startTime=imr.startTime,
                            endTime=imr.endTime,
                            userVisual='video',
                            demoVisual='none',
                            practiceSpeed=speed,
                            startInstruction=f"Now try doing it from memory",
                            endInstruction=f"Nice job!"
                        )
                    ]
                )
                for speed in mastery_speeds
            ] + [
                Instructions.generate_instructionstep(
                    dance_title=imr.clipTitle, 
                    position=Instructions.InstructionPosition.MASTERY_PREPERFORMANCE,
                    type=Instructions.WorkflowType.CURRENT_MERGED,
                ),
                WorkflowStep(
                    type='UploadTask',
                    title='Final Performance',
                    upload=WorkflowStepUploadData(
                        identifier=f'{imr.clipName}-{workflow.id}-performance',
                        prompt=f"Now perform this dance!",
                        maxAllowedAttempts=2,
                        followAlong=WorkflowStepUploadDataFollowAlong(
                            clipName=imr.clipName,
                            visualMode='none',
                            clipSpeed=1.0,
                            startTime=imr.startTime,
                            endTime=imr.endTime,
                        )
                    ),
                    experiment=WorkflowStepExperimentData(
                        showInExperimentOnly=True,
                        # disableRepitition=True,
                        isTimeExpiredTask=True,
                    )
                )
            ],
        )
    ])
    return workflow