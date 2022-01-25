from pathlib import Path
import subprocess
import sys

def extract_audio(video_path: Path, relative_path: Path, audio_dir: Path):
    audio_path = relative_path.parent.joinpath(relative_path.stem + '.wav')
    audio_path = audio_dir.joinpath(audio_path)
    audio_path.parent.mkdir(exist_ok=True, parents=True)

    if audio_path.exists():
        return audio_path

    print(f'Creating audio for {audio_path}')
    import subprocess
    command = f'ffmpeg -i "{str(video_path)}" -ab 160k -ac 1 -ar 44100 -vn {str(audio_path)} -y'
    proc = subprocess.Popen(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    result = proc.wait()
    if result != 0:
        output = proc.stderr.readlines()[-1].decode('utf-8')
        print(f'Unable to create audio for {relative_path}: {output}')
        return None

    return audio_path

def trim_video(video_path: Path, out_filepath: Path, startTimeSecs: float, endTimeSecs: float):
    # Example:
    # Start & End Time
    #   ffmpeg -i input.mp4 -ss 1:19:27 -to 02:18:51 -c:v copy -c:a copy output.mp4
    # Fixed Duration
    #   ffmpeg -i input.mp4 -ss 00:01:10 -t 00:01:05 -c:v copy -c:a copy output.mp4


    # Reencoding:
    # ffmpeg -i input.mp4 -ss 00:00:15 -t 00:00:10 -async -1 clip.mp4

    # Another option, using trim filter (from 10sec to 25sec)
    # ffmpeg -i my_video.mp4 -vf trim=10:25,setpts=PTS-STARTPTS clip.mp4

    command = f'ffmpeg -ss 00:00:{startTimeSecs} -i "{str(video_path)}" -to 00:00:{endTimeSecs} -async -1 "{str(out_filepath)}"'
    proc = subprocess.Popen(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    result = proc.wait()
    if result != 0:
        output = proc.stderr.readlines()[-1].decode('utf-8')
        print(f'Unable to create clip for {video_path} from {startTimeSecs} to {endTimeSecs}: {output}', file=sys.stderr)
    
    