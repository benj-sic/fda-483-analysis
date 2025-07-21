import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import os

# --- Configuration ---
# Input file will be the output from the currently running classification script
CLASSIFIED_DATA_FILE = 'results/classified_483_drug_bio_data.csv'
# Directory to save the final charts and reports
OUTPUT_DIR = "results/final_483_report"

# High-Quality Plotting Defaults
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.size'] = 12
plt.rcParams['axes.titlesize'] = 16

# --- Analysis Functions ---

def create_summary_chart(df, categories, title, save_name):
    """Creates a professional horizontal bar chart for the 483 categories."""
    print(f"Generating summary chart: {title}...")
    
    # Calculate counts and percentages from the total number of inspections with observations
    inspections_with_obs = df[df['long_description'].str.len() > 0]
    total_with_obs = len(inspections_with_obs)
    
    counts = inspections_with_obs[categories].sum()
    percentages = (counts / total_with_obs) * 100
    
    sorted_percentages = percentages.sort_values(ascending=True)
    sorted_counts = counts.reindex(sorted_percentages.index)

    fig, ax = plt.subplots(figsize=(12, 8))
    bars = ax.barh(range(len(sorted_percentages)), sorted_percentages.values,
                   color=plt.cm.viridis(np.linspace(0, 1, len(sorted_percentages))))

    ax.set_yticks(range(len(sorted_percentages)))
    ax.set_yticklabels(sorted_percentages.index)
    ax.set_xlabel(f'Percentage of Inspections with Observations (n={total_with_obs})', fontweight='bold')
    ax.set_title(title, fontweight='bold', pad=20)

    for i, (bar, percentage, count) in enumerate(zip(bars, sorted_percentages.values, sorted_counts.values)):
        width = bar.get_width()
        label_x = width + 0.5
        ax.text(label_x, bar.get_y() + bar.get_height()/2,
               f'{percentage:.1f}% (n={int(count)})',
               ha='left', va='center', fontweight='bold')

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(True, axis='x', alpha=0.3, linestyle='--')
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, save_name))
    plt.close()
    print(f"Saved summary chart: {save_name}")

def create_co_occurrence_heatmap(df, categories):
    """Generates a heatmap to show 483 deficiency co-occurrence."""
    print("Generating co-occurrence heatmap...")
    
    # Filter for rows with observations and ensure boolean/int type
    df_obs = df[df['long_description'].str.len() > 0].copy()
    for cat in categories:
        df_obs[cat] = df_obs[cat].astype(int)

    co_occurrence_matrix = df_obs[categories].T.dot(df_obs[categories])
    np.fill_diagonal(co_occurrence_matrix.values, 0)

    plt.figure(figsize=(10, 8))
    sns.heatmap(co_occurrence_matrix, annot=True, fmt='d', cmap='viridis')
    plt.title('Co-occurrence of 483 Deficiency Categories', fontsize=16, fontweight='bold')
    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=0)
    plt.tight_layout()
    save_path = os.path.join(OUTPUT_DIR, "483_co_occurrence_heatmap.png")
    plt.savefig(save_path)
    plt.close()
    print(f"Saved co-occurrence heatmap to {save_path}")

def analyze_trends_over_time(df, categories):
    """Analyzes and plots 483 deficiency trends over time."""
    print("Analyzing trends over time...")
    
    df_trends = df.copy()
    df_trends['year'] = pd.to_datetime(df_trends['inspection_end_date'], errors='coerce').dt.year
    df_trends.dropna(subset=['year'], inplace=True)
    df_trends['year'] = df_trends['year'].astype(int)

    yearly_trends = df_trends.groupby('year')[categories].sum().reset_index()
    
    plt.figure(figsize=(14, 8))
    for category in categories:
        sns.lineplot(data=yearly_trends, x='year', y=category, label=category, marker='o')
        
    plt.title('483 Deficiency Trends Over Time', fontsize=16, fontweight='bold')
    plt.xlabel('Year of Inspection')
    plt.ylabel('Number of Deficiencies Cited')
    plt.legend(title='Deficiency Category')
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    plt.tight_layout()
    save_path = os.path.join(OUTPUT_DIR, "483_deficiency_trends.png")
    plt.savefig(save_path)
    plt.close()
    print(f"Saved trend analysis chart to {save_path}")

# --- Main Execution Block ---
def main():
    """Main function to generate all final reports and visualizations for the 483 analysis."""
    print("🚀 Generating all final analysis and report components for 483s...")

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    try:
        df = pd.read_csv(CLASSIFIED_DATA_FILE)
    except FileNotFoundError:
        print(f"FATAL: Classified data not found at '{CLASSIFIED_DATA_FILE}'.")
        print("Please wait for the classification script (02) to finish.")
        return

    # These must match the categories from the classification script
    CATEGORIES = [
        "Procedures Not in Writing / Not Followed",
        "Inadequate Investigation of Discrepancies (CAPA)",
        "Data Integrity and Record-Keeping",
        "Deficient Cleaning, Sanitizing, and Maintenance",
        "Inadequate Equipment and Facilities",
        "Lack of Process or Equipment Validation",
        "Inadequate Testing and Quality Control"
    ]

    # Run all analysis functions
    create_summary_chart(df, CATEGORIES, 'Frequency of Primary 483 Deficiency Categories', '483_category_summary.png')
    create_co_occurrence_heatmap(df, CATEGORIES)
    analyze_trends_over_time(df, CATEGORIES)

    print("\n✅ Final report generation complete!")
    print(f"All charts and analyses have been saved to the '{OUTPUT_DIR}' directory.")

if __name__ == "__main__":
    main()