# Grading Scripts for Algorithms and Programming in C++ and R

Downloading assignments from Blackboard gives you a folder with all files submitted by all students,
with metadata prepended to file names.

The scripts organize the files, run the code, and put the output into "feedback" .txt files.
These .txt files have a section for feedback at the end; fill this section with comments.
Once you've finished reviewing the students' code, you can email the feedback to them.

Grades and feedback are not submitted to Blackboard, so this process is only suitable
for formative assessment, although you can upload grades in addition to emailing the feedback.

# Scripts

- `grade.py`: takes an assignment download from Blackboard and...
  - creates a directory for each student containing the files they submitted
  - compiles/runs all source files in each student directory
  - writes source code, compiler output, and program output to a .txt feedback file for each student
- `email_grades.py`: emails the content of each feedback.txt file to the corresponding student
- `get_grades.sh`: move the last "gradebook" download from Blackboard to a specified directory (not particularly robust)

# Future plans

- Log feedback send via email (which students submitted work, etc)
- Deal with .Rmd files
