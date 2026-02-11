import requests
import bibtexparser
import pandas as pd
import os
from bibtexparser.bparser import BibTexParser
from bibtexparser.customization import convert_to_unicode
from huggingface_hub import HfApi

def get_and_parse_cryptobib():
    # --- CHANGED: Use the official GitHub Raw URLs ---
    abbrev_url = "https://cryptobib.di.ens.fr/cryptobib/static/files/abbrev0.bib" # '0' is the most detailed version
    crypto_url = "https://cryptobib.di.ens.fr/cryptobib/static/files/crypto.bib"

    print(f"Downloading abbrev0.bib from {abbrev_url}...")
    abbrev_response = requests.get(abbrev_url)
    abbrev_response.raise_for_status()
    
    print(f"Downloading crypto.bib from {crypto_url}...")
    crypto_response = requests.get(crypto_url)
    crypto_response.raise_for_status()

    # 2. Concatenate: Abbrev MUST come first
    # We add a newline character in between just to be safe
    full_bib_string = abbrev_response.text + "\n" + crypto_response.text

    print("Parsing BibTeX data (this may take a moment)...")
    
    # 3. Configure the parser
    # We use common customizations to handle LaTeX characters (e.g., \"{o} -> ö)
    parser = BibTexParser()
    parser.customization = convert_to_unicode
    
    # 4. Parse the combined string
    bib_database = bibtexparser.loads(full_bib_string, parser=parser)
    
    # 5. Convert to DataFrame
    df = pd.DataFrame(bib_database.entries)
    
    print(f"Successfully parsed {len(df)} entries.")
    
    return df

if __name__ == "__main__":
    # --- Part 1: Convert ---
    try:
        df = get_and_parse_cryptobib()
        
        output_filename = "crypto_papers.jsonl"
        df.to_json(output_filename, orient="records", lines=True, force_ascii=False)
        print(f"Saved locally to {output_filename}")

        # --- Part 2: Upload to Hugging Face ---
        # This gets the token from your GitHub Secrets (or local env if you set it)
        hf_token = os.environ.get("HF_TOKEN")
        
        if hf_token:
            print("HF_TOKEN found. Uploading to Hugging Face...")
            api = HfApi()
            
            # UPLOAD COMMAND
            # REPLACE 'YOUR_USERNAME/YOUR_DATASET_NAME' BELOW!
            api.upload_file(
                path_or_fileobj=output_filename,
                path_in_repo=output_filename,
                repo_id="hk2617/cryptobib-search",  # <--- DON'T FORGET TO UPDATE THIS!
                repo_type="dataset",
                token=hf_token
            )
            print("Upload complete!")
        else:
            print("Warning: HF_TOKEN not found in environment variables. If you are running this locally, that's expected. If on GitHub, check your Secrets.")

    except Exception as e:
        print(f"An error occurred: {e}")
