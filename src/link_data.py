import pandas as pd

# Define file paths
inspections_file = 'data/inspections_details.xlsx'
warning_letters_file = 'data/drug_and_biologic_warning_letters.csv'
output_file = 'data/inspections_with_warning_letter_status.csv'

try:
    # --- Step 1: Load the Datasets ---
    print("Loading datasets...")
    # Load inspection details
    inspections_df = pd.read_excel(inspections_file, engine='openpyxl')
    # Load the filtered warning letters
    warning_letters_df = pd.read_csv(warning_letters_file)

    # --- Step 2: Prepare Data for Merging ---
    # Convert date columns to datetime objects for accurate comparison
    inspections_df['Inspection End Date'] = pd.to_datetime(inspections_df['Inspection End Date'])
    warning_letters_df['Action Taken Date'] = pd.to_datetime(warning_letters_df['Action Taken Date'])

    # --- Step 3: Merge the Datasets on FEI Number ---
    # We use a 'left' merge to keep all original inspections and add warning letter info where it exists.
    print("Merging datasets on FEI Number...")
    merged_df = pd.merge(
        inspections_df,
        warning_letters_df,
        on='FEI Number',
        how='left',
        suffixes=('', '_wl') # Add a suffix to warning letter columns to avoid confusion
    )

    # --- Step 4: Validate the Linkage ---
    # A valid warning letter should come AFTER the inspection.
    # Calculate the difference in days between the action date and the inspection end date.
    merged_df['Days_to_Warning_Letter'] = (merged_df['Action Taken Date'] - merged_df['Inspection End Date']).dt.days

    # Create a final flag. The link is valid if a warning letter exists AND it was issued after the inspection.
    # We'll allow for a small window (e.g., up to 0 days) in case they occur on the same day.
    merged_df['Received_Warning_Letter'] = (merged_df['Days_to_Warning_Letter'] >= 0)

    # Clean up - set the flag to False for rows that had no matching warning letter (NaNs)
    merged_df['Received_Warning_Letter'] = merged_df['Received_Warning_Letter'].fillna(False)


    # --- Step 5: Analyze and Save Results ---
    # Count how many inspections have a linked warning letter
    warning_letter_count = merged_df['Received_Warning_Letter'].sum()
    total_inspections = len(inspections_df)
    percentage = (warning_letter_count / total_inspections) * 100

    print("\n--- Analysis Complete ---")
    print(f"Total inspections analyzed: {total_inspections}")
    print(f"Inspections linked to a subsequent Warning Letter: {warning_letter_count} ({percentage:.2f}%)")


    # Select and rename columns for a clean final output
    final_df = merged_df[[
        'FEI Number',
        'Inspection ID',
        'Inspection End Date',
        'Classification',
        'Legal Name',
        'City',
        'State',
        'Received_Warning_Letter',
        'Action Taken Date',
        'Days_to_Warning_Letter'
    ]].copy()


    # Save the new, enriched dataset
    final_df.to_csv(output_file, index=False)
    print(f"\nEnriched data saved to: {output_file}")
    print("\n--- First 10 Rows of Linked Data ---")
    # Show rows that actually received a warning letter for demonstration
    print(final_df[final_df['Received_Warning_Letter']].head(10))


except FileNotFoundError as e:
    print(f"Error: A required file was not found. {e}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")