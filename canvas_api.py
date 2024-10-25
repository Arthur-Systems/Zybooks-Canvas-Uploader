# grading_tool/canvas_api.py

import sys
import requests

def get_students(course_id, headers, endpoint):
    students = []
    users_url = f"{endpoint}/courses/{course_id}/users"
    while users_url:
        response = requests.get(users_url, headers=headers, params={"enrollment_type": "student", "per_page": 100})
        if response.status_code != 200:
            print(f"Failed to retrieve students. Status code: {response.status_code}, Response: {response.text}")
            sys.exit(1)
        students.extend(response.json())
        users_url = None
        if 'Link' in response.headers:
            links = response.headers['Link'].split(',')
            for link in links:
                if 'rel="next"' in link:
                    users_url = link[link.find('<') + 1:link.find('>')]
    return students

def get_assignments(course_id, headers, endpoint):
    assignments = []
    assignments_url = f"{endpoint}/courses/{course_id}/assignments"
    while assignments_url:
        response = requests.get(assignments_url, headers=headers, params={"per_page": 100})
        if response.status_code != 200:
            print(f"Failed to retrieve assignments. Status code: {response.status_code}, Response: {response.text}")
            sys.exit(1)
        assignments.extend(response.json())
        assignments_url = None
        if 'Link' in response.headers:
            links = response.headers['Link'].split(',')
            for link in links:
                if 'rel="next"' in link:
                    assignments_url = link[link.find('<') + 1:link.find('>')]
    return assignments

def find_assignment(assignments, assignment_name):
    normalized_assignment_name = assignment_name.replace(" ", "").lower()
    for assignment in assignments:
        normalized_name = assignment['name'].replace(" ", "").lower()
        if normalized_name == normalized_assignment_name:
            return assignment
    return None

def update_grade(course_id, assignment_id, student_id, grade, headers, endpoint):
    submission_url = f"{endpoint}/courses/{course_id}/assignments/{assignment_id}/submissions/{student_id}"
    payload = {
        "submission": {
            "posted_grade": grade,
            "late_policy_status": ("missing" if grade in [0, "0"] else "none")
        }
    }
    response = requests.put(submission_url, headers=headers, json=payload)
    if "missing" in payload["submission"]["late_policy_status"]:
        print(f"marked as missing")
    if response.status_code != 200:
        print(f"Failed to update grade for student {student_id}. Status code: {response.status_code}, Response: {response.text}")
