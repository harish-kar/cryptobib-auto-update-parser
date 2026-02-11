import requests
import bibtexparser
import pandas as pd
from bibtexparser.bparser import BibTexParser
from bibtexparser.customization import convert_to_unicode, author

def get_and_parse_cryptobib():
    # 1. Define the URLs
    abbrev_url = "https://cryptobib.di.ens.fr/abbrev0.bib" # '0' is the most detailed version
    crypto_url = "https://cryptobib.di.ens.fr/crypto.bib"

    print("Downloading abbrev0.bib...")
    abbrev_response = requests.get(abbrev_url)
    abbrev_response.raise_for_status()
    
    print("Downloading crypto.bib...")
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
    
    # Optional: clean up columns. 
    # 'ID' is the citation key (e.g., 'BonehG05'). 
    # 'ENTRYTYPE' is usually 'inproceedings' or 'article'.
    print(f"Successfully parsed {len(df)} entries.")
    
    return df

if __name__ == "__main__":
    df = get_and_parse_cryptobib()
    
    # Save as JSONL (preferred for Hugging Face as it handles large text better)
    df.to_json("crypto_papers.jsonl", orient="records", lines=True, force_ascii=False)
    
    # Or CSV if you prefer
    # df.to_csv("crypto_papers.csv", index=False, encoding='utf-8')
    print("Saved to crypto_papers.jsonl")
