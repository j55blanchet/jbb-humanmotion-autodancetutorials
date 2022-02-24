
from datetime import timedelta
from ..datatypes.Workflow import *
from ..datatypes import Instructions
from typing import *

REVIEW_ACTIVITY_THRESHOLD_SECS = 3.0
SEGMENT_LABEL_TIMEDINSTRUCTION_QUEUELENGTH_SECS = 1.0

def create_simple_speedstepped_lesson(imr: IMR, lesson_id_cache: Dict[str, str], showSkeleton: bool, segmentLesson: bool, spds: List[float]):

    creationMethod = imr.generationMethod
    learningScheme = f'SimpleSpeedStep {spds}' + (' (Skeleton)' if showSkeleton else '') + (' (Segmented)' if segmentLesson else '')
    idEntry = f"{imr.clipName}-{learningScheme}-{creationMethod}"
    workflowId = lesson_id_cache.get(idEntry, str(uuid.uuid4()))
    lesson_id_cache[idEntry] = workflowId

    spd_title_addon = (f" @ {spds[0]}x" if len(spds) == 1 else '')
    preview_endinstruction = f"Preview complete!\nNext, you'll practice this dance at {spds[0]}x speed"
    return Workflow(
        title=f"{imr.clipName}" + spd_title_addon,
        userTitle=f'Learning: "{imr.clipTitle}"' + spd_title_addon,
        id=workflowId,
        learningScheme=learningScheme,
        creationMethod=creationMethod,
        thumbnailSrc=imr.thumbnailSrc,
        stages=[
            # WorkflowStage(
            #     title="Instructions",
            #     steps=[
            #         WorkflowStep.with_instructions(
            #             stepTitle='Instructions',
            #             heading='Instructions',
            #             text=f"TBD - insert experiment as a whole instructions here",
            #             isBeforeTimeStartTask=True,
            #         )
            #     ]
            # ),
            WorkflowStage(
                title="Learning",
                maxStageTimeSecs=60*12,
                steps=[
                    Instructions.generate_instructionstep(
                        dance_title=imr.clipTitle, 
                        position=Instructions.InstructionPosition.SINGLE_STAGE_INTRODUCTION,
                        type=Instructions.WorkflowType.SPEED_STEP,
                        time_alloted=timedelta(seconds=60*12)
                    ),
                    WorkflowStep.with_minilesson(
                        stepTitle='Preview',
                        lesson=MiniLesson.construct_imr_preview(
                            imr, 
                            disableSegmentation=not segmentLesson,
                            hideSegmentLabels=True,
                            endInstruction=preview_endinstruction,
                        )
                    ),
                ] + [
                    WorkflowStep.with_lessonactivities(
                        imr=imr,
                        disableSegmentation= not segmentLesson,
                        hideSegmentLabels=True,
                        stepTitle=f'{stepTitle}' + (f' @ {spd}x' if len(spds) > 1 or not segmentLesson else ''),
                        activities=[
                             MiniLessonActivity(
                                title=activityTitle,
                                startTime=startTime,
                                endTime=endTime,
                                practiceSpeed=spd,
                                showVideoControls=False,
                                startInstruction="Get ready to follow along!",
                                # playingInstruction="Follow along!",
                                endInstruction="Try to memorize this!",
                                timedInstructions=(
                                    None if (timedInstructs is None or (not segmentLesson)) else
                                    [
                                        TimedInstruction(tiStart, tiEnd, text=tiLabel) 
                                        for tiStart, tiEnd, tiLabel in timedInstructs
                                        if tiLabel is not None and tiLabel != ''
                                    ]
                                )
                            ),
                        ] + 
                        ([
                            MiniLessonActivity(
                                title=f'Record & Review',
                                startTime=startTime,
                                endTime=endTime,
                                practiceSpeed=spd,
                                showVideoControls=False,
                                userVisual='video',
                                demoVisual='skeleton' if showSkeleton else 'none',
                                startInstruction="This part is optional - if you'd like to review your performance, record it and review it now! This recording is just for practice and won't be uploaded.",
                                playingInstruction="Recording...",
                                endInstruction="Review your performance and feel free to repeat!",
                                timedInstructions=(
                                    None if (timedInstructs is None or (not segmentLesson)) else
                                    [
                                        TimedInstruction(tiStart, tiEnd, text=tiLabel) 
                                        for tiStart, tiEnd, tiLabel in timedInstructs
                                        if tiLabel is not None and tiLabel != ''
                                    ]
                                ),
                                reviewing=ReviewInfo(
                                    showModelSkeleton=showSkeleton,
                                    showUserSkeleton=False,
                                ),
                            )
                        ] if includeReview else [])
                    )
                    for spd in spds
                    for 
                        stepTitle,
                        activityTitle, 
                        startTime, 
                        endTime,   
                        timedInstructs, 
                        includeReview in 
                    chain(
                        ([] if not segmentLesson else [
                            (f'Part {i+1}' + (f': {seg.label}' if seg.label is not None else ''), 
                            (f'Part {i+1}'),
                            seg.startTime, 
                            seg.endTime, 
                            [(seg.startTime, seg.endTime, seg.label if seg.label is not None else f'Part {i+1}')], 
                            False,# seg.endTime - seg.startTime > REVIEW_ACTIVITY_THRESHOLD_SECS
                            ) 
                            for i, seg in enumerate(imr.temporalSegments)
                        ])
                        , 
                        [
                            ('Practice' if not segmentLesson else 'Full Practice',
                            ('Practice'),
                             imr.startTime, 
                             imr.endTime, 
                             [] if not segmentLesson else ([(seg.startTime - (SEGMENT_LABEL_TIMEDINSTRUCTION_QUEUELENGTH_SECS * spd), seg.endTime, seg.label if seg.label is not None else f'Part {i+1}') for i, seg in enumerate(imr.temporalSegments)]), 
                             True)
                        ]
                    )
                ] + [
                    Instructions.generate_instructionstep(
                        dance_title=imr.clipTitle, 
                        position=Instructions.InstructionPosition.SINGLE_STAGE_PREPERFORMANCE,
                        type=Instructions.WorkflowType.SPEED_STEP,
                    ),
                ] + [
                    WorkflowStep(
                        type='UploadTask',
                        title=f'Performance @ {speed}x speed)',
                        upload=WorkflowStepUploadData(
                            identifier=f'clip={imr.clipName}-workflow={workflowId}-spd={int(speed*100)}',
                            prompt=f"Show us what you've learned so far!",
                            maxAllowedAttempts=2,
                            followAlong=WorkflowStepUploadDataFollowAlong(
                                clipName=imr.clipName,
                                visualMode='none',
                                clipSpeed=speed,
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
                    for speed in [0.5] #, 1.0)
                ]
            ),
            # WorkflowStage(
            #     title="Mastery",
            #     maxStageTimeSecs=60*8,
            #     steps=[
            #         Instructions.generate_instructionstep(
            #             dance_title=imr.clipTitle, 
            #             position=Instructions.InstructionPosition.MASTERY_INTRODUCTION,
            #             type=Instructions.WorkflowType.CONTROL,
            #             time_alloted=timedelta(seconds=60*8)
            #         ),
            #         WorkflowStep.with_lessonactivities(
            #             imr=imr,
            #             stepTitle='Practice',
            #             activities=[
            #                 MiniLessonActivity(
            #                     title='Learning',
            #                     startTime=imr.startTime,
            #                     endTime=imr.endTime,
            #                     practiceSpeed=1.0,
            #                     showVideoControls=True
            #                 )
            #             ]
            #         ),
            #         Instructions.generate_instructionstep(
            #             dance_title=imr.clipTitle, 
            #             position=Instructions.InstructionPosition.MASTERY_PREPERFORMANCE,
            #             type=Instructions.WorkflowType.CONTROL,
            #         ),
            #         WorkflowStep(
            #             type='UploadTask',
            #             title='Final Performance',
            #             upload=WorkflowStepUploadData(
            #                 identifier=f'{imr.clipName}-{workflowId}-performance',
            #                 prompt=f"Now perform this dance!",
            #                 maxAllowedAttempts=2,
            #                 followAlong=WorkflowStepUploadDataFollowAlong(
            #                     clipName=imr.clipName,
            #                     visualMode='none',
            #                     clipSpeed=1.0,
            #                     startTime=imr.startTime,
            #                     endTime=imr.endTime,
            #                 )
            #             ),
            #             experiment=WorkflowStepExperimentData(
            #                 showInExperimentOnly=True,
            #                 disableRepitition=True,
            #                 isTimeExpiredTask=True,
            #             )
            #         )
            #     ]
            # )
        ],
    )
    