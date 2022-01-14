from typing import List
import uuid
import datetime
import math
from ..datatypes.IMR import IMR, Motion, TemporalSegment
from ..datatypes.MiniLesson import ActivityPause, MiniLesson, MiniLessonActivity, TimedInstruction, MotionLessonHeader
from ..datatypes.Workflow import Workflow, WorkflowStage, WorkflowStepUploadData, WorkflowStep, WorkflowStepActivityReference

def get_preposition(index, max_index):
    if index == 0 and max_index > 0:
        return "First "
    if index > 0 and index == max_index:
        return "Finally,"
    return "Now "

def get_focused_segments(focusStart: float, focusEnd: float, segmentBreaks: List[float]):

    startI = 0
    while startI < len(segmentBreaks) and focusStart > segmentBreaks[startI]:
        startI += 1

    endI = startI
    while endI < len(segmentBreaks) and focusEnd > segmentBreaks[endI]:
        endI += 1

    return list(range(startI, endI + 1))

def create_embeddedminilesson_workflowstep(imr: IMR, title: str, activities: List[MiniLessonActivity]) -> WorkflowStep:
    return WorkflowStep(
        type="MiniLessonEmbedded",
        title=title,
        miniLessonEmbedded=MiniLesson(
            segmentBreaks=imr.get_segment_breaks(),
            clipName=imr.clipName,
            lessonTitle=title,
            activities=activities,
        )
    )

def create_dance_preview(imr: IMR) -> WorkflowStage:

    small_timeframe = 0.01
    lessons = []

    activity = MiniLessonActivity(
            title="Dance Segment Preview",
            startTime=imr.startTime,
            endTime=imr.endTime,
            focusedSegments=[0],
            practiceSpeed=1,
            startInstruction="Here's the dance you'll be learning..."          
        )

    lessons.extend([
        MiniLesson(
            lessonTitle='Entire Dance',
            clipName=imr.clipName,
            segmentBreaks=imr.get_segment_nobreaks(),
            activities=[activity]
        )
    ])
    
    if len(imr.temporalSegments) > 1:
        activity = MiniLessonActivity(
            title="Part Preview",
            startTime=imr.startTime-small_timeframe,
            endTime=imr.endTime,
            focusedSegments=list(range(len(imr.temporalSegments))),
            practiceSpeed=1,
            pauses=[
                ActivityPause(time=seg.startTime, pauseDuration=0.5) 
                for seg in imr.temporalSegments[1:]
            ],
            startInstruction=f"You'll learn this dance in {len(imr.temporalSegments)} parts",
            timedInstructions=[  
                TimedInstruction(
                    seg.startTime, 
                    seg.endTime,
                    f"Part {i+1}"
                )
                for i, seg in enumerate(imr.temporalSegments)
            ],
            # endInstruction="Ready to learn first part of the dance?"
        )
        lessons.extend([
            MiniLesson(
                lessonTitle='Preview By Parts',
                clipName=imr.clipName,
                segmentBreaks=imr.get_segment_breaks(),
                activities=[activity]
            )
        ])
        
    return WorkflowStage(
        title="Preview",
        steps=[
            WorkflowStep(
                type="MiniLessonEmbedded",
                title=lesson.header.lessonTitle,
                miniLessonEmbedded=lesson) for lesson in lessons
        ],
    )

