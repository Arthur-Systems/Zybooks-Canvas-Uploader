# Canvas Grade Uploader

This tool is designed to apply student grades and late penilities for specific assignments in Canvas. It automates the process of fetching submissions, applying penalties, and updating grades based on input from a CSV file containing student scores. The tool can be run using either command-line arguments or interactively for ease of use.

## Features

- Automatically fetches student submissions and applies late penalties for assignments.
- Supports grade updates from a CSV file using `zyphraser`.
- Customizable late penalties, with an override for specific conditions.
- Handles authentication via a config file or command-line arguments.
- Interactive mode when command-line arguments are not provided.
- Provides detailed logging for submission failures or grade mismatches.

## Requirements

- Python 3.x
- Libraries:
  - `pyfiglet`
  - `argparse`
  - `requests`

You can install the required dependencies using:

```bash
pip install -r requirements.txt
```

## Usage

###  Sanatize CSV File
Please use `Name_Fix/gradeMuge.v3.py` to sanitize the CSV file before using this tool. Students name sometimes does not match the name in Canvas. This tool will help you to fix the name issue.

To run the tool, refer to the PDF file in the `Name_Fix` folder.

I modified the original code so it now only takes -z (zybooks file) and -c (canvas file) as arguments. 

```bash

python gradeMuge.v3.py -z zybooks.csv -c canvas.csv

```

### Canvas API Access Token

To get the Canvas API access token, follow these steps:

[API Token](https://community.canvaslms.com/t5/Canvas-Basics-Guide/How-do-I-manage-API-access-tokens-in-my-user-account/ta-p/615312)

### Course ID

To get the course ID, follow these steps:

[Course ID](https://13kb.helpscoutdocs.com/article/551-how-to-locate-canvas-course-and-section-id)


### Config File (`config.json`)

RECOMMENDED: Provide access token and course ID via a `config.json` file:

```json
{
  "access_token": "your_canvas_access_token",
  "course_id": "your_course_id"
}
```

This is so you don't have to provide the access token and course ID as command-line arguments every time you run the script.

### Interactive Mode

I recommend everyone to use this mode. If the required command-line arguments are not provided, the tool will prompt for input interactively:

```bash
python publish.py
```

### Command-line Arguments

You can run the script using command-line arguments for non-interactive execution. Required arguments include the Canvas API access token, course ID, assignment name, and CSV file.

Example usage:

```bash
python canvas_late_penalty.py --access_token <your_token> --course_id <your_course_id> <assignment_name> <csv_file_path>
```

#### Arguments:
- `--access_token`: The API token for Canvas (required).
- `--course_id`: The ID of the course in Canvas (required).
- `assignment_name`: The name of the assignment to update grades for (required).
- `csv_file_path`: The path to the CSV file containing student grades (required).

If a `config.json` file is available in the project directory, the tool will use the token and course ID from the file unless they are provided as command-line arguments.


The script will ask you to input the assignment name and the path to the CSV file containing grades.

### Example CSV File

The CSV file should have the following structure:

| Student Last Name | Student First Name | Assignment to be graded in points |
|-------------------|--------------------|-------|
| Doe               | John               | 85    |
| Smith             | Jane               | 90    |

> As Zybooks exports percentage by default I decided to make the grade conversion to points manual. This means the grader will have to convert the percentage to points in the CSV file before running the tool. This is as simple as multiplying the percentage by the total points of the assignment then using excel or google sheets equation to convert the percentage to points then dragging the equation down to apply to all students. This is a simple process and should not take more than a few minutes.

## Late Penalty

The tool applies a late penalty of of your choosing. You can customize the late penalty logic in the script if needed.

To apply a late penalty, you just need to run "canvas_late_penalty.py" with the required arguments you used before.

```bash

python canvas_late_penalty.py --access_token <your_token> --course_id <your_course_id> <assignment_name> <csv_file_path>

```

tool checks the submission date of each student and compares it to the due date of the assignment. If the submission is late, the tool applies the late penalty to the student's grade.


## Output

This program will error if:

- The assignment name is not found in the course.
- The CSV file is not found.
- The student is not found in the course.
- The student submission is not found.
- The student grade is not updated successfully.

## Author

Created by Arthur Wei.

