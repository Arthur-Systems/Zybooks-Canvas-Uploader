import os
import pandas as pd
import datetime
import shutil

def process_row(canvas_row, zy_df):
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

    # Try to find the student in the Zybooks report based on email
    zybook_entry = zy_df[zy_df['School email'].str.lower() == email]

    if not zybook_entry.empty:
        # Extract names from Zybooks report and normalize for comparison
        zy_first_name = zybook_entry["First name"].values[0].strip()
        zy_last_name = zybook_entry["Last name"].values[0].strip()

        # Compare names (case-sensitive) and update Zybooks with Canvas names if they don't match
        if zy_first_name != first_name or zy_last_name != last_name:
            print(f"Name mismatch found for {email}: Updating Zybooks name.")
            # Update the names in the Zybooks DataFrame with proper capitalization
            zy_df.loc[zy_df['School email'].str.lower() == email, 'First name'] = first_name
            zy_df.loc[zy_df['School email'].str.lower() == email, 'Last name'] = last_name

        # Return updated record with the Canvas names and grades
        return {
            "Student": canvas_row['Student'],
            "ID": canvas_row['ID'],
            "SIS Login ID": canvas_row['SIS Login ID'],
            "Section": canvas_row['Section'],
            "First Name": first_name,
            "Last Name": last_name,
        }
    else:
        # If the email is not found in Zybooks, return None (will handle separately)
        return None


def process_csv(canvas_df, zy_df):
    processed_rows = []
    unmatched_rows = []

    # Iterate over each row in the Canvas DataFrame
    for index, canvas_row in canvas_df.iterrows():
        # Process each row and build the result
        processed_row = process_row(canvas_row, zy_df)

        if processed_row:
            processed_rows.append(processed_row)
        else:
            # Add unmatched rows to a separate list for export
            unmatched_rows.append(canvas_row)

    # Convert the results into DataFrames
    processed_df = pd.DataFrame(processed_rows)
    unmatched_df = pd.DataFrame(unmatched_rows)

    return processed_df, unmatched_df


def main():
    # Automatically find the Zybooks and Canvas files
    current_year = str(datetime.datetime.now().year)
    files = os.listdir('.')

    # Find the Zybooks file (starts with "UCSC")
    zybooks_file_candidates = [f for f in files if f.startswith("UCSC") and f.endswith(".csv")]
    if not zybooks_file_candidates:
        raise FileNotFoundError("A Zybooks Gradebook File has NOT been found.")
    zybooks_file= zybooks_file_candidates[0]

    # Find the Canvas file (starts with current year)
    # NOTE: This Process can be Automated https://canvas.instructure.com/doc/api/users.html#method.profile.settings
    # But is difficult to implement in a short time frame
    canvas_file_candidates = [f for f in files if f.startswith(current_year) and f.endswith(".csv")]
    if not canvas_file_candidates:
        raise FileNotFoundError(f"A Canvas Gradebook File has NOT been found.")
    canvas_file = canvas_file_candidates[0]

    # Load Zybooks CSV
    zy_df = pd.read_csv(zybooks_file)

    # Normalize email case for matching in Zybooks data
    zy_df["School email"] = zy_df["School email"].str.lower()

    # Load Canvas CSV
    canvas_df = pd.read_csv(canvas_file)
    canvas_df["SIS Login ID"] = canvas_df["SIS Login ID"].str.lower()  # Normalize email case

    # Process the CSV row by row
    result_df, unmatched_df = process_csv(canvas_df, zy_df)

    # Define output files
    result_file_name = "canvas_graded_output.csv"
    unmatched_file_name = "unmatched_emails.csv"
    updated_zybooks_file = "updated_zybooks.csv"

    # Write the results to new CSV files
    result_df.to_csv(result_file_name, index=False)
    unmatched_df.to_csv(unmatched_file_name, index=False)
    # Save the updated Zybooks data with corrected names
    zy_df.to_csv(updated_zybooks_file, index=False)

    print(f"Processed grades have been saved to {result_file_name}")
    print(f"Unmatched emails have been saved to {unmatched_file_name}")
    print(f"Updated Zybooks data saved to {updated_zybooks_file}")

    # After processing, create old directories and move files
    oldzybooks_dir = "oldzybooks"
    oldcanvas_dir = "oldcanvas"
    output_dir = "output"

    os.makedirs(oldzybooks_dir, exist_ok=True)
    # os.makedirs(oldcanvas_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)

    # Move Zybooks files
    shutil.move(zybooks_file, os.path.join(oldzybooks_dir, zybooks_file))
    # Move Canvas files
    # shutil.move(canvas_file, os.path.join(oldcanvas_dir, canvas_file))

    # Move output files
    shutil.move(updated_zybooks_file, os.path.join(output_dir, updated_zybooks_file))
    shutil.move(result_file_name, os.path.join(output_dir, result_file_name))
    shutil.move(unmatched_file_name, os.path.join(output_dir, unmatched_file_name))


if __name__ == "__main__":
    main()
