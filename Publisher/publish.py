import sys
import argparse
import pyfiglet
import json
import pandas as pd
from Publisher.utils.canvas_api import get_students, get_assignments, find_assignment, update_grade


def print_banner():
    banner = pyfiglet.figlet_format("Canvas Grade Publisher", font="slant")
    separator = u'\u2500' * 100
    print(separator)
    print(banner)
    print(separator)
    print("\n")


def display_intro():
    separator = u'\u2500' * 100
    print("Welcome to the Grade Publisher tool!")
    print("This script will update grades for all students in Canvas.")
    print("Project created by: Arthur Wei")
    print(separator)


def get_user_input():
    print("ENTER THE FOLLOWING DETAILS")
    csv_file = input("Path to CSV File (default: 'grade.csv'): ") or 'grade.csv'
    assignment_name = input("Enter the assignment name: ")
    print("Starting the grade update process...")
    return csv_file, assignment_name


def load_config(config_file='../config.json'):
    try:
        with open(config_file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Config file '{config_file}' not found, using command-line arguments.")
    except json.JSONDecodeError:
        print(f"Error parsing the config file '{config_file}', using command-line arguments.")
    return {}


def detect_grade_column(df):
    """Detects the correct grade column dynamically."""
    for col in df.columns:
        if "Grade" in col and "Max" not in col:
            return col
    raise ValueError("No valid grade column found.")


def get_scores(csv_file):
    """Reads grades from CSV and maps them to student names."""
    df = pd.read_csv(csv_file)
    grade_column = detect_grade_column(df)

    student_grades = {
        (row['First Name'], row['Last Name']): row[grade_column]
        for _, row in df.iterrows()
    }
    return student_grades


def main():
    print_banner()
    display_intro()

    config = load_config()

    parser = argparse.ArgumentParser(description='Update grades for all students in Canvas.')
    parser.add_argument('--access_token', help='The Canvas API access token')
    parser.add_argument('--course_id', help='The Canvas course ID')
    parser.add_argument('--csv_file', default='grade.csv', help='Path to the CSV file with student grades')
    parser.add_argument('--assignment_name', help='The name of the assignment in Canvas')

    args = parser.parse_args()

    access_token = args.access_token or config.get('access_token')
    course_id = args.course_id or config.get('course_id')

    if not access_token or not course_id:
        print("Access token and course ID must be provided either via config.json or command-line arguments.")
        sys.exit(1)

    csv_file = args.csv_file
    assignment_name = args.assignment_name

    if not assignment_name:
        csv_file, assignment_name = get_user_input()

    endpoint = 'https://canvas.ucsc.edu/api/v1'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }

    students = get_students(course_id, headers, endpoint)
    assignments = get_assignments(course_id, headers, endpoint)

    assignment = find_assignment(assignments, assignment_name)

    if not assignment:
        print(f"Assignment '{assignment_name}' not found.")
        print("Available assignments:", [assign['name'] for assign in assignments])
        sys.exit(1)

    student_grades = get_scores(csv_file)

    for student in students:
        name_parts = student['sortable_name'].split(", ")
        last_name = name_parts[0]
        first_name = name_parts[1] if len(name_parts) > 1 else ''
        grade = student_grades.get((first_name, last_name))

        if grade is not None:
            update_grade(course_id, assignment['id'], student['id'], grade, headers, endpoint)
            print(f"Updated grade for student {student['sortable_name']} to {grade}")
        else:
            print(f"No grade found for student {student['sortable_name']}")

    print(f"All students have been updated with their grades for assignment '{assignment_name}'.")


if __name__ == '__main__':
    main()