def create_singlemotion_segment_steps(imr: IMR, segments: List[TemporalSegment], segment_i: int, practice_speed: float) -> List[WorkflowStep]:
    temporalSegment = segments[segment_i]
    # motion = temporalSegment.motions[0]

    return [create_embeddedminilesson_workflowstep(
        imr=imr,
        title=f"Learn Segment {segment_i + 1}",
        activities=[
            MiniLessonActivity(
                    title=f"Segment {segment_i + 1}, (Complete, single move)",
                    startTime=temporalSegment.startTime,
                    endTime=temporalSegment.endTime,
                    focusedSegments=[segment_i],
                    practiceSpeed=practice_speed,
                    startInstruction=f"Segment #{segment_i + 1} is short. Try it!",
                    playingInstruction="Follow along...",
                    timedInstructions=[],
                    endInstruction="Next you'll try without the video"
                ),
            MiniLessonActivity(
                    title=f"Segment {segment_i + 1}, (Complete, single move, novideo, 25%)",
                    startTime=temporalSegment.startTime,
                    endTime=temporalSegment.endTime,
                    focusedSegments=[segment_i],
                    practiceSpeed=0.25,
                    userVisual=MiniLessonActivity.VisualType.VIDEO,
                    demoVisual=MiniLessonActivity.VisualType.SKELETON,
                    # emphasizedJoints=motion.emphasis,
                    startInstruction=f"Now try it without the video (slowly)",
                    playingInstruction="Follow along...",
                    timedInstructions=[],
                    endInstruction="Next you'll try a little faster"
                ),
            MiniLessonActivity(
                    title=f"Segment {segment_i + 1}, (Complete, single move, novideo, 50%)",
                    startTime=temporalSegment.startTime,
                    endTime=temporalSegment.endTime,
                    focusedSegments=[segment_i],
                    practiceSpeed=0.5,
                    userVisual=MiniLessonActivity.VisualType.VIDEO,
                    demoVisual=MiniLessonActivity.VisualType.SKELETON,
                    # emphasizedJoints=motion.emphasis,
                    startInstruction=f"Now try it without the video, a bit faster",
                    playingInstruction="Follow along...",
                    timedInstructions=[]
                )
        ]
    )]

def create_multimotion_segment_steps(imr: IMR, segments: List[TemporalSegment], segment_i: int, practice_speed: float) -> List[WorkflowStep]:
    activities = []
    temporalSegment = segments[segment_i]
    segment_count = len(segments)

    steps: List[WorkflowStep] = []

    # Temporal Segment Preview
    steps.append(create_embeddedminilesson_workflowstep(
        imr=imr,
        title=f"Segment {segment_i+1} Preview",
        activities=[MiniLessonActivity(
            title=f"Segment {segment_i+1} Preview",
            startTime=temporalSegment.startTime,
            endTime=temporalSegment.endTime,
            startInstruction=f"{get_preposition(segment_i, segment_count)}we're going to learn segment {segment_i+1}. ({len(temporalSegment.motions)} moves)",
            timedInstructions=[
                TimedInstruction(
                    startTime=motion.startTime,
                    endTime=motion.endTime,
                    text=f"Dance Move #{motion_i+1}"
                )
                for motion_i, motion in enumerate(temporalSegment.motions)
            ],
            pauses=[ActivityPause(time=motion.startTime) for motion in temporalSegment.motions],
            focusedSegments=[segment_i],
            practiceSpeed=practice_speed
        )]
    ))

    # Individual Motion Learning
    activities = []
    for motion_i, motion in enumerate(temporalSegment.motions):   
        
        is_last = motion_i + 1 == len(temporalSegment.motions)

        activity = MiniLessonActivity(
            title=f"Segment {segment_i + 1}, Move {motion_i + 1}",
            startTime=motion.startTime,
            endTime=motion.endTime,
            focusedSegments=[segment_i],
            practiceSpeed=practice_speed,
            startInstruction=f"Let's practice move #{motion_i + 1} in this segment",
            timedInstructions=[],
            endInstruction=f"Next: practicing these {motion_i + 1} moves together" if is_last else f"Next: move {motion_i + 1}"
        )
        activities.append(activity)

    steps.append(create_embeddedminilesson_workflowstep(
        imr=imr,
        title=f"Move Learning",
        activities=activities
    ))
    
    # Temporal Segment Integration
    steps.append(create_embeddedminilesson_workflowstep(
        imr=imr,
        title=f"Dance Move Integration",
        activities=[MiniLessonActivity(
            title=f"Segment {segment_i + 1}, Integration",
            startTime=temporalSegment.startTime,
            endTime=temporalSegment.endTime,
            startInstruction="Now practice these moves together",
            practiceSpeed=practice_speed,
            focusedSegments=[segment_i],
            endInstruction="Next you'll try without the video"
        )]
    ))

    steps.append(create_embeddedminilesson_workflowstep(
        imr=imr,
        title=f"Practice without Video",
        activities=[MiniLessonActivity(
            title=f"Segment {segment_i + 1}, Integration (practice wo skeleton, slow)",
            startTime=temporalSegment.startTime,
            endTime=temporalSegment.endTime,
            focusedSegments=[segment_i],
            practiceSpeed=0.25,
            userVisual=MiniLessonActivity.VisualType.VIDEO,
            demoVisual=MiniLessonActivity.VisualType.SKELETON,
            # emphasizedJoints=motion.emphasis,
            startInstruction=f"Now try it without the video (slowly)",
            playingInstruction="Follow along...",
            timedInstructions=[],
            endInstruction="Next you'll try a little faster"
        )]
    ))
    
    return steps

