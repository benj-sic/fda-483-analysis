import pandas as pd
import google.generativeai as genai
import time
import json
import logging
import os
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed

# --- Basic Setup ---
load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Global Variables ---
API_KEY = os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    logging.error("FATAL: GOOGLE_API_KEY environment variable not set.")
    exit()

# --- MODIFIED: Pointing to the new, more focused dataset ---
INPUT_FILE = "results/merged_483_drug_bio_data.csv"
OUTPUT_FILE = "results/classified_483_drug_bio_data.csv" # Updated output file as well
RATE_LIMIT_DELAY = 0.1
MAX_WORKERS = 50


# --- 483 Deficiency Categories Schema ---
CATEGORIES = [
    "Procedures Not in Writing / Not Followed",
    "Inadequate Investigation of Discrepancies (CAPA)",
    "Data Integrity and Record-Keeping",
    "Deficient Cleaning, Sanitizing, and Maintenance",
    "Inadequate Equipment and Facilities",
    "Lack of Process or Equipment Validation",
    "Inadequate Testing and Quality Control"
]

# --- Prompt Design for 483 Analysis ---
def create_483_analysis_prompt(observation_text: str) -> str:
    """
    Creates a prompt for Gemini to perform a multi-label classification
    of the full text from a Form 483 observation list.
    """
    prompt = f"""
You are an expert FDA regulatory and compliance analyst. Your task is to perform a comprehensive, multi-label classification of the following list of FDA Form 483 observations from a single inspection.

Read the entire text carefully. The text may contain multiple observations separated by '---'. Based on the full text, identify all applicable deficiency categories from the list provided.

**Classification Categories:**
- **Procedures Not in Writing / Not Followed:** SOPs are missing, inadequate, or not being followed by staff.
- **Inadequate Investigation of Discrepancies (CAPA):** Failures, deviations, or out-of-spec results are not properly investigated; Corrective and Preventive Actions (CAPA) are deficient.
- **Data Integrity and Record-Keeping:** Records are not accurate, complete, or secure. Includes issues with master production and control records.
- **Deficient Cleaning, Sanitizing, and Maintenance:** Equipment and facilities are not properly cleaned or maintained, posing contamination risks.
- **Inadequate Equipment and Facilities:** The design, size, location, or maintenance of equipment or the facility itself is deficient.
- **Lack of Process or Equipment Validation:** Manufacturing processes or equipment have not been validated to ensure consistent product quality.
- **Inadequate Testing and Quality Control:** Insufficient or inadequate testing of raw materials or finished products.

**Instructions:**
1.  Analyze the complete text of observations provided below.
2.  For each of the 7 categories, determine if it is a reason for any of the observations.
3.  You MUST respond with a valid JSON object only, with no additional text or explanations before or after the JSON.

**JSON Output Format:**
{{
  "analysis_summary": {{
    "Procedures Not in Writing / Not Followed": true/false,
    "Inadequate Investigation of Discrepancies (CAPA)": true/false,
    "Data Integrity and Record-Keeping": true/false,
    "Deficient Cleaning, Sanitizing, and Maintenance": true/false,
    "Inadequate Equipment and Facilities": true/false,
    "Lack of Process or Equipment Validation": true/false,
    "Inadequate Testing and Quality Control": true/false
  }}
}}

**Observation Text to Analyze:**
---
{observation_text}
---

Respond with only the JSON object.
"""
    return prompt

# --- Main Logic ---
def analyze_483_with_gemini(inspection_id: int, text: str, model):
    """
    Worker function to call the Gemini API for a single inspection's observations.
    """
    if not isinstance(text, str) or len(text.strip()) < 20:
        result_row = {'inspection_id': inspection_id, 'error': 'No text to analyze.'}
        for category in CATEGORIES:
            result_row[category] = False
        return result_row

    try:
        time.sleep(RATE_LIMIT_DELAY)
        prompt = create_483_analysis_prompt(text)
        response = model.generate_content(prompt)

        clean_response = response.text.strip().replace('```json', '').replace('```', '')
        data = json.loads(clean_response)

        result_row = {'inspection_id': inspection_id, 'error': None}
        analysis_summary = data.get('analysis_summary', {})

        for category in CATEGORIES:
            result_row[category] = analysis_summary.get(category, False)

        return result_row

    except json.JSONDecodeError:
        logging.warning(f"JSON parsing failed for inspection {inspection_id}. Response was not valid JSON.")
        return {'inspection_id': inspection_id, 'error': 'JSONDecodeError'}
    except Exception as e:
        if "429" in str(e):
             logging.warning(f"Quota error for inspection {inspection_id}. The script will continue.")
        else:
            logging.error(f"An error occurred while processing inspection {inspection_id}: {e}")
        return {'inspection_id': inspection_id, 'error': str(e)}

def main():
    """
    Main function to run the AI-powered 483 analysis pipeline.
    """
    logging.info("🚀 Starting AI-Powered 483 Classification (Drugs and Biologics).")

    try:
        df = pd.read_csv(INPUT_FILE)
        df_to_analyze = df[df['long_description'].notna() & (df['long_description'].str.strip() != '')].copy()
        logging.info(f"Loaded {len(df)} inspections, found {len(df_to_analyze)} with 483 observations to analyze.")
    except FileNotFoundError:
        logging.error(f"FATAL: Input file not found at '{INPUT_FILE}'. Please run script 01 first.")
        return

    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')

    all_results = []

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_inspection = {
            executor.submit(analyze_483_with_gemini, row['inspection_id'], row['long_description'], model): row
            for index, row in df_to_analyze.iterrows()
        }

        for i, future in enumerate(as_completed(future_to_inspection)):
            result = future.result()
            all_results.append(result)
            inspection_id = result.get('inspection_id', 'Unknown')
            status = "✓" if result.get('error') is None else "✗"
            logging.info(f"({i+1}/{len(df_to_analyze)}) {status} Processed Inspection ID: {inspection_id}")

    results_df = pd.DataFrame(all_results)
    final_df = pd.merge(df, results_df, on='inspection_id', how='left')

    for category in CATEGORIES:
        if category in final_df.columns:
            final_df[category] = final_df[category].fillna(False)

    final_df.to_csv(OUTPUT_FILE, index=False, encoding='utf-8')
    logging.info(f"🎉 Analysis complete! Results saved to '{OUTPUT_FILE}'.")

    summary_df = final_df[[c for c in CATEGORIES if c in final_df.columns]]
    print("\n--- AI-Powered 483 Analysis Summary (Drugs and Biologics) ---")
    print(summary_df.sum())
    print("-----------------------------------")


if __name__ == "__main__":
    main()