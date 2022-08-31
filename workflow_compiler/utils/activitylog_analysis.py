from io import StringIO, TextIOWrapper
from pathlib import Path
import re
import json
from dataclasses import dataclass, field
from typing import Final, Optional, Union
from dataclasses_json import dataclass_json
from dateutil import parser as dateparser
from datetime import datetime

from .workflow_condition_names import workflow_condition_names

USERSTUDY2_VALID_SUBJECTIDS = set(
    [str(i) for i in 
        [4545, 4432, 5172, 5796, 4163, 5799, 5803, 4941, 3975, 4953, 5806, 9960, 4707, 5811, 5815, 5123, 5820, 5819, 4402, 5829, 5828, 5830, 5831, 5816, 5832, 5834, 5480, 5857, 4291, 5701, 5718, 5898, 5824, 5904, 5905, 5836, 5887, 4814, 5180, 5933, 5946, 4701, 5590, 3609, 5982, 5985, 5986, 5878, 6817, 5833]
    ]
)

REGEX_START_WORKFLOW: Final[str] = r'(?:Starting workflow)\s([\w\-]+)\s\@\s([\d\.]+)x\ \-\ ([\w\d\-]+)[\n\r]'
REGEX_PARTICIPANT_ID: Final[str] = r'user(?:PARTICIPANTID)?(\d+)\-'

REGEX_STARTED_MINI_LESSON: Final[str] = r"(\d\d\d\d\-\d\d\-\d\dT\d\d\:\d\d\:\d\d\.\d\d\dZ): Started mini lesson \'(.+)\'"
REGEX_FINISHED_MINI_LESSON: Final[str] = r"(\d\d\d\d\-\d\d\-\d\dT\d\d\:\d\d\:\d\d\.\d\d\dZ): Finished mini lesson \'(.+)\'"
REGEX_ACTIVITY_PLAYBACK: Final[str] = r"(\d\d\d\d\-\d\d\-\d\dT\d\d\:\d\d\:\d\d\.\d\d\dZ): Starting playback of activity ([\w \d\.]+) at (\d+.\d+)[\n\r]+"
REGEX_RECORDING_STARTED: Final[str] = r"(\d\d\d\d\-\d\d\-\d\dT\d\d\:\d\d\:\d\d\.\d\d\dZ): Starting recording \'([\w\-\=\@\ \.]+)\'"
REGEX_RECORDING_STOPPED: Final[str] = r"(\d\d\d\d\-\d\d\-\d\dT\d\d\:\d\d\:\d\d\.\d\d\dZ): Stopped recording \'([\w\-\=\@\ \.]+)\'"
REGEX_LAST_LINE: Final[str] = r'(\d\d\d\d\-\d\d\-\d\dT\d\d\:\d\d\:\d\d\.\d\d\dZ): ([ \S]*)$'
REGEX_FIRST_LINE: Final[str] = r'^(\d\d\d\d\-\d\d\-\d\dT\d\d\:\d\d\:\d\d\.\d\d\dZ): ([ \S]*)'
REGEX_STAGE_EXPIRED: Final[str] = r"(\d\d\d\d\-\d\d\-\d\dT\d\d\:\d\d\:\d\d\.\d\d\dZ): Stage time expired '(.+)'"

@dataclass_json
@dataclass
class AnalyzedActivityLog:
    workflow_name: str = 'not_found'
    workflow_id: str = 'not_found'
    workflow_condition: str = 'unknown'
    participant_id: str = 'not_found'
    lesson_playbacks: dict = field(default_factory=dict)
    activity_playbacks: dict = field(default_factory=dict)
    activity_repeated_playbacks: dict = field(default_factory=dict)
    recordings_started = 0
    recordings_completed = 0
    idle_time_before_first_stage_expiration_secs: Union[None, float] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

    def parse_file(self, text: str):
        
        first_line_match = re.search(REGEX_FIRST_LINE, text)
        if first_line_match is not None:
            self.start_time = dateparser.parse(first_line_match.group(1))

        last_line_match = re.search(REGEX_LAST_LINE, text)
        if last_line_match is not None:
            self.end_time = dateparser.parse(last_line_match.group(1))

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

        stage_expired_match = re.search(REGEX_STAGE_EXPIRED, text)
        if stage_expired_match:
            expiration_datetime = dateparser.parse(stage_expired_match.group(1))
            prev_action = re.search(REGEX_LAST_LINE, text[:stage_expired_match.start()])
            prev_action_datetime = dateparser.parse(prev_action.group(1))
            self.idle_time_before_first_stage_expiration_secs = (expiration_datetime - prev_action_datetime).total_seconds()

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
                playback_start = activity_playback[2]
                activity_playback_key = f"{lesson_name}__{activity_name}__{playback_start}"
                
                self.lesson_playbacks[lesson_name] = self.lesson_playbacks.get(lesson_name, 0) + 1
                self.activity_playbacks[activity_playback_key] = self.activity_playbacks.get(activity_playback_key, 0) + 1
                    


