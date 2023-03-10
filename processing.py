"""
Extract and organize student files downloaded from Blackboard.
"""
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import zipfile

from code_checking import Compiler, Executor

def get_id(file):
    """
    get_id Try to extract student ID from Blackboard
    file name. Return "noid" if no ID found.

    Args:
        file (Path-like): path to file.

    Returns:
        str: Student ID or "noid" if none found.
    """
    id_pat = re.compile(r'[a-z]{2}[0-9]{5}')
    match =  id_pat.search(file.stem)
    if match:
        return match.group(0)
    else:
        return "noid"

def remove_filename_whitespace(dir_path):
    """
    for all files in dir, replace all whitespace
    in the file name with underscores

    dir - Path object
    """
    pat = re.compile(r'\s')
    for file in dir_path.glob('*.*'):
        s = file.name
        t = pat.sub('_', s)
        os.rename(file, file.parent / t)

class GradeBook():
    """
    Generate and hold a list of Student objects.

    """
    def __init__(self, in_dir=Path.cwd(), out_dir=None, file_types=None) -> None:
        self.in_dir = in_dir
        self.out_dir = out_dir
        if file_types:
            self.file_types = file_types
        else:
            self.file_types = [".c", ".cpp"]
        self.student_dict = {}
        remove_filename_whitespace(self.in_dir)

    def get_files_by_id(self):
        """
        get_files_by_id

        Populate student_dict by iterating over files in in_dir.

        When a new student ID is encountered, it is used as the
        key for a new student object.
        Files are appended to the file list of a Student object
        with ID matching that found in the file.

        """
        files = list(self.in_dir.glob('*.*'))
        for file in files:
            file_id = get_id(file)
            try:
                self.student_dict[file_id].add_file(file)
            except KeyError:
                self.student_dict[file_id] = Student(file_id)
                self.student_dict[file_id].add_file(file)

    def make_folders(self):
        for student in self.student_dict.values():
            student.make_folder(self.out_dir, file_types=self.file_types)

    def write_feedback(self, feedback_steps, compiler=Compiler()):
        for student in self.student_dict.values():
            write_name = student.first + student.last + student.student_id + ".txt"
            print(f'Writing file {write_name}')
            with open(self.out_dir / write_name, "w", encoding='utf-8') as f:
                f.write(f"*** homework for {student.first} {student.last} ({student.student_id}) ***\n\n")
                f.write("\nThis report contains all C code you submitted, warnings and errors from the compiler (if any), program output (if your code compiled), followed by feedback.\n\n")

                for suffix in self.file_types:
                    for file in student.dir.glob("*" + suffix):
                        try:
                            code = CodeFile(file)
                        except ValueError:
                            continue
                        else:
                            code.compile(compiler)
                            for step in feedback_steps:
                                step(f, code)


# Helper functions for Student class
def get_name(file):
    """
    Extract student's first and last name from Blackboard .txt file.
    """
    pat = re.compile(r"([A-Z][a-z]+)\s+([A-Z][a-z]+)")
    with open(file, 'rt', encoding='utf-8') as f:
        line = f.readline()
    name = pat.search(line)
    if name:
        return name.groups()
    else:
        return "", ""

def make_dir_name(path, student_id):
    """
    make_dir_name make a directory path for Student folder

    Args:
        path (Path object): path to parent directory.
        student_id (string): student's id (e.g. self.student_id)

    Returns:
        Path object: path to student's folder.
    """
    return path / student_id

def get_suffix(file_string):
    """get the suffix from a string of the form filename.suffix"""
    pattern = re.compile(r"\.[A-Za-z]*$")
    match = pattern.search(file_string)
    if match:
        return match.group(0)
    return None

def move_to_top(dir_, file_types):
    """
    move all .c files in file tree of "dir" into dir itself.

    dir - Path object
    file_types - list of file suffixes
    """
    for dirpath, _, files in os.walk(dir_):
        if dirpath != str(dir_):
            for file in files:
                filepath = os.path.join(dirpath, file)
                if get_suffix(file) in file_types:
                    try:
                        shutil.move(str(filepath), str(dir_))
                    except FileExistsError:
                        print(f"A file named {file} already exists in {dir_}. \
                            Could not copy.")
                        # TODO find way to add suffix based on hash of file name
                        # try:
                        #     new_filepath = add_random_suffix_to_file(dir, file)
                        #     shutil.move(str(filepath), new_filepath)
                        # except shutil.Error as e:
                        #     pass
                    except shutil.Error as e:
                        print(e)
                        print(f"Couldn't move file {file}.")


