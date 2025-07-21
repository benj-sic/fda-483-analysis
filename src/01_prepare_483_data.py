import pandas as pd
import os

# --- Configuration ---
INSPECTIONS_FILE = 'data/inspections_details.xlsx'
CITATIONS_FILE = 'data/inspections_citations_details.xlsx'
PUBLISHED_483_FILE = 'data/published_483s.xlsx'

# Directory to save the output
OUTPUT_DIR = "results"
# The final, merged output file
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "merged_483_drug_bio_data.csv") # New output filename

# --- MODIFIED: 'devices' has been removed ---
BIOPHARMA_PRODUCT_TYPES = ['drugs', 'biologics']


# --- Main Execution ---
def main():
    """
    Loads, FILTERS for drugs and biologics, merges, and cleans the FDA 483 data.
    """
    print("🚀 Starting data preparation for FDA 483 analysis (Drugs and Biologics only)...")

    # Create output directory if it doesn't exist
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    # --- 1. Load the data using pd.read_excel ---
    try:
        print(f"Loading inspections data from '{INSPECTIONS_FILE}'...")
        df_inspections = pd.read_excel(INSPECTIONS_FILE)

        print(f"Loading citations data from '{CITATIONS_FILE}'...")
        df_citations = pd.read_excel(CITATIONS_FILE)

        print(f"Loading published 483s data from '{PUBLISHED_483_FILE}'...")
        df_published = pd.read_excel(PUBLISHED_483_FILE)

    except FileNotFoundError as e:
        print(f"❌ FATAL ERROR: Input file not found. {e}")
        return
    except Exception as e:
        print(f"❌ FATAL ERROR: Could not read Excel files. Ensure 'openpyxl' is installed.")
        print(f"   Error details: {e}")
        return

    # --- 2. Standardize Column Names ---
    print("\n--- Standardizing column names ---")
    for df in [df_inspections, df_citations, df_published]:
        df.columns = df.columns.str.lower().str.replace(' ', '_')

    # --- 3. Filter for Biopharma Inspections by Product Type ---
    print("\nFiltering for Drugs and Biologics by 'product_type'...")
    if 'product_type' in df_inspections.columns:
        df_inspections['product_type_lower'] = df_inspections['product_type'].str.lower().fillna('')
        
        mask = df_inspections['product_type_lower'].str.contains('|'.join(BIOPHARMA_PRODUCT_TYPES), na=False)
        
        original_count = len(df_inspections)
        df_inspections_filtered = df_inspections[mask].drop(columns=['product_type_lower'])
        filtered_count = len(df_inspections_filtered)
        
        print(f"Filtered inspections from {original_count} down to {filtered_count} based on product type.")
    else:
        print("⚠️ Warning: 'product_type' column not found in inspections data. Skipping filter.")
        df_inspections_filtered = df_inspections


    # --- 4. Aggregate Citation Data ---
    print("\nAggregating citation text for each inspection...")
    citation_agg_map = {
        'program_area': lambda x: '; '.join(x.astype(str).unique()),
        'short_description': lambda x: '; '.join(x.astype(str).unique()),
        'long_description': lambda x: '\n\n---\n\n'.join(x.astype(str))
    }
    required_cols = list(citation_agg_map.keys())
    if not all(col in df_citations.columns for col in required_cols):
        print(f"❌ FATAL ERROR: The citations file is missing required columns. Expected: {required_cols}")
        return
    df_citations_agg = df_citations.groupby('inspection_id').agg(citation_agg_map).reset_index()


    # --- 5. Merge the DataFrames ---
    print("\nMerging filtered inspections and aggregated citations data...")
    df_merged = pd.merge(
        df_inspections_filtered,
        df_citations_agg,
        on='inspection_id',
        how='left'
    )

    print("Merging with published 483 data using 'fei_number' as the key...")
    if 'fei_number' in df_published.columns:
        df_published.rename(columns={'download': 'published_483_url'}, inplace=True)
        df_published_subset = df_published[['fei_number', 'published_483_url']].drop_duplicates()
        
        df_final = pd.merge(
            df_merged,
            df_published_subset,
            on='fei_number',
            how='left'
        )
    else:
        df_final = df_merged
        df_final['published_483_url'] = ''


    # --- 6. Final Cleaning and Output ---
    print("\nFinalizing the dataset...")
    text_cols_final = ['program_area', 'short_description', 'long_description', 'published_483_url']
    for col in text_cols_final:
         if col in df_final.columns:
            df_final[col] = df_final[col].fillna('')

    date_cols = ['inspection_end_date', 'fmd-145_date', 'publish_date', 'record_date']
    for col in date_cols:
        if col in df_final.columns:
            df_final[col] = pd.to_datetime(df_final[col], errors='coerce')


    # Save the final merged dataset as a CSV for future steps
    df_final.to_csv(OUTPUT_FILE, index=False, encoding='utf-8')

    print("\n" + "="*50)
    print("✅ Data preparation complete!")
    print(f"Filtered drug and biologics data saved to: {OUTPUT_FILE}")
    print(f"Total inspections in final dataset: {len(df_final)}")
    if 'long_description' in df_final.columns:
        print(f"Inspections with 483 observations: {df_final[df_final['long_description'].str.len() > 0].shape[0]}")
    print("="*50)
    print("\nSample of the final merged data:")
    print(df_final[['inspection_id', 'legal_name', 'product_type', 'classification']].head())


if __name__ == "__main__":
    main()