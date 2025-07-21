import os
import pandas as pd
import asyncio
import time
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.output_parsers import PydanticOutputParser
from tqdm.asyncio import tqdm

# --- 1. Define the desired, structured output format ---
class GranularClassification(BaseModel):
    """A structured model for a detailed classification of an FDA 483 observation."""
    primary_category: str = Field(description="The main category of the observation.")
    sub_category: str = Field(description="A specific, detailed sub-category of the issue.")
    severity: str = Field(description="The estimated severity of the finding: 'Critical', 'Major', or 'Minor'.")
    reasoning: str = Field(description="A brief justification for the chosen categories and severity.")

# --- 2. Asynchronous Classification Function for a single row ---
async def process_row(row, chain, semaphore):
    """Asynchronously processes a single row with semaphore to limit concurrency."""
    async with semaphore:
        index, data = row
        text = data['text']

        if not text.strip():
            return {'primary_category': 'No Text', 'sub_category': 'No Text', 'severity': 'N/A', 'reasoning': 'Skipped due to empty observation text.'}

        try:
            # Use ainvoke for asynchronous call
            response = await chain.ainvoke({"observation_text": text})
            return response.model_dump()
        except Exception as e:
            # Simple retry logic for transient errors
            print(f"\n  - Error on row {index + 1}. Retrying in 5s. Error: {e}")
            await asyncio.sleep(5)
            try:
                response = await chain.ainvoke({"observation_text": text})
                return response.model_dump()
            except Exception as e_retry:
                print(f"\n  - Retry failed for row {index + 1}. Skipping. Error: {e_retry}")
                return {'primary_category': 'Error', 'sub_category': 'Error', 'severity': 'Error', 'reasoning': str(e_retry)}

# --- 3. Main Asynchronous Orchestrator ---
async def classify_final(data_folder='results', input_filename='merged_483_drug_bio_data.csv', output_filename='classified_483s_final.csv'):
    """
    Classifies FDA 483 observations concurrently, respecting API rate limits and showing progress.
    """
    start_time = time.time()
    load_dotenv()
    if not os.getenv("GOOGLE_API_KEY"):
        print("Error: GOOGLE_API_KEY not found.")
        return

    # Load data
    input_path = os.path.join(data_folder, input_filename)
    df = pd.read_csv(input_path)
    df['text'] = (df['short_description'].fillna('') + ' ' + df['long_description'].fillna('')).str.strip()
    print("Data loaded and 'text' column prepared.")

    # Set up LangChain components
    model = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest", temperature=0)
    parser = PydanticOutputParser(pydantic_object=GranularClassification)
    prompt = PromptTemplate(
        template="You are an expert FDA compliance consultant. Analyze the following FDA 483 observation text. Your task is to identify the single most significant finding and classify it. Provide your output as a single JSON object. Do not return a list.\n{format_instructions}\n**Observation Text to Analyze:**\n{observation_text}",
        input_variables=["observation_text"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )
    chain = prompt | model | parser

    # Concurrency Control: Set a safe number of parallel requests
    CONCURRENT_REQUESTS = 40
    semaphore = asyncio.Semaphore(CONCURRENT_REQUESTS)

    # Create a list of tasks to run
    tasks = [process_row(row, chain, semaphore) for row in df.iterrows()]

    # Run tasks with tqdm for a visual progress bar
    print(f"Starting processing of {len(df)} rows with a limit of {CONCURRENT_REQUESTS} parallel requests...")
    results = await tqdm.gather(*tasks, desc="Classifying Observations")

    # Combine results and save
    results_df = pd.DataFrame(results)
    final_df = pd.concat([df.reset_index(drop=True), results_df.reset_index(drop=True)], axis=1)
    output_path = os.path.join(data_folder, output_filename)
    final_df.to_csv(output_path, index=False)

    end_time = time.time()
    print(f"\nProcessing complete!")
    print(f"Data saved to {output_path}")
    print(f"Total time taken: {(end_time - start_time)/60:.2f} minutes.")

if __name__ == '__main__':
    # Make sure 'tqdm' is installed: pip install tqdm
    # Stop any previous script and run this one.
    asyncio.run(classify_final())