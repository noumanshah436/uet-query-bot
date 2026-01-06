import re


def chunk_text(text: str) -> list[str]:
    """
    Create semantic chunks and return only the text content of each chunk.
    """

    chunks = []

    # Normalize whitespace
    text = re.sub(r"\s+", " ", text).strip()

    # Match department/institute/centre headers (with optional 'of')
    dept_pattern = re.compile(
        r"(\d+\.\s*(?:Department|Institute|Center|Centre)(?:\s+of)? [A-Za-z &]+)",
        re.IGNORECASE,
    )

    dept_splits = dept_pattern.split(text)

    for i in range(1, len(dept_splits), 2):
        dept_title = dept_splits[i].strip()
        dept_body = dept_splits[i + 1].strip()

        department_name = re.sub(r"^\d+\.\s+", "", dept_title)

        # Match section headers inside the department
        section_pattern = re.compile(
            r"(\d+\.\d+\s+(Introduction|Offered Programs|Eligibility Criteria|Faculty Members))",
            re.IGNORECASE,
        )

        section_splits = section_pattern.split(dept_body)

        for j in range(1, len(section_splits), 3):
            section_name = section_splits[j + 1].strip()
            section_content = section_splits[j + 2].strip()

            if len(section_content) < 50:
                continue

            # Only the final chunk text
            chunk_text = f"{department_name} - {section_name}: {section_content}"
            chunks.append(chunk_text)

    return chunks
