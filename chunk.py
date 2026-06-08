"""
chunk.py — Chunking Pipeline
Splits cleaned documents into chunks using a pure-Python recursive character splitter.
Spec: chunk_size=400, chunk_overlap=75, splits on paragraph > sentence > space > char.
Prepends a [Professor: X | Source: filename] header to every chunk.
"""

import re
from ingest import load_documents


# --- Config (matches planning.md) ---
CHUNK_SIZE = 400
CHUNK_OVERLAP = 75
SEPARATORS = ["\n\n", "\n", ". ", " ", ""]


# --- Pure-Python recursive text splitter (replaces LangChain dependency) ---

def _merge_splits(splits: list, separator: str, chunk_size: int, chunk_overlap: int) -> list:
    """Merge a flat list of small splits into chunks, adding overlap between chunks."""
    chunks = []
    current: list = []
    current_len = 0
    sep_len = len(separator)

    for s in splits:
        s_len = len(s)
        add_sep = sep_len if current else 0

        if current and current_len + add_sep + s_len > chunk_size:
            chunks.append(separator.join(current))

            # Keep trailing splits that fit within the overlap window for next chunk
            overlap: list = []
            overlap_len = 0
            for p in reversed(current):
                p_cost = len(p) + (sep_len if overlap else 0)
                if overlap_len + p_cost <= chunk_overlap:
                    overlap.insert(0, p)
                    overlap_len += p_cost
                else:
                    break
            current = overlap
            current_len = overlap_len

        current.append(s)
        current_len += (sep_len if len(current) > 1 else 0) + s_len

    if current:
        chunks.append(separator.join(current))

    return [c for c in chunks if c.strip()]


def _recursive_split(text: str, separators: list, chunk_size: int, chunk_overlap: int) -> list:
    """Recursively split text by trying separators in priority order."""
    if len(text) <= chunk_size:
        return [text] if text.strip() else []

    # Find the first separator present in the text
    chosen_sep = ""
    remaining_seps = []
    for i, sep in enumerate(separators):
        if sep == "" or sep in text:
            chosen_sep = sep
            remaining_seps = separators[i + 1:]
            break

    # Hard-cut fallback when no separator works
    if chosen_sep == "" and not remaining_seps:
        step = max(1, chunk_size - chunk_overlap)
        return [text[i: i + chunk_size] for i in range(0, len(text), step) if text[i: i + chunk_size].strip()]

    raw = text.split(chosen_sep) if chosen_sep else list(text)

    # Recursively split any piece still over chunk_size
    flat: list = []
    for piece in raw:
        if not piece.strip():
            continue
        if len(piece) > chunk_size and remaining_seps:
            flat.extend(_recursive_split(piece, remaining_seps, chunk_size, chunk_overlap))
        else:
            flat.append(piece)

    return _merge_splits(flat, chosen_sep, chunk_size, chunk_overlap)


def split_text(text: str, chunk_size: int = CHUNK_SIZE, chunk_overlap: int = CHUNK_OVERLAP) -> list:
    """Public entry point matching LangChain's RecursiveCharacterTextSplitter interface."""
    return _recursive_split(text, SEPARATORS, chunk_size, chunk_overlap)


def extract_professor(filename: str) -> str:
    """
    Parse the professor name from the filename.
    Convention used in /docs filenames:
      rmp_thornton_reviews.txt       -> Thornton
      reddit_ics33_thornton_curve.txt -> Thornton
      reddit_ics46_shindler_ics53_wongma.txt -> Shindler/Wong Ma
      rmp_wongma_reviews.txt         -> Wong Ma
      thornton_ics46_course_reference.txt -> Thornton
    Returns "Unknown" if no known professor is found.
    """
    name_lower = filename.lower()

    professors = {
        "thornton": "Thornton",
        "thorton": "Thornton",   # handles misspelled filename rmp_thorton_reviews.txt
        "shindler": "Shindler",
        "wongma": "Wong Ma",
        "wong_ma": "Wong Ma",
        "klefstad": "Klefstad",
    }

    found = []
    for key, display in professors.items():
        if key in name_lower and display not in found:
            found.append(display)

    if found:
        return "/".join(found)
    return "Unknown"


def build_header(professor: str, source: str) -> str:
    """Build the metadata header prepended to every chunk."""
    return f"[Professor: {professor} | Source: {source}]\n"


def chunk_documents(documents: list[dict]) -> list[dict]:
    """
    Split each document into chunks and prepend metadata headers.
    Returns a list of dicts:
      {
        "text": header + chunk_text,
        "source": filename,
        "professor": professor_name,
        "chunk_index": int,
      }
    """
    all_chunks = []

    for doc in documents:
        source = doc["source"]
        professor = extract_professor(source)
        header = build_header(professor, source)

        raw_chunks = split_text(doc["text"])

        for i, chunk_text in enumerate(raw_chunks):
            chunk_text = chunk_text.strip()
            if not chunk_text:  # skip empty strings
                continue

            full_text = header + chunk_text

            all_chunks.append(
                {
                    "text": full_text,
                    "source": source,
                    "professor": professor,
                    "chunk_index": i,
                }
            )

    return all_chunks


def print_chunk_sample(chunks: list[dict], n: int = 5) -> None:
    """Print n evenly-spaced chunks for manual inspection."""
    if not chunks:
        print("No chunks to display.")
        return

    step = max(1, len(chunks) // n)
    sample_indices = [i * step for i in range(n)]

    print(f"\n{'='*60}")
    print(f"CHUNK INSPECTION — {n} samples (total chunks: {len(chunks)})")
    print(f"{'='*60}")

    for idx in sample_indices:
        chunk = chunks[idx]
        print(f"\n[Chunk #{idx} | Source: {chunk['source']} | Professor: {chunk['professor']}]")
        print("-" * 50)
        print(chunk["text"])
        print(f"(length: {len(chunk['text'])} chars)")


if __name__ == "__main__":
    print("=== Chunking Pipeline ===\n")

    # Step 1: Load documents
    documents = load_documents()

    # Step 2: Chunk them
    chunks = chunk_documents(documents)

    # Step 3: Inspect
    print_chunk_sample(chunks, n=5)

    # Step 4: Count and sanity-check
    print(f"\n{'='*60}")
    print(f"TOTAL CHUNKS: {len(chunks)}")
    if len(chunks) < 50:
        print("  ⚠️  WARNING: fewer than 50 chunks — chunks may be too large.")
        print("     Consider reducing CHUNK_SIZE or check that documents loaded correctly.")
    elif len(chunks) > 2000:
        print("  ⚠️  WARNING: more than 2000 chunks — chunks may be too small.")
        print("     Consider increasing CHUNK_SIZE.")
    else:
        print("  OK: Chunk count is in the healthy range (50-2000).")

    # Step 5: Check for known bad patterns
    print("\n--- Quality checks ---")
    empty = [c for c in chunks if not c["text"].strip()]
    fragments = [c for c in chunks if len(c["text"]) < 60]
    print(f"  Empty chunks:    {len(empty)}")
    print(f"  Very short (<60 chars): {len(fragments)}")
    if fragments:
        print("  Sample short chunks:")
        for f in fragments[:3]:
            print(f"    [{f['source']}] {repr(f['text'])}")