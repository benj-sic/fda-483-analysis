# FDA 483 Analysis Pipeline

This project is an end-to-end data analysis pipeline that processes, classifies, and visualizes FDA Form 483 inspection observations related to drug and biologic products. The pipeline uses a large language model (LLM) to categorize observations, providing insights into common compliance issues.

## Features

-   **Data Preparation**: Merges and cleans FDA data from multiple sources.
-   **AI-Powered Classification**: Uses a LLM to automatically classify 483 observations into predefined categories.
-   **Insightful Reporting**: Generates a variety of visualizations, including:
    -   Frequency of deficiency categories
    -   Co-occurrence of different deficiencies
    -   Trends of deficiencies over time

## Project Structure

```
.
├── data/
│   ├── inspections_details.xlsx
│   ├── inspections_citations_details.xlsx
│   └── published_483s.xlsx
├── results/
│   ├── merged_483_drug_bio_data.csv
│   ├── classified_483_drug_bio_data.csv
│   └── final_483_report/
│       ├── 483_category_summary.png
│       ├── 483_co_occurrence_heatmap.png
│       └── 483_deficiency_trends.png
├── src/
│   ├── 01_prepare_483_data.py
│   ├── 02_classify_483s_with_ai.py
│   └── 03_generate_483_report.py
├── .env
└── README.md
```

## Setup and Installation

1.  **Clone the repository:**
    ```bash
    git clone <your-repository-url>
    cd <your-repository-directory>
    ```

2.  **Create a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install dependencies:**
    ```bash
    pip install pandas openpyxl google-generativeai python-dotenv seaborn matplotlib numpy
    ```

4.  **Set up your environment variables:**
    Create a file named `.env` in the root of the project directory and add your Google API key:
    ```
    GOOGLE_API_KEY="your_google_api_key"
    ```

## Usage

The scripts are designed to be run in a specific order.

1.  **Prepare the Data:**
    This script merges and cleans the initial data.
    ```bash
    python src/01_prepare_483_data.py
    ```

2.  **Classify Observations with AI:**
    This script uses the LLM to classify the 483 observations.
    ```bash
    python src/02_classify_483s_with_ai.py
    ```

3.  **Generate the Final Report:**
    This script generates the charts and visualizations.
    ```bash
    python src/03_generate_483_report.py
    ```
    The final report images will be saved in the `results/final_483_report` directory.

## Dependencies

-   pandas
-   openpyxl
-   google-generativeai
-   python-dotenv
-   seaborn
-   matplotlib
-   numpy