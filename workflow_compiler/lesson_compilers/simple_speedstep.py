
from datetime import timedelta
from ..datatypes.Workflow import *
from ..datatypes import Instructions
from typing import *

def create_simple_speedstepped_lesson(imr: IMR, lesson_id_cache: Dict[str, str], showSkeleton: bool, segmentLesson: bool, spds: List[float]):

    creationMethod = imr.generationMethod
    learningScheme = f'SimpleSpeedStep {spds}' + (' (Skeleton)' if showSkeleton else '') + (' (Segmented)' if segmentLesson else '')
    idEntry = f"{imr.clipName}-{learningScheme}-{creationMethod}"
    workflowId = lesson_id_cache.get(idEntry, str(uuid.uuid4()))
    lesson_id_cache[idEntry] = workflowId

    spd_title_addon = (f" @ {spds[0]}x" if len(spds) == 1 else '')
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
                        lesson=MiniLesson.construct_imr_preview(imr, speeds=[1.0, 0.5])
                    ),
                ] + [
                    WorkflowStep.with_lessonactivities(
                        imr=imr,
                        stepTitle=f'{title}' + (' @ {spd}x' if len(spds) > 1 else ''),
                        activities=[
                             MiniLessonActivity(
                                title=title,
                                startTime=startTime,
                                endTime=endTime,
                                practiceSpeed=spd,
                                showVideoControls=False,
                                startInstruction="Get ready to follow along!",
                                playingInstruction="Follow along!",
                                endInstruction="Try again as many times as you'd like!",
                            ),
                            MiniLessonActivity(
                                title=f'Record & Review',
                                startTime=startTime,
                                endTime=endTime,
                                practiceSpeed=spd,
                                showVideoControls=False,
                                userVisual='video',
                                demoVisual='skeleton' if showSkeleton else 'none',
                                startInstruction="Get ready to follow along! We'll record you so you can see how you did at the end",
                                playingInstruction="Follow along!",
                                endInstruction="Try again as many times as you'd like!",
                                reviewing=ReviewInfo(
                                    showModelSkeleton=showSkeleton,
                                    showUserSkeleton=False,
                                )
                            )
                        ]
                    )
                    for spd in spds
                    for title, startTime, endTime in 
                    chain(
                        [] if not segmentLesson else [(f'Part {i+1}' + (f': {seg.label}' if seg.label is not None else ''), seg.startTime, seg.endTime) for i, seg in enumerate(imr.temporalSegments)], 
                        [('Practice' if not segmentLesson else 'Full Practice', imr.startTime, imr.endTime)]
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
                        title=f'Performance ({int(speed * 100)}% speed)',
                        upload=WorkflowStepUploadData(
                            identifier=f'{imr.clipName}-{workflowId}-{int(speed*100)}spd',
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
                    for speed in (0.5, 1.0)
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
    