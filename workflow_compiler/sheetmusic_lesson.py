import uuid

from .MiniLesson import *
from .IMR import IMR
from .Workflow import *

def create_sheetmusic_lesson(imr: IMR) -> Workflow:

    workflow = Workflow(
        title=f"""{imr.title} - Sheet Music""",
        id=str(uuid.uuid4()),
        creationMethod=f'SheetMusicCompiler ({imr.generationMethod})',
    )

    workflow.stages.append(
        WorkflowStage(
            title='Preview',
            steps=[
            ]
        ),
    )

    return workflow