import pandas as pd
import os

def generate_polished_report(
    data_folder='results',
    input_filename='classified_483s_final.csv', # Using the final data from the previous step
    output_filename='final_polished_report.md'
    ):
    """
    Generates a final, polished report by improving normalization and cleaning data.
    """
    print("Starting final report generation...")
    input_path = os.path.join(data_folder, input_filename)
    output_path = os.path.join(data_folder, output_filename)

    try:
        df = pd.read_csv(input_path)
    except FileNotFoundError:
        print(f"Error: The file {input_path} was not found.")
        return

    # --- 1. Expanded Normalization Mapping ---
    # This more comprehensive map will reduce the 'Other' category size.
    category_map = {
        'Procedures': ['procedure', 'sops', 's.o.p.'],
        'Investigations': ['investigation', 'capa', 'corrective and preventive'],
        'Quality Systems': ['quality system', 'quality control', 'quality assurance', 'cgmp deficiencies'],
        'CGMP': ['cgmp', 'gmp', 'good manufacturing'],
        'Recordkeeping': ['record', 'documentation', 'data integrity'],
        'Testing & Lab Controls': ['testing', 'laboratory', 'lab controls', 'stability', 'analytical method'],
        'Facilities & Equipment': ['facility', 'equipment', 'environmental control', 'sanitation', 'cleaning'],
        'Clinical & IRB': ['clinical', 'irb', 'institutional review', 'informed consent', 'protocol deviation', 'gcp'],
        'Personnel': ['personnel', 'training', 'qualifications'],
        'Materials Management': ['materials', 'supplier', 'component', 'storage', 'handling', 'distribution'],
        'Aseptic Processing': ['aseptic', 'sterile', 'sterility'],
        'Reporting & Submissions': ['report', 'submission', 'adverse event', 'mdr', 'ind', 'new drug application'],
        'Validation': ['validation', 'validated'],
        'Design Controls': ['design control', 'dhf'],
        'Labeling': ['labeling', 'label']
    }

    def normalize_category(cat):
        cat_lower = str(cat).lower()
        for key, variations in category_map.items():
            for variation in variations:
                if variation in cat_lower:
                    return key
        return 'Other'

    # Apply the improved normalization
    df['normalized_category'] = df['primary_category'].apply(normalize_category)
    print("Categories have been normalized with an expanded map.")

    # --- 2. CRITICAL: Clean the data BEFORE analysis ---
    # Filter out rows where classification failed or there was no text
    df_clean = df[~df['primary_category'].isin(['Error', 'No Text'])].copy()
    
    # Check if the dataframe is empty after cleaning
    if df_clean.empty:
        print("Warning: No data left after cleaning. The report will be empty.")
        return

    # --- 3. Re-run Analysis on Polished Data ---
    severity_order = ['Critical', 'Major', 'Minor']
    df_clean['severity'] = pd.Categorical(df_clean['severity'], categories=severity_order, ordered=True)

    total_observations = len(df_clean)
    normalized_category_dist = df_clean['normalized_category'].value_counts()
    severity_dist = df_clean['severity'].value_counts()
    top_sub_categories = df_clean['sub_category'].value_counts().nlargest(10)
    critical_issues = df_clean[df_clean['severity'] == 'Critical']['sub_category'].value_counts().nlargest(10) # Expanded to top 10
    critical_companies = df_clean[df_clean['severity'] == 'Critical']['legal_name'].value_counts().nlargest(10) # Expanded to top 10

    # --- 4. Build the Polished Markdown Report ---
    report = [f"# FDA 483 Actionable Intelligence Report (Final Polished)\n"]
    report.append(f"This report analyzes **{total_observations:,}** valid, classified FDA 483 observations, providing the most accurate view of industry-wide compliance risks.\n")
    report.append("---")
    report.append("## 1. The Real Top 10: Normalized Compliance Failures\n")
    report.append(f"```\n{normalized_category_dist.head(10).to_string()}\n```\n")
    report.append("---")
    report.append("## 2. The Most Frequent, Specific Failures (Top 10 Sub-Categories)\n")
    report.append(f"```\n{top_sub_categories.to_string()}\n```\n")
    report.append("---")
    report.append("## 3. The Highest-Risk Landscape\n")
    report.append("### Most Common `Critical` Risk Sub-Categories\n")
    report.append(f"```\n{critical_issues.to_string()}\n```\n")
    report.append("### Overall Severity of Findings\n")
    report.append(f"```\n{severity_dist.to_string()}\n```\n")
    report.append("---")
    report.append("## 4. Companies with the Most `Critical` Observations\n")
    report.append(f"```\n{critical_companies.to_string()}\n```\n")

    # --- 5. Write the report to a file ---
    with open(output_path, 'w') as f:
        f.write('\n'.join(report))

    print(f"\nFinal polished report generated at: {output_path}")

if __name__ == '__main__':
    generate_polished_report()