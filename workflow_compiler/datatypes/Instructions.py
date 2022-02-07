from datetime import timedelta
from enum import Enum, auto, unique
import inspect

from .Workflow import WorkflowStepExperimentData, WorkflowStepInstructions, WorkflowStep

@unique
class InstructionPosition(Enum):
    LEARNING_INTRODUCTION = auto()
    LEARNING_PREPERFORMANCE = auto()
    SINGLE_STAGE_INTRODUCTION = auto()
    SINGLE_STAGE_PREPERFORMANCE = auto()
    MASTERY_INTRODUCTION = auto()
    MASTERY_PREPERFORMANCE = auto()

@unique
class WorkflowType(Enum):
    CONTROL = auto()
    SIMPLE_SEGMENTED = auto()
    CURRENT_MERGED = auto()
    LEGACY_SKELETON = auto()
    LEGACY_SHEETMOTION = auto()

    def welcome_instruction(self):
        if self == WorkflowType.CONTROL:
            return "In this trial, you're going to have full control over how you learn the video. Use the on screen controls to seek different parts of the video."
        elif self == WorkflowType.SIMPLE_SEGMENTED:
            return "In this trial, the dance has been divided into a few parts for you to practice. Feel free to practice the parts in any order you like. \n\nA few practice speeds are available to you. We recommend learning the dance at a slow speed at first before practicing at higher speeds."
        elif self == WorkflowType.CURRENT_MERGED:
            return "In this trial, you're be guided though learning the dance one part at a time. While learning each part you'll first see a demo of the dance segment, then an activity to practice & memorize the moves, then a chance to try the part from memory, and last an activity to integrate the part with the rest of the song you've already learned."
        elif self == WorkflowType.LEGACY_SKELETON:
            return "In this trial, you're be guided though learning the dance one part at a time. While learning each part you'll first see a demo of the dance segment, then an activity to practice & memorize the moves, then a chance to try the part from memory, and last an activity to integrate the part with the rest of the song you've already learned."
        elif self == WorkflowType.LEGACY_SHEETMOTION:
            return "In this trial, you're be guided though learning the dance one part at a time. While learning each part you'll first see a demo of the dance segment, followed by a breakdown of the individual dance moves, then an activity to practice & memorize the moves using sheet motion, then a chance to try the part from memory, and last an activity to integrate the part with the rest of the song you've already learned."
        else:
            raise Exception(f"Unknown WorkflowType {self}")

def td_format(td_object: timedelta) -> str:
    seconds = int(td_object.total_seconds())
    periods = [
        ('year',        60*60*24*365),
        ('month',       60*60*24*30),
        ('day',         60*60*24),
        ('hour',        60*60),
        ('minute',      60),
        ('second',      1)
    ]

    strings=[]
    for period_name, period_seconds in periods:
        if seconds > period_seconds:
            period_value , seconds = divmod(seconds, period_seconds)
            has_s = 's' if period_value > 1 else ''
            strings.append("%s %s%s" % (period_value, period_name, has_s))

    return ", ".join(strings)

