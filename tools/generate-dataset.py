import os
import random
from datasets import load_dataset

RAW_DIR = "data/raw"

def save_docs(dataset_name, docs, prefix, field="text"):
    print(f"Saving {len(docs)} docs from {dataset_name}...")
    for i, doc_content in enumerate(docs):
        # Handle cases where content might be dict or list
        if isinstance(doc_content, dict):
            content = doc_content.get(field, "")
        else:
            content = doc_content
            
        if not content:
            continue
            
        filename = f"{RAW_DIR}/{prefix}_{i:03d}.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"Source: {dataset_name}\n\n")
            f.write(str(content))

def main():
    os.makedirs(RAW_DIR, exist_ok=True)
    
    # Clear existing files to avoid mixing fake data with real data
    print("Clearing old data...")
    import glob
    files = glob.glob(f"{RAW_DIR}/*")
    for f in files:
        os.remove(f)

    # 1. Multi-News (Long news articles)
    print("Downloading Multi-News...")
    try:
        ds = load_dataset("alexfabbri/multi_news", split="train[:50]", trust_remote_code=True) # Take 50
        save_docs("Multi-News", ds["document"], "multinews", field="document")
    except Exception as e:
        print(f"Error loading Multi-News: {e}")

    # 2. GovReport (Gov reports)
    print("Downloading GovReport...")
    try:
        ds = load_dataset("launch/gov_report", split="train[:20]", trust_remote_code=True) # Take 20 (they are long)
        save_docs("GovReport", ds["document"], "govreport", field="document")
    except Exception as e:
        print(f"Error loading GovReport: {e}")

    # 3. WikiQA (QA pairs - we'll index the candidate sentences as knowledge)
    print("Downloading WikiQA...")
    try:
        ds = load_dataset("microsoft/wiki_qa", split="train[:100]", trust_remote_code=True) # Take 100
        # WikiQA has 'question', 'answer', 'document_title', 'label'
        save_docs("WikiQA", ds["answer"], "wikiqa", field="answer")
    except Exception as e:
        print(f"Error loading WikiQA: {e}")

    # 4. Financial Phrasebank (Sentences)
    print("Downloading Financial Phrasebank...")
    try:
        # Use official dataset for reliability
        ds = load_dataset("financial_phrasebank", "sentences_allagree", split="train[:100]", trust_remote_code=True)
        save_docs("FinancialPhrasebank", ds["sentence"], "finphrase", field="sentence")
    except Exception as e:
        print(f"Error loading Financial Phrasebank: {e}")

    print("Done generating real data.")

if __name__ == "__main__":
    main()
