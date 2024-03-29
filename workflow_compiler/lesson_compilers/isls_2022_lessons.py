
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

def create_isls2022_segmentlearningstep(imr: IMR, segment_i: int, speed: float, useSheetMotion: bool) -> WorkflowStep:

    COMBINE_PREV_SEGMENT_THRESHOLD = 1.0

    i = segment_i
    start_overlap = 1 if i > 0 else 0
    
    seg = imr.temporalSegments[i]
    target_start_time = seg.startTime - start_overlap
    prev_seg_start_time = imr.temporalSegments[i-1].startTime if i > 0 else imr.startTime
    start_time = prev_seg_start_time if prev_seg_start_time > target_start_time - COMBINE_PREV_SEGMENT_THRESHOLD else target_start_time
    end_time = seg.endTime

    keyframes = [kf.timestamp for kf in imr.keyframes if kf.timestamp >= start_time and kf.timestamp <= end_time] if imr.keyframes is not None else []
    keyframes = list(chain([start_time], keyframes, [end_time]))
    keyframes.sort()

    return WorkflowStep.with_lessonactivities(
        imr,
        f"Segment {i+1}",
        [
            MiniLessonActivity.from_temporal_segment(
                imr.temporalSegments[i],
                title="Learn",
                speed=speed,
                is_skeleton=False,
                startInstruction=f"Let's memorize part {i+1}. Follow along with the video.",
                endInstruction="Now try repeating this part until you've memorized it.\n(try doing it with your eyes closed)" if not useSheetMotion else "Feel free to repeat this step to help get it memorized!",
                override_start_time=start_time,
                # motionTrails=MotionFrame.simplify_trails(seg.motionTrails, MOTION_TRAILS_SIMPLIFY_OPTIONS),
                # motionTrailBreaks=[kf.timestamp for kf in seg.keyframes],
                # pauses=[ActivityPause(time=kf, instruction=f"Keyframe {j +1 }") for j, kf in enumerate(imr.keyframes or []) if start_time < kf < imr.temporalSegments[i].endTime]
            ),
        ] +
        (
            [
                MiniLessonActivity.from_temporal_segment(
                    imr.temporalSegments[i],
                    title="Practice",
                    speed=speed,
                    is_skeleton=True,
                    startInstruction=f"Let's practice this! Use the skeleton overlay to refine your performance.",
                    endInstruction="How was that? Feel free to repeat and practice some more!",
                    override_start_time=start_time,
                )
            ] if not useSheetMotion or len(keyframes) <= 2 else
            [
                # MiniLessonActivity(
                #     title="Breakdown",
                #     startTime=start_time,
                #     endTime=end_time,
                #     practiceSpeed=speed,
                #     startInstruction=f"Let's break this down by the beat",
                #     playingInstruction="Try following along!",
                #     endInstruction="Next you'll try it with sheet motion.",
                #     pauses=[ActivityPause(time=kf.timestamp) for j, kf in enumerate(seg.keyframes or [])],
                #     motionTrails=MotionFrame.simplify_trails(seg.motionTrails, MOTION_TRAILS_SIMPLIFY_OPTIONS),
                #     motionTrailBreaks=[kf.timestamp + 0.01 for kf in seg.keyframes[1:]],
                #     timedInstructions=[
                #         TimedInstruction(s, e, f'Beat {i+1}')
                #         for i, (s, e) in enumerate(zip(keyframes, chain(keyframes[1:], [end_time])))
                #     ]
                # ),
                MiniLessonActivity(
                    title="Practice",
                    startTime=seg.startTime,
                    endTime=end_time,
                    practiceSpeed=speed,
                    demoVisual='none',
                    startInstruction=f"Let's practice this without the demo video!",
                    endInstruction="Feel free to repeat this much as you'd like!",
                    sheetMotionVisual='video',
                    sheetMotion=SheetMotion(
                        phrases=[
                            MotionPhrase(frames=[
                                MotionFrame(
                                    timestamp=kf.timestamp,
                                    type='move' if kf.significance >= 0.0 else 'pause',
                                    motionTrails=[
                                        [
                                            (trail.times[j], trail.x[j], trail.y[j]) for j in range(len(trail.times))
                                            if trail.times[j] >= kf.timestamp and trail.times[j] < nextkf.timestamp
                                        ] for trail in seg.motionTrails
                                    ],
                                    simplify=MOTION_TRAILS_SIMPLIFY_OPTIONS,
                                )
                                for kf, nextkf in zip(
                                    seg.keyframes,
                                    itertools.chain(seg.keyframes[1:], [Keyframe(timestamp=end_time, significance=0.0)])
                                )
                            ])
                        ]
                    )
                )
            ]
        ) +
        [
            MiniLessonActivity(
                title="Test & Review",
                startTime=start_time,
                endTime=end_time,
                userVisual='video',
                demoVisual='none',
                practiceSpeed=speed,
                startInstruction="Do you have it? Let's try without the " + ("sheet motion." if useSheetMotion else " skeleton."),
                endInstruction=f"Next up: combining this what you learned earlier" if i != 0 else "Nice work! Feel free to repeat these steps, or hit 'Done' when you're ready to move on.",
                # recordBehavior="video-only",
                # reviewBehavior="video"
            ),
        ]
        + (
            [] if i == 0 or start_time - COMBINE_PREV_SEGMENT_THRESHOLD < imr.startTime else 
            ([
                MiniLessonActivity(
                    title="From the Start",
                    startTime=imr.startTime,
                    endTime=imr.temporalSegments[i].endTime,
                    userVisual='video',
                    demoVisual='skeleton',
                    practiceSpeed=speed,
                    startInstruction="Now try it from the beginning!",
                    endInstruction=f"Nice job!"
                )
            ] if not useSheetMotion else [
                MiniLessonActivity(
                    title="From the Start",
                    startTime=imr.startTime,
                    endTime=imr.temporalSegments[i].endTime,
                    practiceSpeed=speed,
                    demoVisual='none',
                    sheetMotionVisual='skeleton',
                    startInstruction="Now try it from the beginning!",
                    endInstruction=f"Nice job!",
                    sheetMotion=SheetMotion(
                        phrases=[
                            MotionPhrase(frames=[
                                MotionFrame(
                                    timestamp=kf.timestamp,
                                    type='move' if kf.significance >= 0.0 else 'pause',
                                    motionTrails=[
                                        [
                                            (trail.times[j], trail.x[j], trail.y[j]) for j in range(len(trail.times))
                                            if trail.times[j] >= kf.timestamp and trail.times[j] < nextkf.timestamp
                                        ] for trail in full_practice_seg.motionTrails
                                    ],
                                    simplify=MOTION_TRAILS_SIMPLIFY_OPTIONS,
                                )
                                for kf, nextkf in zip(
                                    full_practice_seg.keyframes,
                                    itertools.chain(full_practice_seg.keyframes[1:], [Keyframe(timestamp=end_time, significance=0.0)])
                                )
                            ])
                            for full_practice_seg in imr.temporalSegments[:segment_i+1]
                        ]
                    )
                )
            ])
        )
    )

