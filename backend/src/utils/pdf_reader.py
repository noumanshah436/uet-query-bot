import pdfplumber


def read_pdf(pdf_path: str, skip_pages: int = 4) -> str:
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
