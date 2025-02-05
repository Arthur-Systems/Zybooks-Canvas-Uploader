import os
import pandas as pd
import datetime
import shutil

def process_row(canvas_row, new_df):
    """Match students from the Canvas file with the new dataset and update names if necessary."""
    # Extract email from Canvas row
    if isinstance(canvas_row['SIS Login ID'], str):
        email = canvas_row['SIS Login ID'].strip().lower()  # Normalize email for comparison
    else:
        return None

    # Check if the 'Student' column is valid (to skip rows like "Points Possible")
    if ',' not in canvas_row['Student']:
        return None  # Skip invalid rows

    # Split the 'Student' column into 'Last Name' and 'First Name'
    last_name, first_name = [name.strip() for name in canvas_row['Student'].split(", ")]

    # Try to find the student in the new dataset based on email
    new_entry = new_df[new_df['Email'].str.lower() == email]

    if not new_entry.empty:
        # Extract names from the dataset and normalize for comparison
        new_first_name = new_entry["First Name"].values[0].strip()
        new_last_name = new_entry["Last Name"].values[0].strip() if isinstance(new_entry["Last Name"].values[0], str) else ""

        # Compare names and update if necessary
        if new_first_name != first_name or new_last_name != last_name:
            print(f"Name mismatch found for {email}: Updating names in the dataset.")
            new_df.loc[new_df['Email'].str.lower() == email, 'First Name'] = first_name
            new_df.loc[new_df['Email'].str.lower() == email, 'Last Name'] = last_name

        # Return updated record with the Canvas names and grades
        return {
            "Student": canvas_row['Student'],
            "ID": canvas_row['ID'],
            "SIS Login ID": canvas_row['SIS Login ID'],
            "Section": canvas_row['Section'],
            "First Name": first_name,
            "Last Name": last_name,
            "Grade": new_entry["Grade"].values[0],  # Extract the grade
            "Max Grade": new_entry["Max Grade"].values[0]  # Extract the max grade
        }
    else:
        # If the email is not found, return None (will handle separately)
        return None


def process_csv(canvas_df, new_df):
    processed_rows = []
    unmatched_rows = []

    # Iterate over each row in the Canvas DataFrame
    for _, canvas_row in canvas_df.iterrows():
        processed_row = process_row(canvas_row, new_df)

        if processed_row:
            processed_rows.append(processed_row)
        else:
            unmatched_rows.append(canvas_row)

    # Convert the results into DataFrames
    processed_df = pd.DataFrame(processed_rows)
    unmatched_df = pd.DataFrame(unmatched_rows)

    return processed_df, unmatched_df


def main():
    # Automatically find the Canvas and CSE30 files
    current_year = str(datetime.datetime.now().year)
    files = os.listdir('.')

    # Find the CSE30 dataset file (starts with "CSE30")
    new_file_candidates = [f for f in files if f.startswith("CSE30") and f.endswith(".csv")]
    if not new_file_candidates:
        raise FileNotFoundError("A CSE30 Gradebook File has NOT been found.")
    new_file = new_file_candidates[0]

    # Find the Canvas file (starts with current year)
    canvas_file_candidates = [f for f in files if f.startswith(current_year) and f.endswith(".csv")]
    if not canvas_file_candidates:
        raise FileNotFoundError(f"A Canvas Gradebook File has NOT been found.")
    canvas_file = canvas_file_candidates[0]

    # Load the CSE30 dataset
    new_df = pd.read_csv(new_file)
    new_df["Email"] = new_df["Email"].str.lower()  # Normalize email case

    # Load Canvas CSV
    canvas_df = pd.read_csv(canvas_file)
    canvas_df["SIS Login ID"] = canvas_df["SIS Login ID"].str.lower()  # Normalize email case

    # Process the CSV row by row
    result_df, unmatched_df = process_csv(canvas_df, new_df)

    # Define output files
    result_file_name = "canvas_graded_output.csv"
    unmatched_file_name = "unmatched_emails.csv"
    updated_new_file = "updated_dataset.csv"

    # Write results to new CSV files
    result_df.to_csv(result_file_name, index=False)
    unmatched_df.to_csv(unmatched_file_name, index=False)
    new_df.to_csv(updated_new_file, index=False)

    print(f"Processed grades have been saved to {result_file_name}")
    print(f"Unmatched emails have been saved to {unmatched_file_name}")
    print(f"Updated dataset saved to {updated_new_file}")

    # After processing, create old directories and move files
    oldcse30_dir = "oldcse30"
    oldcanvas_dir = "oldcanvas"
    output_dir = "output"

    os.makedirs(oldcse30_dir, exist_ok=True)
    os.makedirs(oldcanvas_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)

    # Move CSE30 file to oldcse30 directory
    shutil.move(new_file, os.path.join(oldcse30_dir, new_file))

    # Move Canvas file to oldcanvas directory
    shutil.move(canvas_file, os.path.join(oldcanvas_dir, canvas_file))

    # Move output files to output directory
    shutil.move(updated_new_file, os.path.join(output_dir, updated_new_file))
    shutil.move(result_file_name, os.path.join(output_dir, result_file_name))
    shutil.move(unmatched_file_name, os.path.join(output_dir, unmatched_file_name))


if __name__ == "__main__":
    main()