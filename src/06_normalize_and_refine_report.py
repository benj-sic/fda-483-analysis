import pandas as pd
import os

def normalize_and_report(
    data_folder='results',
    input_filename='classified_483s_final.csv',
    output_filename='final_report_normalized.md'
    ):
    """
    Normalizes the AI-generated categories and creates a final, refined report.
    """
    print("Starting report refinement and normalization...")
    input_path = os.path.join(data_folder, input_filename)
    output_path = os.path.join(data_folder, output_filename)

    try:
        df = pd.read_csv(input_path)
    except FileNotFoundError:
        print(f"Error: The file {input_path} was not found.")
        return

    # --- 1. Normalization Mapping ---
    # This dictionary defines how to merge messy categories into clean ones.
    category_map = {
        'Procedures': ['Procedures', 'Failure to Establish and Follow Written Procedures', 'Failure to Follow Standard Operating Procedures (SOPs)', 'Lack of Written Procedures and Inadequate Controls'],
        'Investigations': ['Investigations', 'Failure to Conduct Investigation According to Protocol', 'Failure Investigations', 'Failure to Investigate'],
        'Quality Systems': ['Quality Systems', 'Quality System', 'CGMP Deficiencies', 'Lack of Quality System'],
        'CGMP': ['Current Good Manufacturing Practices (CGMP)', 'Good Manufacturing Practices (GMP)', 'cGMP', 'CGMP Violations', 'Failure to comply with cGMP'],
        'Recordkeeping': ['Recordkeeping', 'Data Integrity', 'Device History Records', 'Incomplete/Missing Records'],
        'Testing & Lab Controls': ['Testing', 'Laboratory Controls', 'Quality Control', 'Test Method Validation'],
        'Facilities & Equipment': ['Facilities & Equipment', 'Facility and Equipment', 'Facilities', 'Equipment', 'Environmental Control'],
        'Clinical & IRB': ['Clinical Investigations', 'Institutional Review Board (IRB) deficiencies', 'Informed Consent', 'Protocol Deviation', 'Good Clinical Practice (GCP)'],
        'Personnel': ['Personnel', 'Personnel and Training'],
        'Materials Management': ['Materials', 'Supplier Control', 'Component Controls'],
        'Aseptic Processing': ['Aseptic Processing', 'Sterility Assurance'],
        'Reporting': ['Failure to Report', 'Adverse Event Reporting', 'Medical Device Reporting (MDR)']
    }

    # Create a reverse map for easy lookup
    reverse_map = {val: key for key, values in category_map.items() for val in values}

    def normalize_category(cat):
        # Find a match in the map, otherwise return 'Other'
        for key, variations in category_map.items():
            for variation in variations:
                if variation.lower() in str(cat).lower():
                    return key
        return 'Other'

    # Apply the normalization
    df['normalized_category'] = df['primary_category'].apply(normalize_category)
    print("Categories have been normalized.")

    # --- 2. Re-run Analysis on Clean Data ---
    df_clean = df[df['normalized_category'] != 'Error'].copy()
    severity_order = ['Critical', 'Major', 'Minor']
    df_clean['severity'] = pd.Categorical(df_clean['severity'], categories=severity_order, ordered=True)

    total_observations = len(df_clean)
    normalized_category_dist = df_clean['normalized_category'].value_counts()
    severity_dist = df_clean['severity'].value_counts()
    top_sub_categories = df_clean['sub_category'].value_counts().nlargest(10)
    critical_issues = df_clean[df_clean['severity'] == 'Critical']['sub_category'].value_counts().nlargest(5)
    critical_companies = df_clean[df_clean['severity'] == 'Critical']['legal_name'].value_counts().nlargest(5)

    # --- 3. Build the Refined Markdown Report ---
    report = []
    report.append("# FDA 483 Observations: Refined Actionable Report\n\n")
    report.append("## 1. Executive Summary\n")
    report.append(f"This refined report analyzes **{total_observations:,}** observations based on **normalized compliance categories**. This provides a clearer, more accurate view of the key risk areas.\n")

    report.append("---")
    report.append("## 2. Deep Dive: Normalized Compliance Failures\n")
    report.append("### Most Frequent Observation Categories (Normalized)\n")
    report.append("This consolidated view shows the true frequency of core compliance issues.\n")
    report.append(f"```\n{normalized_category_dist.to_string()}\n```\n")
    
    report.append("### Top 10 Most Frequent Sub-Categories (All Severities)\n")
    report.append(f"```\n{top_sub_categories.to_string()}\n```\n")

    report.append("---")
    report.append("## 3. High-Level Risk Landscape\n")
    report.append("### Overall Severity of Findings\n")
    report.append(f"```\n{severity_dist.to_string()}\n```\n")
    
    report.append("### Most Common `Critical` Risk Sub-Categories\n")
    report.append("These sub-categories represent the most severe, direct risks to patient safety and data integrity.\n")
    report.append(f"```\n{critical_issues.to_string()}\n```\n")
    
    report.append("---")
    report.append("## 4. Company-Specific Risk Insights\n")
    report.append("### Top 5 Companies by Number of `Critical` Observations\n")
    report.append(f"```\n{critical_companies.to_string()}\n```\n")

    report.append("---")
    report.append("## 5. Actionable Insights for Stakeholders (Unchanged)\n")
    report.append("*(The strategic advice remains the same, but is now based on more accurate data)*\n")

    # (Your existing insights section can be copied here)

    # --- 4. Write the report to a file ---
    with open(output_path, 'w') as f:
        f.write('\n'.join(report))

    print(f"\nRefined and normalized report successfully generated at: {output_path}")


if __name__ == '__main__':
    normalize_and_report()