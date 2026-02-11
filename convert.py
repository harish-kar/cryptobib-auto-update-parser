import requests
import bibtexparser
import pandas as pd
import os
from bibtexparser.bparser import BibTexParser
from bibtexparser.customization import convert_to_unicode
from huggingface_hub import HfApi

def get_and_parse_cryptobib():
    # 1. Define URLs
    abbrev_url = "https://raw.githubusercontent.com/cryptobib/export/master/abbrev0.bib"
    crypto_url = "https://raw.githubusercontent.com/cryptobib/export/master/crypto.bib"

    print("Downloading files...")
    abbrev_response = requests.get(abbrev_url)
    abbrev_response.raise_for_status()
    
    crypto_response = requests.get(crypto_url)
    crypto_response.raise_for_status()

    # 2. Concatenate
    full_bib_string = abbrev_response.text + "\n" + crypto_response.text

    print("Parsing BibTeX...")
    parser = BibTexParser()
    parser.customization = convert_to_unicode
    bib_database = bibtexparser.loads(full_bib_string, parser=parser)
    
    # 3. Create DataFrame
    df = pd.DataFrame(bib_database.entries)
    
    # --- CHANGED: Keep ONLY these 3 columns ---
    # ID = BibTeX Key
    # title = Paper Title
    # author = Author List
    df = df[['ID', 'title', 'author']]
    
    # Clean up: Fill empty values with "" to prevent errors
    df.fillna("", inplace=True)
    
    print(f"Parsed {len(df)} papers. Kept only Key, Title, and Author.")
    return df

if __name__ == "__main__":
    try:
        # --- Part 1: Convert ---
        df = get_and_parse_cryptobib()
        
        output_filename = "crypto_papers.jsonl"
        df.to_json(output_filename, orient="records", lines=True, force_ascii=False)
        print(f"Saved locally to {output_filename}")

        # --- Part 2: Upload ---
        hf_token = os.environ.get("HF_TOKEN")
        
        if hf_token:
            print("HF_TOKEN found. Uploading...")
            api = HfApi()
            
            api.upload_file(
                path_or_fileobj=output_filename,
                path_in_repo=output_filename,
                repo_id="hk2617/cryptobib-search", 
                repo_type="dataset",
                token=hf_token
            )
            print("Upload complete!")
        else:
            print("Warning: HF_TOKEN not found. Skipping upload.")

    except Exception as e:
        print(f"An error occurred: {e}")
