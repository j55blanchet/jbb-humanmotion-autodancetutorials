import json
import os
import sys
from pathlib import Path
from ..datatypes.IMR import IMR
from .current_lesson_compiler import create_simple_lesson
# from .legacy_lesson_compiler import create_legacy_lesson
from ..datatypes import CustomSerializable
from .isls_2022_lessons import create_isls2022_lesson
from .control_lessons import create_control_lesson
from .simple_speedstep import create_simple_speedstepped_lesson

if __name__ == "__main__":
    imr_dir = Path(sys.argv[1])
    output_dir = Path(sys.argv[2])
    lesson_id_cache_path = Path(sys.argv[3])

    lesson_id_cache = {}
    if lesson_id_cache_path.exists():
        with open(lesson_id_cache_path, 'r') as f:
            lesson_id_cache = json.load(f)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    imr_files = list(imr_dir.rglob('*.[i][m][r].[j][s][o][n]'))
    out_lesson_files = [
        (
            output_dir.joinpath(
                imr_path.relative_to(imr_dir).parent, 
                imr_path.stem.replace('.imr', '') + '.workflow.json'
            ),
            output_dir.joinpath(
                imr_path.relative_to(imr_dir).parent, 
                imr_path.stem.replace('.imr', '') + '-simple.workflow.json'
            )
        )
        for imr_path in imr_files
    ]
    combined_output_path = output_dir.joinpath('all_workflows.json')

    all_lessons = []
    for i in range(len(imr_files)):
        imr_filepath = imr_files[i]
        out_lesson_file = out_lesson_files[i][0]
        out_lesson_file_simple = out_lesson_files[i][1]
        imr = None
        with open(imr_filepath, "r", encoding='utf-8') as imrfile:
            imr = IMR.from_json(json.load(imrfile))

        # lesson = create_lesson(imr)
        isls2022_lesson_nosheetmotion = create_isls2022_lesson(imr, useSheetMotion=False, lessonIdCache=lesson_id_cache)
        isls2022_lesson_sheetmotion = create_isls2022_lesson(imr, useSheetMotion=True, lessonIdCache=lesson_id_cache)
        # simple_lesson_sheetmusic = create_simple_lesson(imr, useSheetMotion=True, lessonIdCache=lesson_id_cache)
        # simple_lesson_nosheetmusic = create_simple_lesson(imr, useSheetMotion=False, lessonIdCache=lesson_id_cache)
        # current_lesson = create_simple_lesson(imr, lessonIdCache=lesson_id_cache)
        # control_lesson = create_control_lesson(imr, lesson_id_cache=lesson_id_cache)
        unsegmented_noskeleton_speedstep_lesson = create_simple_speedstepped_lesson(imr, lesson_id_cache=lesson_id_cache, showSkeleton=False, segmentLesson=False, spds=[0.5])
        unsegmented_skeleton_speedstep_lesson = create_simple_speedstepped_lesson(imr, lesson_id_cache=lesson_id_cache, showSkeleton=True, segmentLesson=False, spds=[0.5])
        segmented_noskeleton_speedstep_lesson = create_simple_speedstepped_lesson(imr, lesson_id_cache=lesson_id_cache, showSkeleton=False, segmentLesson=True, spds=[0.5])
        segmented_skeleton_speedstep_lesson = create_simple_speedstepped_lesson(imr, lesson_id_cache=lesson_id_cache, showSkeleton=True, segmentLesson=True, spds=[0.5])

        out_lesson_file.parent.mkdir(exist_ok=True, parents=True)
        out_lesson_file_simple.parent.mkdir(exist_ok=True, parents=True)

        new_lessons = [ 
            isls2022_lesson_nosheetmotion,
            isls2022_lesson_sheetmotion,
            # unsegmented_noskeleton_speedstep_lesson,
            # unsegmented_skeleton_speedstep_lesson,
            # segmented_noskeleton_speedstep_lesson,
            # segmented_skeleton_speedstep_lesson,
            # current_lesson,
            # control_lesson,
        ]
        all_lessons.extend(new_lessons)

        print(f"Created {len(new_lessons)} new lessons for {imr_filepath}")
        # with open(out_lesson_file, "w", encoding='utf-8') as lessonfile:
            # lesson.write_json(lessonfile, indent=2)
        # with open(out_lesson_file_simple, 'w', encoding='utf-8') as simple_lessonfile:
            # simple_lesson.write_json(simple_lessonfile, indent=2)            

        # print("Created complex lesson at ", out_lesson_file.resolve().as_posix())
        # print("Created simple  lesson at ", out_lesson_file_simple.resolve().as_posix())
    
    
    print('Writing combined lesson output at ' + str(combined_output_path))
    with open(combined_output_path, 'w', encoding='utf-8') as combined_output_file:
        CustomSerializable.write_json_native(all_lessons, combined_output_file, indent=None)

    print('Writing lesson cache at ' + str(lesson_id_cache_path))
    with open(lesson_id_cache_path, 'w') as f:
        json.dump(lesson_id_cache, f, indent=2)