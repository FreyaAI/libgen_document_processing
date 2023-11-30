import glob
import json
import os
import time
import argparse

from typing import List

from queue import Queue

from document import *
from process_parallelizer import DocumentProcessParallelizer


def read_filenames_from_directory(directory, mission_files_list=None):
    try:
        filenames = glob.glob(directory + "/*")

        if mission_files_list is not None:
            ## Filter out the files that are not in the mission files list but make the filteration that is basefilename without extension and without path
            filenames = [
                filename
                for filename in filenames
                if filename.split("\\")[-1].split(".")[0] in mission_files_list
            ]

        return filenames

    except Exception as e:
        print(f"Could not read filenames from directory {directory}")
        return None


def read_mission_files_list(path):
    try:
        with open(path, "r", encoding="utf-8") as file:
            data = json.load(file)

        return data

    except Exception as e:
        print(f"Could not read mission files list")
        return None


def makedirsifnotexists(path):
    if not os.path.exists(path):
        os.makedirs(path)


def parse_args():
    parser = argparse.ArgumentParser(description="Process some integers.")
    parser.add_argument(
        "--source_dir",
        type=str,
        required=True,
        help="Source directory",
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        default="output",
        help="Output directory",
    )
    parser.add_argument(
        "--mission_files_list",
        type=str,
        default="mission_files_list.json",
        help="Mission files list",
    )
    parser.add_argument(
        "--batch_count",
        type=int,
        default=10,
        help="Batch count",
    )

    args = parser.parse_args()

    return args


def main(args):
    start_time = time.time()

    SOURCE_DIRECTORY = args.source_dir  # "C:\Workzone\Datasets\TurkishBooksSample"
    OUTPUT_DIRECTORY = args.output_dir  # "output"
    MISSION_FILES_LIST_PATH = args.mission_files_list  # "mission_files_list.json"
    BATCH_COUNT = args.batch_count  # 10

    makedirsifnotexists(OUTPUT_DIRECTORY)

    mission_files_list = read_mission_files_list(MISSION_FILES_LIST_PATH)

    filenames = read_filenames_from_directory(SOURCE_DIRECTORY, mission_files_list)
    print(f"Found {len(filenames)} files")

    if filenames is None or len(filenames) == 0:
        print("No files found, exiting")
        return

    filename_batches = [filenames[i::BATCH_COUNT] for i in range(BATCH_COUNT)]

    print(
        f"Cumulative length of batches: {sum([len(batch) for batch in filename_batches])}"
    )

    del filenames

    for i, batch in enumerate(filename_batches):
        print(f"Processing batch {i+1} of {BATCH_COUNT}")
        parallelizer = DocumentProcessParallelizer(OUTPUT_DIRECTORY)

        parallelizer.process(batch)

        del parallelizer

    print(f"Done in {time.time() - start_time} seconds")


if __name__ == "__main__":
    args = parse_args()
    main(args)
