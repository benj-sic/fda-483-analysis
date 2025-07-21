import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

def analyze_and_plot_trends(
    data_folder='results',
    input_filename='classified_483_drug_bio_data.csv',
    output_image_path='citation_trends.png',
    category_column='classification'  # <-- **** CHANGE THIS IF YOUR COLUMN IS NAMED DIFFERENTLY ****
    ):
    """
    Analyzes and plots the trends of FDA 483 citation categories over time.

    Args:
        data_folder (str): The folder where the input data is stored.
        input_filename (str): The name of the input CSV file.
        output_image_path (str): The path to save the output plot image.
        category_column (str): The name of the column containing the citation categories.
    """
    # Construct the full path to the data file
    classified_data_path = os.path.join(data_folder, input_filename)

    # Load the classified data
    try:
        df = pd.read_csv(classified_data_path)
    except FileNotFoundError:
        print(f"Error: The file {classified_data_path} was not found.")
        print("Please ensure the script is run from the 'fda_form_483s' directory.")
        return
    except Exception as e:
        print(f"An error occurred while reading the CSV: {e}")
        return

    # --- Data Preparation ---
    # Verify the category column exists
    if category_column not in df.columns:
        print(f"Error: Column '{category_column}' not found in the CSV file.")
        print(f"Available columns are: {list(df.columns)}")
        print("Please update the 'category_column' variable in the script.")
        return

    # Convert 'inspection_end_date' to datetime objects
    df['inspection_end_date'] = pd.to_datetime(df['inspection_end_date'], errors='coerce')

    # Drop rows where date conversion failed
    df.dropna(subset=['inspection_end_date'], inplace=True)

    # Extract the year from the inspection date
    df['year'] = df['inspection_end_date'].dt.year

    # --- Trend Analysis ---
    # Group by year and category to count citations
    trends = df.groupby(['year', category_column]).size().reset_index(name='count')

    # Pivot the data to get years as the index and categories as columns
    trends_pivot = trends.pivot(index='year', columns=category_column, values='count').fillna(0)

    # --- Visualization ---
    plt.style.use('seaborn-v0_8-whitegrid')
    fig, ax = plt.subplots(figsize=(15, 10))

    trends_pivot.plot(kind='line', marker='o', ax=ax)

    # --- Formatting the Plot ---
    ax.set_title('Annual Trends of FDA 483 Citation Categories', fontsize=18, fontweight='bold')
    ax.set_xlabel('Year', fontsize=12)
    ax.set_ylabel('Number of Citations', fontsize=12)
    ax.legend(title='Citation Category', bbox_to_anchor=(1.05, 1), loc='upper left')
    ax.grid(True, which='both', linestyle='--', linewidth=0.5)

    # Ensure the output directory exists
    output_dir = os.path.dirname(output_image_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Save the plot to a file
    plt.tight_layout()
    plt.savefig(output_image_path, dpi=300)
    print(f"Trend analysis plot saved to {output_image_path}")

if __name__ == '__main__':
    # This allows the script to be run from the command line from the root project directory
    # The output plot will be saved in the 'results' folder.
    analyze_and_plot_trends(output_image_path='results/citation_trends.png')