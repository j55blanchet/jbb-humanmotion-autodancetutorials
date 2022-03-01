
import argparse
import signal
import librosa
import numpy as np
# Intersting Links:
#   > https://stackoverflow.com/questions/25394937/automatically-sync-two-audio-recordings-in-python
#   > https://github.com/Algomorph/cvcalib
#   > sync/

def find_audio_offset(src_file: str, within_file: str, window: int):
    """Find the location of one audio file within another

    Args:
        src_file (str): The audio signal to search for
        within_file (str): The file in which to search for the src audio
        window (int): How many seconds to compare

    Returns:
        float: The offset in seconds between audio from the first file to the second
    """
    # from: https://dev.to/hiisi13/find-an-audio-within-another-audio-in-10-lines-of-python-1866

    y_within, sr_within = librosa.load(within_file, sr=None)
    y_find, _ = librosa.load(src_file, sr=sr_within)

    c = signal.correlate(y_within, y_find[:sr_within*window], mode='valid', method='fft')
    peak = np.argmax(c)
    offset = round(peak / sr_within, 2)
    
    return offset

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--find-offset-of', metavar='audio file', type=str, help='Find the offset of file')
    parser.add_argument('--within', metavar='audio file', type=str, help='Within file')
    parser.add_argument('--window', metavar='seconds', type=int, default=10, help='Only use first n seconds of a target audio')
    args = parser.parse_args()
    offset = find_audio_offset(args.within, args.find_offset_of, args.window)
    print(f"Offset: {offset}s" )


if __name__ == '__main__':
    main()