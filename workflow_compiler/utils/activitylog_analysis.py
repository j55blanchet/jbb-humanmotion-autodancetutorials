from io import TextIOWrapper
from pathlib import Path
import re
import json
from dataclasses import dataclass, field
from typing import Final
from dataclasses_json import dataclass_json

from .workflow_condition_names import workflow_condition_names

REGEX_START_WORKFLOW: Final[str] = r'(?:Starting workflow)\s([\w\-]+)\s\@\s([\d\.]+)x\ \-\ ([\w\d\-]+)[\n\r]'
REGEX_PARTICIPANT_ID: Final[str] = r'user(?:PARTICIPANTID)?(\d+)\-'
REGEX_STARTED_MINI_LESSON: Final[str] = r"(\d\d\d\d\-\d\d\-\d\dT\d\d\:\d\d\:\d\d\.\d\d\dZ): Started mini lesson \'([\w\@\ \.]+)\'"
REGEX_FINISHED_MINI_LESSON: Final[str] = r"(\d\d\d\d\-\d\d\-\d\dT\d\d\:\d\d\:\d\d\.\d\d\dZ): Finished mini lesson \'([\w\@\ \.]+)\'"
REGEX_ACTIVITY_PLAYBACK: Final[str] = r"(\d\d\d\d\-\d\d\-\d\dT\d\d\:\d\d\:\d\d\.\d\d\dZ): Starting playback of activity ([\w \d\.]+)[\n\r]+"
REGEX_RECORDING_STARTED: Final[str] = r"(\d\d\d\d\-\d\d\-\d\dT\d\d\:\d\d\:\d\d\.\d\d\dZ): Starting recording \'([\w\-\=\@\ \.]+)\'"
REGEX_RECORDING_STOPPED: Final[str] = r"(\d\d\d\d\-\d\d\-\d\dT\d\d\:\d\d\:\d\d\.\d\d\dZ): Stopped recording \'([\w\-\=\@\ \.]+)\'"
REGEX_LAST_LINE: Final[str] = r'(\d\d\d\d\-\d\d\-\d\dT\d\d\:\d\d\:\d\d\.\d\d\dZ): ([ \S]*)$'

@dataclass_json
@dataclass
class AnalyzedActivityLog:
    workflow_name: str = 'not_found'
    workflow_id: str = 'not_found'
    workflow_condition: str = 'unknown'
    participant_id: str = 'not_found'
    lesson_playbacks: dict = field(default_factory=dict)
    activity_playbacks: dict = field(default_factory=dict)
    recordings_started = 0
    recordings_completed = 0

    def parse_file(self, text: str):
        
        last_line_match = re.search(REGEX_LAST_LINE, text)

        # Metadata - find workflow name and workflow id
        start_workflow_match = re.search(REGEX_START_WORKFLOW, text)
        if start_workflow_match is not None:
            self.workflow_name, _, self.workflow_id = start_workflow_match.groups()
            self.workflow_condition = workflow_condition_names[self.workflow_id]

        # Metadata - find participant ID
        participant_id_match = re.search(REGEX_PARTICIPANT_ID, text)
        if participant_id_match is not None:
            self.participant_id = participant_id_match.group(1)

        # Count recordings
        self.recordings_started = len(re.findall(REGEX_RECORDING_STARTED, text))
        self.recordings_completed = len(re.findall(REGEX_RECORDING_STOPPED, text))

        # Start going through mini lessons in the log. Try to match start and finish lesson events.
        minilesson_start_matches = [m for m in re.finditer(REGEX_STARTED_MINI_LESSON, text)]
        minilesson_end_matches = [m for m in re.finditer(REGEX_FINISHED_MINI_LESSON, text)]
        minilesson_endmatch_pairs = []
        next_end_match_index = 0
        for i, start_match in enumerate(minilesson_start_matches):
            next_start_match = minilesson_start_matches[i+1] if i+1 < len(minilesson_start_matches) else last_line_match
            hopeful_end_match = minilesson_end_matches[next_end_match_index] if next_end_match_index < len (minilesson_end_matches) else last_line_match

            # Avoid edge case if finish lesson is before start lesson 
            while hopeful_end_match.start() < start_match.end():
                next_end_match_index += 1
                hopeful_end_match = minilesson_end_matches[next_end_match_index] if next_end_match_index < len (minilesson_end_matches) else last_line_match
                if next_end_match_index >= len (minilesson_end_matches):
                    break
            
            # Sometimes finish lesson can be missing - if so, end at start of next lesson
            if next_start_match.start() < hopeful_end_match.start():
                minilesson_endmatch_pairs.append(next_start_match)
            # (ideal case) - finish lesson is after start lesson
            else:
                minilesson_endmatch_pairs.append(hopeful_end_match)
                next_end_match_index += 1

        # Aggregate mini-lesson statistics
        match_pairs = list(zip(minilesson_start_matches, minilesson_endmatch_pairs))
        for i, (lessonstart_match, lessonend_match) in enumerate(match_pairs):
            lesson_name = lessonstart_match.group(2)
            
            # Count playbacks, grouped by lesson and lesson-activity
            for activity_playback in re.findall(REGEX_ACTIVITY_PLAYBACK, text[lessonstart_match.end():lessonend_match.start()]):    
                activity_name = activity_playback[1]
                activity_playback_key = f"{lesson_name}__{activity_name}"
                
                self.lesson_playbacks[lesson_name] = self.lesson_playbacks.get(lesson_name, 0) + 1
                self.activity_playbacks[activity_playback_key] = self.activity_playbacks.get(activity_playback_key, 0) + 1
                    


