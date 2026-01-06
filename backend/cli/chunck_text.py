import pdfplumber
import nltk
import re
import json
from typing import List, Dict

# nltk.download("punkt")
from nltk.tokenize import sent_tokenize


# ============================================================
# Text Cleaning
# ============================================================
# def clean_text(text: str) -> str:
#     if not text:
#         return ""

#     # Normalize line breaks
#     text = text.replace("\r", "\n")

#     # Remove standalone page numbers
#     text = re.sub(r"\n\s*\d+\s*$", "", text)

#     # Fix broken lines inside sentences
#     text = re.sub(r"([a-zA-Z,;:])\n([a-zA-Z(])", r"\1 \2", text)

#     # Normalize bullets
#     text = text.replace("•", "-")
#     text = re.sub(r"\n\s*o\s*", "\n- ", text)

#     # Remove extra whitespace
#     text = re.sub(r"[ \t]+", " ", text)
#     text = re.sub(r"\n{3,}", "\n\n", text)

#     return text.strip()


# ============================================================
# Step 1: Read PDF using pdfplumber
# ============================================================
# def read_pdf_plumber(pdf_path: str) -> str:
#     pages_text = []

#     with pdfplumber.open(pdf_path) as pdf:
#         for page in pdf.pages:
#             text = page.extract_text()
#             if text:
#                 text = clean_text(text)
#                 pages_text.append(text)

#     return "\n".join(pages_text)


def read_pdf_plumber(pdf_path: str, skip_pages: int = 4) -> str:
    """
    Reads a PDF using pdfplumber and returns cleaned text.

    Args:
        pdf_path (str): Path to PDF file
        skip_pages (int): Number of initial pages to skip (default: 4)

    Returns:
        str: Cleaned text from remaining pages
    """

    pages_text = []

    with pdfplumber.open(pdf_path) as pdf:
        for page_number, page in enumerate(pdf.pages):
            if page_number < skip_pages:
                continue

            text = page.extract_text()
            if text:
                # text = clean_text(text)
                pages_text.append(text)

    return "\n".join(pages_text)


# ============================================================
# Step 2: Chunk text by Department → Section
# ============================================================
def create_chunks_from_text(text: str) -> List[Dict]:
    """
    Create semantic chunks suitable for chatbot & embeddings
    """

    chunks = []

    # Normalize whitespace again
    text = re.sub(r"\s+", " ", text).strip()

    # Match department headers
    # dept_pattern = re.compile(
    #     r"(\d+\.\s*(?:Department|Institute|Center|Centre) of [A-Za-z &]+)",
    #     re.IGNORECASE,
    # )

    dept_pattern = re.compile(
        r"(\d+\.\s*(?:Department|Institute|Center|Centre)(?:\s+of)? [A-Za-z &]+)",
        re.IGNORECASE,
    )

    dept_splits = dept_pattern.split(text)

    for i in range(1, len(dept_splits), 2):
        dept_title = dept_splits[i].strip()
        dept_body = dept_splits[i + 1].strip()

        department_name = re.sub(r"^\d+\.\s+", "", dept_title)

        # Match section headers
        section_pattern = re.compile(
            r"(\d+\.\d+\s+(Introduction|Offered Programs|Eligibility Criteria|Faculty Members))",
            re.IGNORECASE,
        )

        section_splits = section_pattern.split(dept_body)

        for j in range(1, len(section_splits), 3):
            section_header = section_splits[j].strip()
            section_name = section_splits[j + 1].strip()
            section_content = section_splits[j + 2].strip()

            if len(section_content) < 50:
                continue

            chunk_text = f"{department_name} - {section_name}: {section_content}"

            chunks.append(
                {
                    "department": department_name,
                    "section": section_name,
                    "text": chunk_text,
                }
            )

    return chunks


# ============================================================
# Step 3: Optional — Further split very long chunks
# ============================================================
def split_long_chunks(chunks: List[Dict], max_sentences: int = 8) -> List[Dict]:

    final_chunks = []

    for chunk in chunks:
        sentences = sent_tokenize(chunk["text"])

        if len(sentences) <= max_sentences:
            final_chunks.append(chunk)
        else:
            for i in range(0, len(sentences), max_sentences):
                sub_text = " ".join(sentences[i : i + max_sentences])
                final_chunks.append(
                    {
                        "department": chunk["department"],
                        "section": chunk["section"],
                        "text": sub_text,
                    }
                )

    return final_chunks


# ============================================================
# Main Runner
# ============================================================
if __name__ == "__main__":
    PDF_PATH = "docs/UET lahore Document.pdf"

    print("📄 Reading PDF...")
    raw_text = read_pdf_plumber(PDF_PATH)

    print("✂️ Creating semantic chunks...")
    chunks = create_chunks_from_text(raw_text)

    # print("🧠 Splitting long chunks...")
    # chunks = split_long_chunks(chunks)

    # print(f"✅ Total chunks created: {len(chunks)}")

    # Save chunks to JSON for inspection
    with open("uet_chunks.json", "w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=2, ensure_ascii=False)

    print("💾 Chunks saved to uet_chunks.json")
