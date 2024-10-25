# grading_tool/zyphraser.py

import argparse
import sys
import csv

def get_scores(file, assignment):
    try:
        with open(file, newline='') as csvfile:
            reader = csv.reader(csvfile)
            header = next(reader)

            required_columns = ["Last name", "First name", f"{assignment}(points)"]
            for col in required_columns:
                if col not in header:
                    raise ValueError(f"Missing required column: {col}")

            data = []
            for row in reader:
                last_name = row[header.index("Last name")]
                first_name = row[header.index("First name")]
                points = row[header.index(f"{assignment}(points)")]
                data.append((last_name, first_name, points))

            return data
    except Exception as e:
        print(f"Error reading the file: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Get grades from zybooks")
    parser.add_argument("file", help="Path to the CSV file")
    parser.add_argument("--assignment", default="ZyLab2", help="Assignment name to get scores for")
    args = parser.parse_args()

    scores = get_scores(args.file, args.assignment)

    for score in scores:
        print(f"Last name: {score[0]}, First name: {score[1]}, {args.assignment}: {score[2]}")

if __name__ == '__main__':
    main()
