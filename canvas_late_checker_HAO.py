import pyfiglet
import json
import argparse
import sys
import requests
import zyphraser
from canvas_api import get_students, find_assignment, get_assignments


def print_banner():
    banner = pyfiglet.figlet_format("Canvas Late Penalty Tool", font="slant")
    separator = "\u2500" * 100
    print(separator)
    print(banner)
    print(separator)
    print("\n")


def get_user_input():
    print("Please enter the following details:")
    assignment_name = input("Assignment Name: ")
    csv_file = input("Path to CSV File (default: 'grade.csv'): ") or "grade.csv"
    return assignment_name, csv_file


def display_intro():
    print("Welcome to the Canvas Late Penalty Tool!")
    print(
        "This script will help you apply late penalties and update grades for a specific assignment in Canvas."
    )
    print("Project created by: Arthur Wei")
    print("\n")


def load_config(config_file="config.json"):
    try:
        with open(config_file, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Config file '{config_file}' not found, using command-line arguments.")
    except json.JSONDecodeError:
        print(
            f"Error parsing the config file '{config_file}', using command-line arguments."
        )
    return {}


def get_submission(course_id, assignment_id, student_id, headers):
    submission_url = f"{endpoint}/courses/{course_id}/assignments/{assignment_id}/submissions/{student_id}"
    response = requests.get(submission_url, headers=headers)
    if response.status_code != 200:
        print(
            f"Failed to retrieve submission for student {student_id}. Status code: {response.status_code}, Response: {response.text}"
        )
        return None
    return response.json()


def apply_late_penalty(
    course_id, assignment_id, student_id, headers, current_grade, csv_grade
):
    # Calculate the score increase and apply an 80% late penalty
    score_increased_by = csv_grade - current_grade
    new_score = current_grade + score_increased_by * 0.8

    submission_url = f"{endpoint}/courses/{course_id}/assignments/{assignment_id}/submissions/{student_id}"
    payload = {
        "submission": {
            "posted_grade": new_score,
            "late_policy_status": "late",
            "seconds_late_override": 0,  # just to show that the late penalty was applied
        }
    }
    response = requests.put(submission_url, headers=headers, json=payload)
    if response.status_code != 200:
        print(
            f"Failed to update grade for student {student_id}. Status code: {response.status_code}, Response: {response.text}"
        )
    else:
        print(
            f"Applied late penalty. Updated grade to {new_score} for student {student_id}"
        )


def get_grades(course_id, headers, assignment_name, csv_file):
    students = get_students(course_id, headers, endpoint)
    assignments = get_assignments(course_id, headers, endpoint)
    assignment = find_assignment(assignments, assignment_name)
    if not assignment:
        print(f"Assignment '{assignment_name}' not found.")
        print("Available assignments:", [assign["name"] for assign in assignments])
        sys.exit(1)

    # Get grades from CSV using zyphraser
    grades = zyphraser.get_scores(csv_file, assignment_name)
    student_grades = {(grade[1], grade[0]): grade[2] for grade in grades}

    # Check and update the grade for each student
    for student in students:
        first_name, last_name = (
            student["sortable_name"].split(", ")[1],
            student["sortable_name"].split(", ")[0],
        )
        csv_grade = float(student_grades.get((first_name, last_name), 0))

        submission = get_submission(course_id, assignment["id"], student["id"], headers)
        if submission and "grade" in submission:
            current_grade = float(submission["grade"]) if submission["grade"] else 0
            if csv_grade > current_grade or current_grade == 0:
                apply_late_penalty(
                    course_id,
                    assignment["id"],
                    student["id"],
                    headers,
                    current_grade,
                    csv_grade,
                )
            else:
                print(
                    f"No late penalty applied. Grade not updated for student {student['sortable_name']}"
                )
        else:
            print(f"No current grade found for student {student['sortable_name']}")


def main():
    print_banner()
    display_intro()

    # Load values from config.json
    config = load_config()

    # Set up argument parsing
    parser = argparse.ArgumentParser(
        description="Update grades for a specific assignment for all students in Canvas."
    )
    parser.add_argument("--access_token", help="The Canvas API access token")
    parser.add_argument("--course_id", help="The Canvas course ID")
    parser.add_argument(
        "--assignment_name", help="Name of the assignment to update grades for"
    )
    parser.add_argument(
        "--csv_file",
        default="grade.csv",
        help="Path to the CSV file with student grades",
    )

    args = parser.parse_args()

    # Use values from config.json if not provided in command-line arguments
    access_token = args.access_token or config.get("access_token")
    course_id = args.course_id or config.get("course_id")

    if not access_token or not course_id:
        print(
            "Access token and course ID must be provided either via config.json or command-line arguments."
        )
        sys.exit(1)

    if not args.assignment_name or not args.csv_file:
        print(
            "Command-line arguments not fully provided, switching to interactive mode."
        )
        assignment_name, csv_file = get_user_input()
    else:
        assignment_name, csv_file = args.assignment_name, args.csv_file

    global endpoint
    endpoint = "https://canvas.ucsc.edu/api/v1"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}",
    }

    # Get and update grades
    get_grades(course_id, headers, assignment_name, csv_file)


if __name__ == "__main__":
    main()