def create_segment_learning_steps(imr: IMR, segments: List[TemporalSegment], segment_i: int, speed: float) -> List[WorkflowStep]:
    if len(segments[segment_i].motions) <= 1:
        return create_singlemotion_segment_steps(imr, segments, segment_i, practice_speed=speed)
    else:
        return create_multimotion_segment_steps(imr, segments, segment_i, practice_speed=speed)    

def create_muiltisegment_integration(imr: IMR, segments: List[TemporalSegment], start_i: int, end_i: int, speed: float) -> List[WorkflowStep]:
    return [create_embeddedminilesson_workflowstep(
        imr=imr,
        title=f"Segment {start_i+1}-{end_i+1} integration",
        activities=[MiniLessonActivity(
            title=f"Segment {start_i+1}-{end_i+1} integration",
            startTime=segments[start_i].startTime,
            endTime=segments[end_i].endTime,
            practiceSpeed=speed,
            startInstruction=f"Practice doing segments {start_i+1} - {end_i+1} together",
            focusedSegments=list(range(start_i, end_i+1))
        )]
    )]

def create_dance_review(imr: IMR) -> List[WorkflowStep]:

    speeds = [0.5, 0.6, 0.75, 0.85, 1.0]

    return [
        
        create_embeddedminilesson_workflowstep(
            imr=imr,
            title=f"Review @ {int(speed * 100)}%",
            activities=[
                MiniLessonActivity(
                    title=f"Review @ {int(speed * 100)}",
                    startTime=imr.startTime,
                    endTime=imr.endTime,
                    practiceSpeed=speed,
                    startInstruction= f"Let's try the whole dance at {int(speed * 100)}% speed" if i == 0 else 
                                    f"Now try it at {int(speed * 100)}%",
                    endInstruction=   f"Next we'll try it without video",
                    focusedSegments=list(range(len(imr.temporalSegments)))
                ),
                MiniLessonActivity(
                    title=f"Without Video @ {int(speed * 100)}",
                    startTime=imr.startTime,
                    endTime=imr.endTime,
                    practiceSpeed=speed,
                    startInstruction= f"Now try it without the video%",
                    endInstruction=   f"Next we'll try it at {int(speeds[i+1]*100)}%" if i + 1 < len(speeds) else None,
                    userVisual=MiniLessonActivity.VisualType.VIDEO,
                    demoVisual=MiniLessonActivity.VisualType.SKELETON,
                    focusedSegments=list(range(len(imr.temporalSegments)))
                )
            ]
        )
        
         for i, speed in enumerate(speeds)]

def create_legacy_lesson(imr: IMR) -> Workflow:

    learning_speed = 0.5

    workflow = Workflow(
        title=imr.clipName,
        id=str(uuid.uuid4()),
        creationMethod=f'Complex ({imr.generationMethod})')

    # # Start with a preview of the dance
    workflow.stages.append(create_dance_preview(imr))
    # activities: List[MiniLessonActivity] = create_dance_preview(imr)

    # # Learn & integrate segments chronologically
    segment_count = len(imr.temporalSegments)
    for segment_i in range(segment_count):
        segment_stage = WorkflowStage(title=f"Segment {segment_i + 1}")
        segment_stage.steps.extend(create_segment_learning_steps(imr, imr.temporalSegments, segment_i, [learning_speed]))

        # Integrate with prior two segments
        if segment_i > 0:
            integration_start = max(0, segment_i - 2)
            segment_stage.steps.extend(create_muiltisegment_integration(imr, imr.temporalSegments, integration_start, segment_i, [learning_speed]))
        
        workflow.stages.append(segment_stage)

    # # End with a review of the dance
    review_stage = WorkflowStage(title="Review")
    review_stage.steps.extend(create_dance_review(imr))
    
    workflow.stages.append(review_stage)

    return workflow
    # return MiniLesson(
    #     _id=str(uuid.uuid4()),
    #     header=MotionLessonHeader(
    #         clipName=imr.clipName,
    #         lessonTitle="AutoGenerated Lesson " + timestring
    #     ),
    #     segmentBreaks=segmentBreaks,
    #     activities=activities,
    #     fps=imr.fps,
    #     landmarkScope=imr.landmarkScope,
    # )