def extract_file(file, extract_to=None):
    """
    extract a .zip, .7z, or .rar file to current directory,
    or to a directory specified by extract_to

    file - Path like object to compressed file
    extract_to - string, name of directory to extract file to
    """
    if extract_to:
        new_dir = extract_to
        os.makedirs(new_dir, exist_ok=True)
    else:
        new_dir = file.parent

    if file.suffix == ".zip":
        zip_file = zipfile.ZipFile(file)
        zip_file.extractall(new_dir)
    elif sys.platform == "darwin" and file.suffix == ".rar":
        try:
            subprocess.run(['unrar', 'x', str(file), str(new_dir)], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Process {e.cmd} exited with code {e.returncode}: {e.stderr}")
    else:
        try:
            subprocess.run(['7z', 'e', str(file), '-o' + str(new_dir)], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Process {e.cmd} exited with code {e.returncode}: {e.stderr}")
            print(f"Couldn't extract file {str(file)}.")

class Student():
    """
    Student: Stores student data.
    """
    def __init__(self, student_id):
        self.student_id = student_id
        self.first = ""
        self.last = ""
        self.file_list = None
        self.dir = None

    def add_file(self, file_path):
        """Add a file to the Student's file list.

        Args:
            file_path (Path-like): path to a file belonging to the student
        """
        if self.file_list:
            self.file_list.append(file_path)
        else:
            self.file_list = [file_path]



    def make_folder(self, output_path, file_types=None):
        """Make a folder containing the files belonging to a student.

        Args:
            output_path (Path-like): path to directory where student folders will be stored.
         file_types (list, optional): list of file type suffixes; these files will be moved to
                the top level of the student's folder so that they can be found for compilation.
                Defaults to [".c"].
        """
        # make a new folder for each student
        self.dir = make_dir_name(output_path, self.student_id)
        os.makedirs(self.dir, exist_ok=True)

        if not file_types:
            file_types = [".c", ".cpp"]

        for file in self.file_list:
            # try to get first and last name from blackboard .txt file
            if file.suffix == ".txt":
                self.first, self.last = get_name(file)
                shutil.copy(str(file), str(self.dir))
            # move files from file_types to student folder
            elif file.suffix in file_types:
                shutil.copy(str(file), str(self.dir))
            # try to extract any other files to student folder
            else:
                try:
                    extract_file(file, self.dir / file.stem)
                    shutil.copy(str(file), str(self.dir))
                except OSError:
                    print(f"Could not extract file {str(file)}.\
                        Compressed file copied to student directory.")
                    shutil.copy(str(file), str(self.dir))

        move_to_top(self.dir, file_types) # move to top, in case extracted files nested



class CodeFile():
    """
    CodeFile Stores path to code, allows compilation,
    and stores path of executable, as well as error messages.
    """
    def __init__(self, file_path):
        """
        __init__ Create CodeFile object from file with
        path file_path.

        Args:
            file_path (Path-like): path to code file.
        """
        if file_path.is_file():
            self.file_path = file_path
        else:
            raise ValueError(f"{file_path} is not a file.")
        self.exit_code = None
        self.stderr = ""
        self.output_file = None
        self.output_text = ""

    def compile(self, compiler):
        """
        compile Compile the code at self.file_path and
        capture exit_code and stderr (if applicable).

        Args:
            compiler (Compiler object): Compiler object that
            takes file_path and output_file as arguments.

        """
        if self.output_file is None:
            self.output_file = self.file_path.parent / (self.file_path.stem + ".out")
        self.exit_code, self.stderr = compiler(self.file_path, self.output_file)


    def get_output_as_string(self, exectutor=Executor()):
        """
        get_output_as_string Run code and return output
        as a string.

        Args:
            exectutor (Executor object): Executor object
            to run the code. Defaults to Executor with
            default options.

        """
        if self.output_text:
            return self.output_text
        elif self.exit_code == 0:
            self.output_text = exectutor(self.output_file)
            return self.output_text
        else:
            return "Code did not compile."
