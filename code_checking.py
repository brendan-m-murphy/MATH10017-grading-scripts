"""
This module provides classes that act as hooks for
method in the CodeFile class.

"""
from pathlib import Path
import subprocess

class Compiler():
    """
    Compiler: compile C or C++ code using gcc or clang.

    Used as a hook for CodeFile.compile.
    """
    def __init__(self, *args,
                 compiler_type='gnu',
                 suppress_main_return_warn=True,
                 max_errors=10) -> None:
        """
        __init__ Create Compiler object.

        Args:
            compiler_type (str, optional): type of compiler_type to use,
            either 'gnu' or 'clang'. Defaults to 'gnu'.

            suppress_main_return_warn (bool, optional): suppress
            main-return-type warnings if True.

            max_errors (int, optional): maximum number of errors
            before aborting compilation. Set to -1 for all errors.

            *args (str): additional compiler_type flags may be passed.
        """
        if compiler_type in ['gnu', 'clang']:
            self.compiler_type = compiler_type
        else:
            raise ValueError("compiler_type must be 'gnu' or 'clang'")
        self.flags = list(*args)

        if compiler_type == 'gnu':
            self.flags.append("-lm")
            if max_errors >= 0:
                self.flags.append("-fmax-errors=" + str(max_errors))
            if suppress_main_return_warn:
                self.flags.append("-Wno-main")
        else:
            if max_errors >= 0:
                self.flags.append("-ferror-limit=" + str(max_errors))
            if suppress_main_return_warn:
                self.flags.append("-Wno-main-return-type")

    def __call__(self, in_file, out_file=Path.cwd() / "a.out"):
        """
        __call__ Compiles code in in_file to executable out_file
        and returns exit code and stderr.

        Checks the extension of in_file to decide whether to use
        gcc or gpp.

        For either choice of compiler_type ('gnu' or 'clang'), it is
        assumed that 'gcc' (or 'gpp') is an alias for the compiler.

        Args:
            in_file (Path-like): path to .c or .cpp file to compile
            out_file (Path-like): path to executable output. Defaults
            to "a.out" in current working directory.

        Returns:
            (int, str): exit code and stderr output
        """
        if in_file.suffix == '.c':
            compiler_str = "gcc"
        elif in_file.suffix == '.cpp':
            compiler_str = "g++"
        else:
            raise ValueError("File type not .c or .cpp")

        commands = [compiler_str, str(in_file), "-o", str(out_file)] + self.flags

        try:
            sp = subprocess.run(commands, capture_output=True, text=True, check=True) #, encoding='iso-8859-1')
        except subprocess.CalledProcessError as e:
            #print(f"Process {e.cmd} exited with code {e.returncode}: {e.stderr}")
            return e.returncode, e.stderr
        except UnicodeDecodeError as e:
            print(f"Unicode decode error in {in_file}: {e}")
            return 1, "Unicode error, no compiler output recorded."
        else:
            return sp.returncode, sp.stderr


class Executor():
    """
    Executor: run code and return output.

    Used as hook for CodeFile.get_output_as_string.
    """
    def __init__(self) -> None:
        pass

    def __call__(self, file_path, timeout=5) -> str:
        try:
            sp = subprocess.run([str(file_path)], capture_output=True,
                                text=True,# encoding='iso-8859-1',
                                timeout=timeout, check=True)
        except subprocess.TimeoutExpired:
            return f"Timed out: execution took more than {timeout} seconds."
        except subprocess.CalledProcessError as e:
            print(f"Process {e.cmd} exited with code {e.returncode}: {e.stderr}.")
            return "Couldn't run file."
        else:
            return sp.stdout


class ErrorParser():
    """
    ErrorParser: parses stderr created by compiler.
    """


class OutputParser():
    """
    OutputParser: parses file output
    """