def main():
    import argparse
    import csv

    parser = argparse.ArgumentParser()
    parser.add_argument('--dest-folder', type=str, required=True)
    parser.add_argument('input_files', nargs="*", metavar='activity logs', type=str, help='User activity logs generate a report of')
    parser.add_argument('--save_json', action='store_true', help='Save JSON Log Entries')
    args = parser.parse_args()

    dest_folder = Path(args.dest_folder)
    dest_folder.mkdir(parents=True, exist_ok=True)

    if len(args.input_files) == 1:
        path = Path(args.input_files[0])
        files = list(path.parent.glob(path.name))
        args.input_files = files

    playbacks_by_lesson = {}
    playbacks_by_activity = {}
    participants_by_workflow = {}

    files_by_user = {}

    skipped_files_count = 0
    processed_files_count = 0

    
    participant_csv = [
        ['study', 'dance', 'condition', 'lesson', 'activity_name', 'playback_start', 'participant_id', 'playbacks']
    ]

    skipped_files = []
    skipped_of_interest = []
    for i, log_filepath_str in enumerate(args.input_files):

        filename_partic_id = ""
        try:
            filename = log_filepath_str.stem
            filename_partic_id = filename.split("-")[0][-4:]
        except:
            pass
        
        print(f"Processing {i+1}/{len(args.input_files)}...")
        analyzed_log = AnalyzedActivityLog()
        log_contents = ''
        with open(log_filepath_str, 'r', encoding='utf-8') as f:
            log_contents = f.read()

        analyzed_log.parse_file(log_contents)
        # print(f"\tworkflow name: {analyzed_log.workflow_name}")
        # print(f"\tworkflow id: {analyzed_log.workflow_id}")

        if analyzed_log.participant_id not in USERSTUDY2_VALID_SUBJECTIDS:
            print(f"\t\tSkipping participant id {analyzed_log.participant_id} path={log_filepath_str.name}")
            skipped_files_count += 1
            skipped_files.append(log_filepath_str.name)

            if filename_partic_id in USERSTUDY2_VALID_SUBJECTIDS:
                skipped_of_interest.append((filename_partic_id, log_filepath_str.stem))
            continue

        if analyzed_log.participant_id != filename_partic_id:
            print(f"\t\tParticipant id {analyzed_log.participant_id} does not match filename {filename_partic_id}")
            skipped_files_count += 1
            continue


        files_by_user[analyzed_log.participant_id] = files_by_user.get(analyzed_log.participant_id, []) + [log_filepath_str.name]
        # print(f"\t\tProcessing {analyzed_log.participant_id}...")
        processed_files_count += 1
        participants_by_workflow[analyzed_log.workflow_condition] = participants_by_workflow.get(analyzed_log.workflow_condition, 0) + 1

        inpath = Path(log_filepath_str)
        outpath = dest_folder / f'{inpath.stem}.json'
        if analyzed_log.participant_id != 'not_found' and analyzed_log.workflow_condition != 'unknown':
            outpath = dest_folder / f'log-analysis__user{analyzed_log.participant_id}__{analyzed_log.workflow_condition}.json'

        # Add a placeholder entry, so that no participants get lost.

        study, dance, condition = analyzed_log.workflow_condition.split('-')

        participant_csv.append(
            [study, dance, condition, "info", "lesson-start", 0.00, analyzed_log.participant_id, 0]
        )

        if analyzed_log.idle_time_before_first_stage_expiration_secs is not None:
            participant_csv.append(
                [study, dance, condition, 'info', 'stage-expired-idle-time', analyzed_log.idle_time_before_first_stage_expiration_secs, analyzed_log.participant_id, 0]
            )
        
        start_time_str = 'unknown' if analyzed_log.start_time is None else analyzed_log.start_time.strftime('%x %X')
        participant_csv.append(
            [study, dance, condition, 'info', 'start_time', start_time_str, analyzed_log.participant_id, 0]
        )
        end_time_str = 'unknown' if analyzed_log.end_time is None else analyzed_log.end_time.strftime('%x %X')
        participant_csv.append(
            [study, dance, condition, 'info', 'end_time', end_time_str, analyzed_log.participant_id, 0]
        )

        for lesson, pb_count in analyzed_log.lesson_playbacks.items():
            key = analyzed_log.workflow_condition + '__' + lesson
            playbacks_by_lesson[key] = playbacks_by_lesson.get(key, 0) + pb_count

        for activity_key, pb_count in analyzed_log.activity_playbacks.items():
            key = analyzed_log.workflow_condition + '__' + activity_key
            playbacks_by_activity[key] = playbacks_by_activity.get(key, 0) + pb_count
            workflow_condition, lesson, activity_name, playback_start = key.split('__')
            #['study', 'dance', 'condition', 'lesson', 'activity_name', 'playback_start', 'participant_id', 'playbacks']
            participant_csv.append([
                study, dance, condition, lesson, activity_name, playback_start, analyzed_log.participant_id, pb_count
            ])
        

        if args.save_json:
            with open(str(outpath), 'w', encoding="utf-8") as f:
                json.dump(analyzed_log.to_dict(), f, indent=2)

    
    print("Writing CSV data: playbacks by lesson ...")
    playback_by_lesson_filepath = dest_folder / 'playbacks_by_lesson.csv'
    print(f"\t{playback_by_lesson_filepath!s}")
    with open(str(playback_by_lesson_filepath), 'w', encoding='utf-8', newline="") as f:
        writer = csv.writer(f)
        writer.writerow(['study', 'dance', 'condition', 'lesson', 'playbacks', 'participants'])
        for key, playback_count in playbacks_by_lesson.items():
            workflow_condition, lesson = key.split('__')

            study, dance, condition = workflow_condition.split('-')
            participants = participants_by_workflow.get(workflow_condition, 0)
            writer.writerow([study, dance, condition, lesson, playback_count, participants])


    print("Writing CSV data: playbacks by activity...")
    playback_by_activity_filepath = dest_folder / 'playbacks_by_activity.csv'
    print(f"\t{playback_by_activity_filepath!s}")
    with open(str(playback_by_activity_filepath), 'w', encoding='utf-8', newline="") as f:
        writer = csv.writer(f)
        writer.writerow(['study', 'dance', 'condition', 'lesson', 'activity_name', 'playback_start', 'playbacks', 'participants'])
        for key, playback_count in playbacks_by_activity.items():
            workflow_condition, lesson, activity_name, playback_start = key.split('__')
            study, dance, condition = workflow_condition.split('-')
            participants = participants_by_workflow.get(workflow_condition, 0)
            writer.writerow([study, dance, condition, lesson, activity_name, playback_start, playback_count, participants])

    print("Writing CSV data: participants...")
    participant_filepath = dest_folder / 'playback_count_by_participant.csv'
    print(f"\t{participant_filepath!s}")
    with open(str(participant_filepath), 'w', encoding='utf-8', newline="") as f:
        writer = csv.writer(f)
        for r in participant_csv:
            writer.writerow(r)
        

    print("Skipped files:", skipped_files_count)
    print("Processed files:", processed_files_count)
    print("Total files:", skipped_files_count + processed_files_count)

    # print()
    # print("Files by user")
    # sorted_users = sorted([int(i) for i in files_by_user.keys()])
    # for user in sorted_users:
    #     files = files_by_user[str(user)]
    #     print(f"\t{user}: {len(files)} files")
    #     for f in files:
    #         print(f"\t\t{user} - {f}")

if __name__ == "__main__":
    main()