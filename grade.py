#! /usr/bin/env python3
"""
This script processes assignments downloaded from Blackboard.

The download from Blackboard contains:
- a .txt file for each student
- the files each student has submitted
Blackboard modifies all file names so that they include the student's id.

The script creates
1. FirstnameLastnameID.txt containing:
  - the student's code
  - the compiler's output for that code
  - any output produced by the code
2. A directory named for the student's ID (e.g. ab12345) containing all the files they submitted.

Arguments:
- in_dir: the directory you wish to process
- -o (optional): output directory; the default is dir.
- -a (optional): directory of files to be added student directories (e.g. external data).

"""
import argparse
import os
from pathlib import Path

from code_checking import Compiler
from feedback import SourceCode, CompilerOutput, CodeOutput, EmptyFeedbackSection
from processing import GradeBook


def main():
    """
    Main script for processing raw file download from Blackboard.

    Modify the list of feedback steps to change the format of the
    feedback files.

    You must specify an input file; the output file can be specified
    with the '-o' flag.

    Any external files needed for compilation (e.g. data files) must be
    present in the directory where this script is run.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("in_dir", type=str,
                        help="(relative path to) file containing Blackboard assignment download")
    parser.add_argument("-o", "--out_dir", type=str, help="output directory")
    args = parser.parse_args()

    in_path = Path.cwd() / args.in_dir
    if args.out_dir is None:
        out_path = in_path  # TODO default, make "processed" folder in parent dir of input dir
    else:
        out_path = Path.cwd() / args.out_dir
        os.makedirs(out_path, exist_ok=True)

    gb = GradeBook(in_path, out_path)
    gb.get_files_by_id()
    gb.make_folders()

    feedback_steps = [SourceCode(line_numbers=True),
                      CompilerOutput(shorten_file_paths=True),
                      CodeOutput(line_length=120),
                      EmptyFeedbackSection(),
                      ]

    gb.write_feedback(feedback_steps, compiler=Compiler(
        ['-Wall'], compiler_type='clang'))


if __name__ == "__main__":
    main()
