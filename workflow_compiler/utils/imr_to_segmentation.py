

import json
from pathlib import Path
from ..datatypes.IMR import IMR
import argparse

import sys


def create_segmentation(imr: IMR):
    return [s.startTime for s in imr.temporalSegments] + [imr.temporalSegments[-1].endTime]


if __name__ == "__main__":
    print(sys.argv)
    parser = argparse.ArgumentParser()
    parser.add_argument('--dest-file', metavar='destination file', type=str, default='./segmentations.json')
    parser.add_argument('input_files', nargs="*", metavar='imr inputs', type=str, help='IMR File[s] to generation segmentations for')
    args = parser.parse_args()

    segmentations_dict = {}
    for imr_filepath in args.input_files:
        with open(imr_filepath, 'r', encoding='utf-8') as imr_file:
            imr = IMR.from_json(json.load(imr_file))
            segmentations_dict[f'{imr.clipName}-{imr.generationMethod}'] = create_segmentation(imr)

    with open(args.dest_file, 'w', encoding='utf-8') as dest_file:
        json.dump(segmentations_dict, dest_file, indent=2)