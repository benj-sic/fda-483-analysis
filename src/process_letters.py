import pandas as pd

# Define the input and output file paths
input_file = 'data/compliance_actions.xlsx'
output_file = 'data/drug_and_biologic_warning_letters.csv'

try:
    # Read the Excel file into a pandas DataFrame
    # The engine='openpyxl' is required for .xlsx files
    df = pd.read_excel(input_file, engine='openpyxl')

    # --- Step 1: Filter for Warning Letters ---
    # Keep only the rows where the 'Action Type' column is 'Warning Letter'
    warning_letters_df = df[df['Action Type'] == 'Warning Letter'].copy()

    # --- Step 2: Filter for Drugs and Biologics ---
    # Define the product types we are interested in
    product_types_to_keep = ['Drugs', 'Biologics']

    # Keep only the rows where 'Product Type' is in our list
    filtered_df = warning_letters_df[warning_letters_df['Product Type'].isin(product_types_to_keep)]

    # --- Step 3: Display Results and Save ---
    print("Successfully filtered the data.")
    print(f"Found {len(filtered_df)} warning letters for Drugs and Biologics.")

    # Display the first 10 rows of the filtered data
    print("\n--- Head of Filtered Data ---")
    print(filtered_df.head(10))

    # Save the filtered data to a new CSV file for easier use later
    filtered_df.to_csv(output_file, index=False)
    print(f"\nFiltered data has been saved to: {output_file}")

except FileNotFoundError:
    print(f"Error: The file '{input_file}' was not found.")
    print("Please make sure the file is in the 'data/' directory.")
except Exception as e:
    print(f"An unexpected error occurred: {e}")