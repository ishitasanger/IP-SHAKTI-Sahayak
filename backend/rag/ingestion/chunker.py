import re
import hashlib


# ---------------------------------------------------------
# Structure patterns
# ---------------------------------------------------------

# Examples:
# 3. What are not inventions.—
# 25. Opposition to the patent.—
# 14. Application for registration:
NUMBERED_HEADING_PATTERN = re.compile(
    r"(?m)^\s*(\d+[A-Za-z]?)\s*[.\-—:]\s+"
)

# Examples:
# Section 3. ...
# Section 25. ...
# Rule 14. ...
# Rule 24. ...
SECTION_RULE_PATTERN = re.compile(
    r"(?m)^\s*(Section|Rule)\s+(\d+[A-Za-z]?)"
    r"(?:\s*[.\-—:]\s+|\s*$)",
    flags=re.IGNORECASE
)

# Examples:
# CHAPTER I
# CHAPTER II
# CHAPTER III
CHAPTER_PATTERN = re.compile(
    r"(?m)^\s*CHAPTER\s+[IVXLCDM0-9]+(?:\s+.*)?$",
    flags=re.IGNORECASE
)


# ---------------------------------------------------------
# Heading detection
# ---------------------------------------------------------

def detect_heading(text):
    """
    Detect a structural heading at the beginning of a text block.

    Returns:
        A normalized heading string, or None.
    """

    # Section / Rule heading
    match = SECTION_RULE_PATTERN.match(text)

    if match:
        heading_type = match.group(1).title()
        number = match.group(2)

        return f"{heading_type} {number}"

    # Numbered legal heading
    match = NUMBERED_HEADING_PATTERN.match(text)

    if match:
        number = match.group(1)

        return f"Section {number}"

    return None


def split_into_sections(text):
    """
    Split text using actual structural headings.

    Important:
    We only recognize headings at the START of a line.

    Therefore text such as:

        "section 3 of the Trade Marks Act"

    will NOT be treated as a new section.
    """

    lines = text.splitlines()

    sections = []
    current_section = []

    for line in lines:

        stripped = line.strip()

        # Check whether this line starts a structural heading
        is_heading = False

        if SECTION_RULE_PATTERN.match(line):
            is_heading = True

        elif NUMBERED_HEADING_PATTERN.match(line):
            is_heading = True

        elif CHAPTER_PATTERN.match(line):
            is_heading = True

        if is_heading and current_section:

            section_text = "\n".join(
                current_section
            ).strip()

            if section_text:
                sections.append(section_text)

            current_section = []

        current_section.append(line)

    # Add final section
    if current_section:

        section_text = "\n".join(
            current_section
        ).strip()

        if section_text:
            sections.append(section_text)

    # If no structure was detected,
    # keep the entire document as one block.
    if not sections and text.strip():

        return [text.strip()]

    return sections


def extract_legal_heading(text):
    """
    Extract structural heading metadata.

    Examples:

        3. What are not inventions.—
        -> Section 3

        Section 3. ...
        -> Section 3

        Rule 14. ...
        -> Rule 14

        CHAPTER II ...
        -> Chapter II

    Returns None when no recognizable heading exists.
    """

    match = SECTION_RULE_PATTERN.match(text)

    if match:

        heading_type = match.group(1).title()
        number = match.group(2)

        return f"{heading_type} {number}"

    match = NUMBERED_HEADING_PATTERN.match(text)

    if match:

        number = match.group(1)

        return f"Section {number}"

    match = CHAPTER_PATTERN.match(text)

    if match:

        heading = match.group(0).strip()

        return heading.title()

    return None


# ---------------------------------------------------------
# Chunk creation
# ---------------------------------------------------------

def create_chunks(
    documents,
    chunk_size=1200,
    overlap=200
):
    """
    Create chunks from loaded documents.

    The chunker is domain-independent.

    It can handle:
        - Acts
        - Rules
        - Regulations
        - Guidelines
        - Manuals
        - TKDL material
        - ABS material
        - Other structured documents

    If structural headings exist, they are preserved.
    If they do not exist, normal size-based chunking is used.
    """

    chunks = []

    for document in documents:

        text = document["text"]

        sections = split_into_sections(text)

        for section_index, section in enumerate(
            sections
        ):

            section_heading = (
                extract_legal_heading(section)
            )

            start = 0
            chunk_index = 0

            while start < len(section):

                end = start + chunk_size

                chunk_text = (
                    section[start:end].strip()
                )

                if not chunk_text:
                    break

                raw_id = (
                    f"{document['source']}_"
                    f"{document.get('source_url')}_"
                    f"{document.get('page')}_"
                    f"{section_index}_"
                    f"{chunk_index}_"
                    f"{chunk_text}"
                )

                chunk_id = hashlib.sha256(
                    raw_id.encode("utf-8")
                ).hexdigest()

                chunks.append({
                    "id": chunk_id,
                    "text": chunk_text,
                    "page": document.get("page"),
                    "source": document["source"],
                    "source_url": document.get(
                        "source_url"
                    ),
                    "parent_source": document.get(
                        "parent_source"
                    ),
                    "section": section_heading
                })

                chunk_index += 1

                if end >= len(section):
                    break

                start += chunk_size - overlap

    return chunks