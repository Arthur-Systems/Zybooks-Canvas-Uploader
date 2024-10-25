import sys
import argparse
import pyfiglet
import json
from canvas_api import get_students, get_assignments, find_assignment, update_grade
from zyphraser import get_scores

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
    print("This script will help you update grades for a specific assignment for all students in Canvas.")
    print("Project created by: Arthur Wei")
    print(separator)

def get_user_input():
    print("Please enter the following details:")
    assignment_name = input("Assignment Name: ")
    csv_file = input("Path to CSV File (default: 'grade.csv'): ") or 'grade.csv'
    return assignment_name, csv_file

def load_config(config_file='config.json'):
    try:
        with open(config_file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Config file '{config_file}' not found, using command-line arguments.")
    except json.JSONDecodeError:
        print(f"Error parsing the config file '{config_file}', using command-line arguments.")
    return {}

def main():
    print_banner()
    display_intro()

    # Load values from config.json
    config = load_config()

    # Set up argument parsing
    parser = argparse.ArgumentParser(description='Update grades for a specific assignment for all students in Canvas.')
    parser.add_argument('--access_token', help='The Canvas API access token')
    parser.add_argument('--course_id', help='The Canvas course ID')
    parser.add_argument('--assignment_name', help='Name of the assignment to update grades for')
    parser.add_argument('--csv_file',default='grade.csv', help='Path to the CSV file with student grades')

    args = parser.parse_args()

    # Use values from config.json if not provided in command-line arguments
    access_token = args.access_token or config.get('access_token')
    course_id = args.course_id or config.get('course_id')

    if not access_token or not course_id:
        print("Access token and course ID must be provided either via config.json or command-line arguments.")
        sys.exit(1)

    if not args.assignment_name or not args.csv_file:
        print("Command-line arguments not fully provided, switching to interactive mode.")
        assignment_name, csv_file = get_user_input()
    else:
        assignment_name = args.assignment_name
        csv_file = args.csv_file

    endpoint = 'https://canvas.ucsc.edu/api/v1'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }

    # Get the list of students
    students = get_students(course_id, headers, endpoint)

    # Get the list of assignments
    assignments = get_assignments(course_id, headers, endpoint)
    # Find the specified assignment
    assignment = find_assignment(assignments, assignment_name)
    if not assignment:
        print(f"Assignment '{assignment_name}' not found.")
        print("Available assignments:", [assign['name'] for assign in assignments])
        sys.exit(1)

    # Get grades from CSV using zyphraser
    grades = get_scores(csv_file, assignment_name)

    # Map student names to grades
    student_grades = {(grade[1], grade[0]): grade[2] for grade in grades}

    # Update the grade for each student
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