def main():
    import argparse
    import csv

    parser = argparse.ArgumentParser()
    parser.add_argument('--dest-folder', type=str, required=True)
    parser.add_argument('input_files', nargs="*", metavar='activity logs', type=str, help='User activity logs generate a report of')
    args = parser.parse_args()

    dest_folder = Path(args.dest_folder)
    dest_folder.mkdir(parents=True, exist_ok=True)

    if len(args.input_files) == 1:
        path = Path(args.input_files[0])
        files = list(path.parent.glob(path.name))
        args.input_files = files

    playbacks_by_lesson = {}
    playbacks_by_activity = {}

    for i, log_filepath_str in enumerate(args.input_files):

        print(f"Processing {i+1}/{len(args.input_files)}...")
        analyzed_log = AnalyzedActivityLog()
        log_contents = ''
        with open(log_filepath_str, 'r') as f:
            log_contents = f.read()

        analyzed_log.parse_file(log_contents)
        print(f"\tworkflow name: {analyzed_log.workflow_name}")
        print(f"\tworkflow id: {analyzed_log.workflow_id}")

        inpath = Path(log_filepath_str)

        outpath = dest_folder / f'{inpath.stem}.json'
        if analyzed_log.participant_id != 'not_found' and analyzed_log.workflow_condition != 'unknown':
            outpath = dest_folder / f'log-analysis__user{analyzed_log.participant_id}__{analyzed_log.workflow_condition}.json'

        for lesson, pb_count in analyzed_log.lesson_playbacks.items():
            key = analyzed_log.workflow_condition + '__' + lesson
            playbacks_by_lesson[key] = playbacks_by_lesson.get(key, 0) + pb_count
        
        for activity_key, pb_count in analyzed_log.activity_playbacks.items():
            key = analyzed_log.workflow_condition + '__' + activity_key
            playbacks_by_activity[key] = playbacks_by_activity.get(key, 0) + pb_count

        with open(str(outpath), 'w') as f:
            json.dump(analyzed_log.to_dict(), f, indent=2)

    
    print("Writing CSV data: playbacks by lesson ...")
    with open(str(dest_folder / 'playback_count_by_lesson.csv'), 'w') as f:
        writer = csv.writer(f)
        writer.writerow(['workflow_condition', 'lesson', 'playbacks'])
        for key, value in playbacks_by_lesson.items():
            condition, lesson = key.split('__')
            writer.writerow([condition, lesson, value])


    print("Writing CSV data: playbacks by activity...")
    with open(str(dest_folder / 'playback_count_by_lessonactivity.csv'), 'w') as f:
        writer = csv.writer(f)
        writer.writerow(['workflow_condition', 'lesson', 'activity', 'playbacks'])
        for key, value in playbacks_by_activity.items():
            condition, lesson, activity = key.split('__')
            writer.writerow([condition, lesson, activity, value])

if __name__ == "__main__":
    main()