# Nicholas Christophides  Nicholas.christophides@stonybrook.edu

"""
EDITS THU June 26th:

NICK CHRISTOPHIDES---------------
    Added more format recognition in order to discard unwanted lines. Variables named "discard_pattern#" where # is an
    integer are used to recognize lines that we don't want to save from the questions.

    Variable "in_answer" is an indicator variable that is True when the current line is part of an answer. This is
    to deal with answers that span multiple lines. As long as in_answer is True, the program will skip over all lines
    until the next question is found.

EDITS FRI June 27th:

NICK CHRISTOPHIDES---------------
    Adding more specificity to the exercise pattern fixed the bug where many exercises were being left out. It was done
    by making the space after the question number optional since some questions had the space and others didn't.

    Adding an alternative exercise pattern accounted for other, less common, exercise formats (4.8 (a)...).

    Adding a pattern to recognize data tables allowed the confusion of exercises and data points to be eliminated.

    In doing these steps, every question is read and stored once and only once. Now further analysis may be completed.

    Added a menu feature for easy viewing purposes. Allows for viewing specific questions, or all questions.

STILL NEEDS:
-Categorize questions into proofs or calculations.
    -An idea of how to do this is to search each question for the words "proof", "prove", or "show". If the words is
    present, then it should be added to the Proof array. If the words aren't present, then it should be added to the
    Calculation array.
        -This will need troubleshooting and a manual review. More likely than not this is not a perfect strategy and
        will require human correction. However, this strategy will be quicker than searching each question manually.

LOOKING AHEAD:
NICK CHRISTOPHIDES--------------
    A current limitation of this program is that the PdfReader does not read statistical symbols properly (summations,
    greek letters, limits, etc...). In order to fix this, it is proposed we use an OCR tool to feed the PdfReader a
    plain text file with symbols turned into LaTeX or some other readable form.
    Some spacing issues are also present. Hopefully the OCR will fix this.
    This will be time-consuming. I have already tried to work with this a little, but was not able to find a quick or
    simple way to work with this. If anyone else in the project has experience with OCR tools and can give advice or
    contribute to the writing of the code, it may be beneficial.
"""

# 1. Extract all exercises from a book
from PyPDF2 import PdfReader
import re

reader = PdfReader("2001_stat_infer.pdf")  # Read the textbook

exercise_pattern = re.compile(r"^\s*(\d+\.\d+)(?![\da-z.,()])")  # Questions match this format
exercise_pattern_alt = re.compile(r"^\s*(\d+\.\d+)\s*\(([a-z])\)")  # Questions also match this format
data_table_pattern = re.compile(r"^\s*\d+\.\d+\s+\d+\.\d+")  # Recognizes data tables

discard_pattern1 = re.compile(r"^Section\s+\d+\.\d+\s+[A-Z ]+\s+\d+$")  # Header format, want to discard
discard_pattern2 = re.compile(r"^\d+\s+[A-Z ]+\s+Section\s+\d+\.\d+$")  # Other header format, want to discard
discard_pattern3 = re.compile(r"^\(Answers?:")  # Answer format, want to discard
discard_pattern4 = re.compile(r"^\s*(\d+\.\d+)\s*(Exercises|Miscellanea)\b")  # Another header format, want to discard
discard_pattern5 = re.compile(r"^\s*(Copyright|Editorial)")  # Copyright Statements, want to discard


exercises = []  # Stores the exercises as tuples
exercise_labels = []  # <--- This stores just the exercise numbers
current_label = None  # Variable to save the exercise number
current_lines = []  # Used in creating each question, stores each line of the question
in_answer = False  # Indicator variable for when current line is part of an (unwanted) answer

for page in reader.pages:  # Iterate through each page in the book
    text = page.extract_text()
    if not text:
        continue

    lines = text.splitlines()  # Separate each line
    for line in lines:  # Iterate through each line
        stripped = line.strip()  # Remove starting and trailing whitespaces

        if stripped[0:8] == "11.12(b)" or stripped[0:6] == "5.8(b)":  # Singular cases, easier to deal with separately
            continue

        # If the line matches the form of the exercise, the proper variable is initialized
        match = exercise_pattern.match(stripped)
        match_alt = exercise_pattern_alt.match(stripped)
        data_match = data_table_pattern.match(stripped)

        # If the line should be discarded, the proper variable is initialized
        discard1 = discard_pattern1.match(stripped)
        discard2 = discard_pattern2.match(stripped)
        discard3 = discard_pattern3.match(stripped)
        discard4 = discard_pattern4.match(stripped)
        discard5 = discard_pattern5.match(stripped)

        # Handles answers spanning multiple lines. When in_answer is true, we discard the line
        if in_answer == True and not match:
            continue

        elif discard1 or discard2 or discard4 or discard5:  # Line is an unwanted header or footer, skip it
            continue

        elif discard3:  # Line is an unwanted answer
            in_answer = True  # Change in_answer to True to skip to next exercise
            continue

        elif data_match:  # Line contains data, want to input it without considering it a question
            current_lines.append(stripped)
            continue

        # If the line matches either exercise format, this block is executed
        elif match or match_alt:
            in_answer = False
            # Save the previous exercise
            if current_label is not None:
                exercises.append((current_label, "\n".join(current_lines)))
                exercise_labels.append(current_label)

            # Start a new exercise
            if match:
                current_label = match.group(1)
            elif match_alt:
                current_label = match_alt.group(1)

            current_lines = [stripped]

        elif current_label is not None:
            current_lines.append(stripped)

# Save the last exercise
if current_label is not None:
    exercises.append((current_label, "\n".join(current_lines)))
    exercise_labels.append(current_label)

# Print list of exercise labels. Visual proof each question is accounted for
print("\nAll exercise labels:")
current_chapter = ''
for label in exercise_labels:
    chapter = label.split(".")[0]
    if chapter != current_chapter:
        print("\n")
        current_chapter = chapter
    print(label, end=" ")

# Show total number of exercises
print(f"\nNumber of Exercises:", len(exercise_labels))

# Print a particular exercise, or see all exercises
target = ""
while target.lower() != "q":

    target = input("\nEnter 'E' to View a Specific Exercise\nEnter 'Q' to Quit:\nEnter 'A' to See All Questions\n\n ")

    if target.lower() == 'a':
        for label, content in exercises:
            print(f"\n=== Exercise {label} ===")
            print(content)

    elif target.lower() == 'e':
        target = input("\nEnter Exercise Number to View: ")
        for label, content in exercises:
            if label == target:
                print(f"\n=== Exercise {label} ===")
                print(content)
                break
        print(f"Exercise {target} not found.")

    elif target.lower() == 'q':
        break
