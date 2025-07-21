import pandas as pd
import os

def generate_actionable_report(
    data_folder='results',
    input_filename='classified_483s_final.csv',
    output_filename='final_actionable_report.md'
    ):
    """
    Generates a markdown report with actionable insights from the classified FDA 483 data.
    """
    print("Starting report generation...")
    # Construct paths
    input_path = os.path.join(data_folder, input_filename)
    output_path = os.path.join(data_folder, output_filename)

    # Load the classified data
    try:
        df = pd.read_csv(input_path)
    except FileNotFoundError:
        print(f"Error: The file {input_path} was not found.")
        return

    # --- 1. Data Cleaning and Preparation ---
    # Drop rows where classification failed
    df_clean = df[df['primary_category'] != 'Error'].copy()
    # Filter out rows with no observation text
    df_clean = df_clean[df_clean['primary_category'] != 'No Text'].copy()

    # Ensure severity levels are ordered for analysis
    severity_order = ['Critical', 'Major', 'Minor']
    df_clean['severity'] = pd.Categorical(df_clean['severity'], categories=severity_order, ordered=True)

    # --- 2. Perform Key Analyses ---
    # Total valid observations
    total_observations = len(df_clean)

    # Overall Category Distribution
    category_dist = df_clean['primary_category'].value_counts()

    # Severity Distribution
    severity_dist = df_clean['severity'].value_counts()

    # Top 10 Most Frequent Sub-Categories
    top_sub_categories = df_clean['sub_category'].value_counts().nlargest(10)

    # Top 5 Critical Sub-Categories
    critical_issues = df_clean[df_clean['severity'] == 'Critical']['sub_category'].value_counts().nlargest(5)
    
    # Top 5 Companies with the Most Critical Observations
    critical_companies = df_clean[df_clean['severity'] == 'Critical']['legal_name'].value_counts().nlargest(5)


    # --- 3. Build the Markdown Report ---
    report = []
    report.append("# FDA 483 Observations: Actionable Intelligence Report\n\n")
    report.append("## 1. Executive Summary\n")
    report.append(f"This report analyzes **{total_observations:,}** classified FDA 483 observations to provide actionable insights for biotech and pharmaceutical stakeholders.\n")
    report.append("The key takeaway is a clear focus on procedural adherence and robust investigation processes. Deficiencies in these areas represent the most significant and frequent compliance risks.\n")

    report.append("---")

    report.append("## 2. High-Level Risk Landscape\n")
    report.append("### Overall Severity of Findings\n")
    report.append("The distribution of observation severity highlights the overall risk profile of the industry.\n")
    report.append(f"```\n{severity_dist.to_string()}\n```\n")
    
    report.append("### Most Common `Critical` Risk Areas\n")
    report.append("These sub-categories represent the most severe, direct risks to patient safety and data integrity.\n")
    report.append(f"```\n{critical_issues.to_string()}\n```\n")

    report.append("---")

    report.append("## 3. Deep Dive: Common Compliance Failures\n")
    report.append("### Most Frequent Observation Categories\n")
    report.append("This chart shows the primary areas where inspectors are focusing their attention.\n")
    report.append(f"```\n{category_dist.to_string()}\n```\n")

    report.append("### Top 10 Most Frequent Sub-Categories (All Severities)\n")
    report.append("These are the specific, recurring problems that companies struggle with most often.\n")
    report.append(f"```\n{top_sub_categories.to_string()}\n```\n")

    report.append("---")
    
    report.append("## 4. Company-Specific Risk Insights\n")
    report.append("### Top 5 Companies by Number of `Critical` Observations\n")
    report.append("The following companies have accumulated the highest number of critical findings, indicating potentially systemic quality issues that warrant further due diligence for investors and executives.\n")
    report.append(f"```\n{critical_companies.to_string()}\n```\n")


    report.append("## 5. Actionable Insights for Stakeholders\n")
    report.append("**For Biotech Entrepreneurs:**\n")
    report.append("- **Design for Compliance:** From day one, build your Quality Management System (QMS) with a focus on robust procedures for investigations (CAPA, root cause) and lab controls.\n")
    report.append("- **Right-Sized SOPs:** Ensure your Standard Operating Procedures (SOPs) are not just written, but are practical, followed, and verifiably adequate for their purpose.\n\n")

    report.append("**For Executives:**\n")
    report.append("- **Resource Allocation:** Use the category and severity data to justify budget and allocate resources to the highest-risk areas, such as `Investigations` and `Testing`.\n")
    report.append("- **Leading Indicators:** Treat a rise in `Major` findings in any category as a leading indicator of future `Critical` issues. Proactively address these trends.\n\n")

    report.append("**For Investors:**\n")
    report.append("- **Due Diligence Red Flags:** A pattern of `Critical` findings, especially in `Data Integrity` or `Sterility Assurance`, is a major red flag. A high number of repeat observations for the same sub-category suggests a failed CAPA system.\n")
    report.append("- **Benchmarking Questions:** When evaluating a company, ask: 'How does your rate of observations in `Procedures` and `Investigations` compare to the industry benchmark shown here?'\n")

    # --- 4. Write the report to a file ---
    with open(output_path, 'w') as f:
        f.write('\n'.join(report))

    print(f"\nActionable report successfully generated at: {output_path}")

if __name__ == '__main__':
    generate_actionable_report()