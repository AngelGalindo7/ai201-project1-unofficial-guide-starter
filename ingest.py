"""
ingest.py — Document Ingestion Pipeline
Loads and cleans all .txt files from the /docs folder.
Returns a list of {"text": str, "source": filename} dicts.
"""

import os
import re


DOCS_FOLDER = "documents"


def clean_text(text: str) -> str:
    """
    Remove boilerplate and artifacts from raw document text.
    Keeps: review text, opinions, professor names, course numbers.
    Removes: HTML tags, HTML entities, excess whitespace.
    """
    # Remove any residual HTML tags (e.g. if copy-paste included markup)
    text = re.sub(r"<[^>]+>", "", text)

    # Decode common HTML entities
    html_entities = {
        "&amp;": "&",
        "&nbsp;": " ",
        "&lt;": "<",
        "&gt;": ">",
        "&quot;": '"',
        "&#39;": "'",
        "&apos;": "'",
    }
    for entity, char in html_entities.items():
        text = text.replace(entity, char)

    # Remove lines that look like navigation / boilerplate
    # (short lines with no alphabetic content, or known nav patterns)
    nav_patterns = [
        r"^\s*Read more\s*$",
        r"^\s*Share\s*$",
        r"^\s*Reply\s*$",
        r"^\s*\d+ (comments?|points?|upvotes?)\s*$",
        r"^\s*Cookie(s| policy| banner)\s*$",
        r"^\s*Sign (in|up)\s*$",
        r"^\s*Log (in|out)\s*$",
        r"^\s*\[deleted\]\s*$",
        r"^\s*\[removed\]\s*$",
        r"^\s*r/\w+\s*$",                                     # subreddit header (r/UCI)
        r"^\s*[•·]\s*$",                                      # Reddit bullet separators
        r"^\s*\d+[ydhm]\s+ago\s*$",                          # timestamps: 3y ago, 2h ago
        r"^\s*\d+\s+(year|month|week|day|hour)s?\s+ago\s*$", # timestamps: 3 years ago
        r"^\s*\d+\s*$",                                       # standalone vote counts
        r"^\s*OP\s*$",                                        # Reddit OP label
        r"^\s*u/\S+\s+avatar\s*$",                           # Reddit avatar lines
        r"^\s*u/\S+\s*$",                                     # bare u/username lines
        r"^\s*Comments Section\s*$",                          # Reddit comments header
        r"^\s*\w+_\w[\w_]*\s*$",                              # Reddit usernames (e.g. Old_Caterpillar_6504)
    ]
    lines = text.splitlines()
    cleaned_lines = []
    for line in lines:
        skip = False
        for pattern in nav_patterns:
            if re.match(pattern, line, re.IGNORECASE):
                skip = True
                break
        if not skip:
            cleaned_lines.append(line)
    text = "\n".join(cleaned_lines)

    # Collapse multiple blank lines into one
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Strip leading/trailing whitespace
    text = text.strip()

    return text


def load_documents(docs_folder: str = DOCS_FOLDER) -> list[dict]:
    """
    Load all .txt files from docs_folder.
    Returns a list of dicts: {"text": cleaned_text, "source": filename}
    """
    if not os.path.exists(docs_folder):
        raise FileNotFoundError(
            f"Docs folder '{docs_folder}' not found. "
            "Make sure you're running this from the project root "
            "and that your .txt files are in the /docs folder."
        )

    documents = []
    txt_files = sorted(f for f in os.listdir(docs_folder) if f.endswith(".txt"))

    if not txt_files:
        raise ValueError(f"No .txt files found in '{docs_folder}'.")

    for filename in txt_files:
        filepath = os.path.join(docs_folder, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            raw_text = f.read()

        cleaned = clean_text(raw_text)

        if not cleaned:
            print(f"  WARNING: '{filename}' is empty after cleaning — skipping.")
            continue

        documents.append({"text": cleaned, "source": filename})
        print(f"  Loaded: {filename} ({len(cleaned)} chars after cleaning)")

    print(f"\nTotal documents loaded: {len(documents)}")
    return documents


if __name__ == "__main__":
    print("=== Ingestion Pipeline ===\n")
    docs = load_documents()

    # Spot-check: print the first document in full so you can verify it looks clean
    if docs:
        print("\n--- Spot-check: first document ---")
        print(f"Source: {docs[0]['source']}")
        print(docs[0]["text"][:1000])
        print("..." if len(docs[0]["text"]) > 1000 else "")