def create_isls2022_lesson(imr: IMR, useSheetMotion: bool, lessonIdCache: Dict[str, str]) -> Workflow:

    compilationMethod = imr.generationMethod
    learningScheme= "V1 w/ " + ("Sheet Motion" if useSheetMotion else "Skeleton Overlay")
    idEntry = f"{imr.clipName}-{compilationMethod}-{learningScheme}"
    workflowId = lessonIdCache.get(idEntry, str(uuid.uuid4()))
    lessonIdCache[idEntry] = workflowId
    workflow = Workflow(
        title=f"{imr.clipName}" + (" with sheet motion" if useSheetMotion else ""),
        userTitle=f'Learning: "{imr.clipTitle}"',
        id=workflowId,
        creationMethod=compilationMethod,
        learningScheme=learningScheme,
        associatedClip=imr.clipName,
        thumbnailSrc=imr.thumbnailSrc,
    )
    
    # workflow.stages.append(
    #     WorkflowStage(
    #         title='Instructions',
    #         steps=[
    #             WorkflowStep.with_instructions(
    #                 stepTitle='Instructions',
    #                 heading='Instructions',
    #                 text=f"TBD - insert experiment as a whole instructions here",
    #                 isBeforeTimeStartTask=True,
    #             )
    #         ]
    #     )
    # )
    
    learning_speeds = [0.5]
    workflow.stages.extend([
        WorkflowStage(
            title=f'Learning ({int(speed * 100)}% speed)',

            steps=[
                Instructions.generate_instructionstep(
                    dance_title=imr.clipTitle, 
                    position=Instructions.InstructionPosition.LEARNING_INTRODUCTION,
                    type=Instructions.WorkflowType.LEGACY_SHEETMOTION if useSheetMotion else Instructions.WorkflowType.LEGACY_SKELETON,
                    time_alloted=timedelta(seconds=60*12)
                ),
                WorkflowStep.with_minilesson(
                    stepTitle='Preview',
                    lesson=MiniLesson.construct_imr_preview(imr)
                )
            ] + [
                create_isls2022_segmentlearningstep(imr, i, speed, useSheetMotion)
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
                    type=Instructions.WorkflowType.LEGACY_SHEETMOTION if useSheetMotion else Instructions.WorkflowType.LEGACY_SKELETON,
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
                    type=Instructions.WorkflowType.LEGACY_SHEETMOTION if useSheetMotion else Instructions.WorkflowType.LEGACY_SKELETON,
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
                    ] + ([
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
                    ] if not useSheetMotion else [
                        MiniLessonActivity(
                            title="Sheet Motion",
                            startTime=imr.startTime,
                            endTime=imr.endTime,
                            userVisual='none',
                            practiceSpeed=speed,
                            startInstruction=f"Now try it with just the sheet motion",
                            endInstruction=f"Next up: doing it from memory. You got this!",
                            demoVisual='none',
                            sheetMotionVisual='video',
                            sheetMotion=SheetMotion(
                                phrases=[
                                    MotionPhrase(frames=[
                                        MotionFrame(
                                            timestamp=kf.timestamp,
                                            type='move' if kf.significance >= 0.0 else 'pause',
                                            motionTrails= [
                                                [
                                                    (trail.times[j], trail.x[j], trail.y[j]) for j in range(len(trail.times))
                                                    if trail.times[j] >= kf.timestamp and trail.times[j] < nextkf.timestamp
                                                ] for trail in seg.motionTrails
                                            ],
                                            simplify=MOTION_TRAILS_SIMPLIFY_OPTIONS,
                                        )
                                        for kf, nextkf in zip(
                                            seg.keyframes,
                                            itertools.chain(seg.keyframes[1:], [Keyframe(timestamp=seg.endTime, significance=0.0)])
                                        )]
                                    )
                                    for seg in imr.temporalSegments
                                ]
                            )
                        )
                    ]
                    ) + [
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
                    type=Instructions.WorkflowType.LEGACY_SHEETMOTION if useSheetMotion else Instructions.WorkflowType.LEGACY_SKELETON,
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