import pandas as pd

# Set pandas to display all rows for our top 10 lists
pd.set_option('display.max_rows', 20)

# --- File Paths ---
linked_inspections_file = 'data/inspections_with_warning_letter_status.csv'
# This file with AI classifications is generated from script 02a
classified_citations_file = 'data/classified_483s_granular.csv' 

try:
    # --- Step 1: Load the Datasets ---
    print("Loading linked inspection and classified citation data...")
    linked_df = pd.read_csv(linked_inspections_file)
    citations_df = pd.read_csv(classified_citations_file)

    # --- Step 2: Merge to Create a Master Analysis File ---
    # We only need the Inspection ID and the warning letter flag from the linked file
    master_df = pd.merge(
        citations_df,
        linked_df[['Inspection ID', 'Received_Warning_Letter']],
        on='Inspection ID',
        how='left'
    )

    # Ensure the flag is boolean (True/False)
    master_df['Received_Warning_Letter'] = master_df['Received_Warning_Letter'].fillna(False)

    # --- Step 3: Split the Data into Two Groups ---
    wl_inspections = master_df[master_df['Received_Warning_Letter'] == True]
    no_wl_inspections = master_df[master_df['Received_Warning_Letter'] == False]
    
    print(f"\nAnalysis includes {len(wl_inspections)} observations from WL-associated inspections.")
    print(f"Analysis includes {len(no_wl_inspections)} observations from non-WL inspections.")

    # --- Step 4: Find the Top 10 Citations for Each Group ---
    top_wl_triggers = wl_inspections['sub_category'].value_counts().nlargest(10)
    top_no_wl_citations = no_wl_inspections['sub_category'].value_counts().nlargest(10)

    # --- Step 5: Display the Comparison ---
    print("\n" + "="*80)
    print("      Comparison: Top 10 Citations by Warning Letter (WL) Status")
    print("="*80 + "\n")

    # Create a DataFrame for nice side-by-side printing
    comparison_df = pd.DataFrame({
        'Citations LEADING TO a Warning Letter': top_wl_triggers.index,
        'Count (WL)': top_wl_triggers.values,
        'Citations NOT leading to a Warning Letter': top_no_wl_citations.index,
        'Count (No WL)': top_no_wl_citations.values
    })
    
    print(comparison_df)
    print("\n" + "="*80)
    

except FileNotFoundError as e:
    print(f"Error: A required file was not found. Please ensure both '{linked_inspections_file}' and '{classified_citations_file}' exist. {e}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")