"""
Creates feedback .txt file.
"""
import re
from code_checking import Executor

def make_header(header_text, size=None):
    """
    make_header Return a string padded by
    newlines:

    ==============
    header_text
    ==============

    Args:
        header_text (str): header text
        size (int, optional): number of = signs. Defaults to None.
    """
    if size:
        line = "\n" + (size * "=") + "\n"
    else:
        line = "\n" + ((len(str(header_text)) + 2) * "=") + "\n"
    return "\n" + line + str(header_text) + line + "\n"

class FeedBackStep():
    """
    FeedBackStep: base class for writing different
    types of feedback to student feedback files.
    """
    def __init__(self, header_text=None) -> None:
        if header_text:
            self.header = make_header(header_text)
        else:
            self.header = "\n"

    def __call__(self, writer, code_file) -> None:
        """
        __call__ writes header to writer.

        Args:
            writer (writer object): open writer for student feedback file.
            code_file (CodeFile object): student code data type
        """
        writer.write(self.header)

class SourceCode(FeedBackStep):
    """
    SourceCode: FeedBackStep to print source code.

    """
    def __init__(self, header_text=None, line_numbers=True) -> None:
        """
        __init__ Create SourceCode object

        Args:
            header_text (str, optional): Text to write as header. Defaults to None.
            line_numbers (bool, optional): Print line numbers. Defaults to True.
        """
        super().__init__(header_text)
        self.line_numbers = line_numbers

    def __call__(self, writer, code_file) -> None:
        """
        __call__ Write source code in file to writer object.

        Args:
            writer (writer object): write to open file.
            code_file (CodeFile): CodeFile object.
        """
        file = code_file.file_path
        writer.write(make_header(str(file.name)))
        with open(file, 'rt', encoding='utf-8') as f:
            try:
                if self.line_numbers:
                    for n, line in enumerate(f.readlines()):
                        writer.write(f"{n+1:<3} {line}")
                else:
                    for line in f.readlines():
                        writer.write(line)
            except UnicodeDecodeError as e:
                print(f"Can't read {str(file)}: {e}")

def shorten_file_paths(s):
    pat = re.compile(r'/\w+/\w+/Dropbox/teaching/cpp-R-2022/marking/\w+/\w+/\w+/[\w-]+_')
    return re.sub(pat, "", s)

class CompilerOutput(FeedBackStep):
    """
    CompilerOutput: FeedBackStep to write compiler messages.

    """
    def __init__(self, header_text="GCC output", error_parser=None, shorten_file_paths=False) -> None:
        super().__init__(header_text)
        self.shorten_file_paths = shorten_file_paths
        if error_parser:
            self.error_parser = error_parser
        else:
            self.error_parser = lambda x: x

    def __call__(self, writer, code_file) -> None:
        """
        __call__ Writes code_file.stderr to writer.

        Args:
            writer (writer object): writes to student feedback file.
            code_file (CodeFile object): contains code data.
                If code_file hasn't been compiled, then stderr will
                be the empty string.

        """
        super().__call__(writer, code_file)
        try:
            if shorten_file_paths:
                writer.write(self.error_parser(shorten_file_paths(code_file.stderr)))
            else:
                writer.write(self.error_parser(code_file.stderr))
        except UnicodeDecodeError as e:
            print(f"Unicode error in stderr of {str(code_file.file_path)[-20:]}: {e}")


class CodeOutput(FeedBackStep):
    """
    CodeOutput: FeedBackStep to write the output (if any)
    of a student program.
    
    """
    def __init__(self,
                 header_text="Program output",
                 line_limit=50,
                 line_length=200,
                 executor=Executor()) -> None:
        super().__init__(header_text)
        self.line_limit = line_limit
        self.line_length = line_length
        self.executor = executor

    def __call__(self, writer, code_file) -> None:
        super().__call__(writer, code_file)
        output = code_file.get_output_as_string(self.executor)
        output_lines = [line[:self.line_length] for line in output.splitlines()]

        if self.line_limit:
            if output.count("\n") > self.line_limit:
                output_truncated = "\n".join(output_lines[:self.line_limit])
                writer.write(output_truncated)
                writer.write(f"\n\n(Output truncated at {self.line_limit} lines.)\n\n")
            else:
                writer.write("\n".join(output_lines))
        else:
            writer.write("\n".join(output_lines))

class EmptyFeedbackSection(FeedBackStep):
    """
    EmptyFeedbackSection: prints Feedback header and nothing else.

    """
    def __init__(self, header_text="Feedback") -> None:
        super().__init__(header_text)


class KNNFeedbackSection(FeedBackStep):
    """
    KNNFeedbackSection: feedback for second coursework on kNN
    """
    def __init__(self, header_text="Feedback") -> None:
        super().__init__(header_text)

    def __call__(self, writer, code_file) -> None:
        super().__call__(writer, code_file)

        # output check
        if code_file.exit_code == 0:
            not1_count = code_file.get_output_as_string().lower().count("not 1")
            if not1_count == 83:
                writer.write("Your code predicts that 17 of the images are the number one, which is the correct output for 5-NN on this data.")
            elif not1_count == 0:
                writer.write("Your code doesn't make any predictions.")
            else:
                writer.write(f"Your code predicts that {100 - not1_count} of the images are the number one, which is incorrect. On this data, 5-NN should predict that 17 images are the number one.")
            writer.write("\n")


        # error checking
        if code_file.exit_code == 0:
            if code_file.stderr:
                writer.write("Your code compiles, but there are some warnings from the compiler.")
            else:
                writer.write("Your code compiles without warnings.")
        else:
            print(f"Non-zero exit code in {str(code_file.file_path)[-20:]}")
            if code_file.stderr:
                writer.write("Your code doesn't compile. The compiler messages explain some of the issues with your code.")
            else:
                writer.write("Your code doesn't compile. Unfortunately, the compiler doesn't seem to have any feedback.")
