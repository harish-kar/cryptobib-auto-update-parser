import requests
import bibtexparser
import pandas as pd
import os
from bibtexparser.bparser import BibTexParser
from bibtexparser.customization import convert_to_unicode
from huggingface_hub import HfApi

def get_and_parse_cryptobib():
    # 1. Define the URLs (using GitHub Raw for reliability)
    abbrev_url = "https://raw.githubusercontent.com/cryptobib/export/master/abbrev0.bib"
    crypto_url = "https://raw.githubusercontent.com/cryptobib/export/master/crypto.bib"

    print(f"Downloading abbrev0.bib from {abbrev_url}...")
    abbrev_response = requests.get(abbrev_url)
    abbrev_response.raise_for_status()
    
    print(f"Downloading crypto.bib from {crypto_url}...")
    crypto_response = requests.get(crypto_url)
    crypto_response.raise_for_status()

    # 2. Concatenate: Abbrev MUST come first
    full_bib_string = abbrev_response.text + "\n" + crypto_response.text

    print("Parsing BibTeX data (this may take a moment)...")
    
    # 3. Configure the parser
    parser = BibTexParser()
    parser.customization = convert_to_unicode
    
    # 4. Parse
    bib_database = bibtexparser.loads(full_bib_string, parser=parser)
    
    # 5. Convert to DataFrame
    df = pd.DataFrame(bib_database.entries)
    
    # --- THE FIX: Replace 'NaN' (empty) with empty strings "" ---
    # This prevents the "Couldn't cast string to null" error on Hugging Face
    df.fillna("", inplace=True)
    
    print(f"Successfully parsed {len(df)} entries.")
    
    return df

if __name__ == "__main__":
    try:
        # --- Part 1: Convert ---
        df = get_and_parse_cryptobib()
        
        output_filename = "crypto_papers.jsonl"
        # Force all data to string type just to be extra safe
        df = df.astype(str)
        
        df.to_json(output_filename, orient="records", lines=True, force_ascii=False)
        print(f"Saved locally to {output_filename}")

        # --- Part 2: Upload ---
        hf_token = os.environ.get("HF_TOKEN")
        
        if hf_token:
            print("HF_TOKEN found. Uploading to Hugging Face...")
            api = HfApi()
            
            api.upload_file(
                path_or_fileobj=output_filename,
                path_in_repo=output_filename,
                repo_id="hk2617/cryptobib-search", 
                repo_type="dataset",
                token=hf_token
            )
            print("Upload complete! Check your dataset viewer in a few minutes.")
        else:
            print("Warning: HF_TOKEN not found. Skipping upload.")

    except Exception as e:
        print(f"An error occurred: {e}")
