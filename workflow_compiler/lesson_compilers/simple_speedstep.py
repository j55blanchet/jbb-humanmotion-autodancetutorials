
from datetime import timedelta
from ..datatypes.Workflow import *
from ..datatypes import Instructions
from typing import *

def create_simple_speedstepped_lesson(imr: IMR, lesson_id_cache: Dict[str, str], showSkeleton: bool):

    compilationMethod = 'SimpleSpeedStep' + ('(Skeleton)' if showSkeleton else '')
    idEntry = f"{imr.clipName}-{compilationMethod}"
    workflowId = lesson_id_cache.get(idEntry, str(uuid.uuid4()))
    lesson_id_cache[idEntry] = workflowId

    return Workflow(
        title=f"{imr.clipName} (SpeedStep)" + (' (Skeleton)' if showSkeleton else ''),
        userTitle=f'Learning: "{imr.clipTitle}"',
        id=workflowId,
        creationMethod=compilationMethod,
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
                        lesson=MiniLesson.construct_imr_preview(imr, speeds=[1, 0.5])
                    ),
                ] + [
                    WorkflowStep.with_lessonactivities(
                        imr=imr,
                        stepTitle=f'Practice @ {spd}x',
                        activities=[
                             MiniLessonActivity(
                                title=f'Practice',
                                startTime=imr.startTime,
                                endTime=imr.endTime,
                                practiceSpeed=spd,
                                showVideoControls=False,
                                startInstruction="Get ready to follow along!",
                                playingInstruction="Follow along!",
                                endInstruction="Try again as many times as you'd like!",
                            ),
                            MiniLessonActivity(
                                title=f'Record & Review',
                                startTime=imr.startTime,
                                endTime=imr.endTime,
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
                    for spd in [0.5, 0.75, 1]
                    # for i, seg in enumerate(imr.temporalSegments)
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
    