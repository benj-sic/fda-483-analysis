import pandas as pd
import sys

# --- CONFIGURATION ---
# The correct column name has been identified and set.
citation_column_name = 'Act/CFR Number' 
# -------------------

# --- File Paths ---
citations_input_file = 'data/inspections_citations_details.xlsx'
output_file = 'data/classified_483s_granular.csv' 

try:
    print(f"Reading file: '{citations_input_file}'...")
    citations_df = pd.read_excel(citations_input_file, engine='openpyxl')
    
    print(f"Using '{citation_column_name}' as the citation column.")
    
    # Rename the selected column to what the analysis script expects
    citations_df.rename(columns={citation_column_name: 'sub_category'}, inplace=True)

    # Handle any missing values in our chosen column
    citations_df['sub_category'] = citations_df['sub_category'].fillna('Not Specified')
    
    # We only need the inspection ID and the new sub_category column
    prepared_df = citations_df[['Inspection ID', 'sub_category']].copy()

    # Save the prepared data to the path the next script needs
    prepared_df.to_csv(output_file, index=False)

    print("\n✅ Successfully prepared citation data!")
    print(f"Created '{output_file}' with '{citation_column_name}' as the 'sub_category'.")
    print("\n➡️ Next Step: Run the final analysis script: python src/analyze_triggers.py")

except FileNotFoundError:
    print(f"❌ Error: The input file '{citations_input_file}' was not found.")
except KeyError:
    print(f"\n❌ KeyError: The column name '{citation_column_name}' is still not correct.")
    print("Please double-check the column list and edit the script again.")
except Exception as e:
    print(f"An unexpected error occurred: {e}")