def generate_instructionstep(dance_title: str, position: InstructionPosition, type: WorkflowType, time_alloted: timedelta = None) -> WorkflowStep:
    
    time_alloted_str = ""
    if time_alloted is not None:
        time_alloted_str = td_format(time_alloted)

    stepTitle = {
        InstructionPosition.LEARNING_INTRODUCTION: "Trial Instructions",
        InstructionPosition.LEARNING_PREPERFORMANCE: "CheckIn Performance Instructions",
        InstructionPosition.SINGLE_STAGE_INTRODUCTION: "How to use this app",
        InstructionPosition.SINGLE_STAGE_PREPERFORMANCE: "Recording & uploading your performance",
        InstructionPosition.MASTERY_INTRODUCTION: "Mastery Introduction",
        InstructionPosition.MASTERY_PREPERFORMANCE: "Final Performance Instructions"
    }[position]

    text_dict = {
        InstructionPosition.SINGLE_STAGE_INTRODUCTION: inspect.cleandoc(f"""Welcome!

        In this app, you're going to learn the dance "{dance_title}".

        First, you'll have {time_alloted_str} to learn the dance. Try your best to memorize and become as fluent and confident with the dance as you can.

        {type.welcome_instruction()}

        After that, you'll record a video of you performing the dance.
        
        Remember, we are rewarding participants who put in great effort to learn the dances. So try your best!

        When you're ready, close this dialog and click 'Begin'!
        """),

        InstructionPosition.SINGLE_STAGE_PREPERFORMANCE: inspect.cleandoc(f"""Congrats on your progress learning the dance!

        Now, we ask you to share what you've learned with us by recording two videos of you performing the dance. 
        - For the first recording, the music will play at half speed. This will help us observe your memorization of the dance.
        - For the second recording, the music will be played at full speed. This will help us observe your fluency with the dance.

        Don't worry if you aren't perfect or struggle with the dance. Do you're best and show us what you've learned so far!
        
        PLEASE MAKE SURE THAT YOU ARE IN THE VIDEO FRAME AND THAT MUSIC IS AUDIBLE IN THE RECORDINGS. Please take headphones off and play the music through speakers so that it comes through in the recording.

        If a glitch happens or you're not happy with your initial recordings, you'll have one opportunity to re-record.
        """),

        InstructionPosition.LEARNING_INTRODUCTION: inspect.cleandoc(f"""Welcome! 
        
        In this trial, you're going to be learning the dance "{dance_title}". 

        The trial is divided into two phases. 
        - During the learning phase, the video will be slowed down so that you can learn and memorize the dance moves. 
        - During the mastery phase, the video will be sped up to allow you to master your moves.

        {type.welcome_instruction()}

        At the end of the learning phase, you'll be asked to record a video of you performing the dance. You'll be able to hear the music, but won't see the video during this performance. We want to see how much you can learn in the time allotted, so do your best!

        You'll have {time_alloted_str} to practice in this learning phase. Try to memorize the dance as best you can in this time. Feel free to skip around and practice whatever part of the dance you need to.

        Remember, we are rewarding participants who put in great effort to learn the dances. So try your best!

        When you're ready, close this dialog and click 'Begin'!
        """),

        InstructionPosition.LEARNING_PREPERFORMANCE: inspect.cleandoc(f"""Congrats on the progress you've made!

        Now, we ask you to share that progress with us by recording two videos of you performing the dance. 
        - For the first recording, the music will play at the same speed you've been learning it at (half speed). 
        - For the second recording, as a real challenge, the music will be played at full speed.

        Don't worry if you aren't perfect or struggle with the dance the full speed. Do you're best and show us what you've learned so far!
        
        PLEASE MAKE SURE THAT YOU ARE IN THE VIDEO FRAME AND THAT MUSIC IS AUDIBLE IN THE RECORDINGS. Please take headphones off and play the music through speakers so that it comes through in the recording.

        If a glitch happens or you're not happy with your initial recordings, you'll have one opportunity to re-record.
        """),

        InstructionPosition.MASTERY_INTRODUCTION: inspect.cleandoc(f"""Now it's time to refine that dance some more!

        In this phase, you'll practice the dance at faster speeds. Try to get as confident and precise as you can regarding the dance moves, and feel free to skip around to practice at whatever pace will help you the most. 

         You'll have {time_alloted_str} to practice in this mastery phase. Once this phase is over, you'll be asked to record a final performance at full speed. 

        When you're ready, close this dialog and click 'Begin'!
        """),

        InstructionPosition.MASTERY_PREPERFORMANCE: inspect.cleandoc(f"""Congrats on completing the mastery phase!

        Hopefully you were able to polish your moves and are feeling confident and beautiful. 

        We're excited to see what you've learned! The final performance will be just like before. 

        As a reminder, please ensure that you are in the video frame and that the music is audible in the recordings (again, take any headphones off and play the music through speakers).

        Good luck!
        """)
    }
    
    text = text_dict[position]
    

    return WorkflowStep.with_instructions(
        stepTitle=stepTitle,
        heading=stepTitle,
        text=text,
        experiment=WorkflowStepExperimentData(
            showInExperimentOnly=True,
            isBeforeTimeStartTask=position in [InstructionPosition.LEARNING_INTRODUCTION, InstructionPosition.MASTERY_INTRODUCTION],
            isTimeExpiredTask=position in [InstructionPosition.LEARNING_PREPERFORMANCE, InstructionPosition.MASTERY_PREPERFORMANCE],
        ),
    )