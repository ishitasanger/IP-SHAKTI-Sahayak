import re


LEGAL_REFERENCE_PATTERN = re.compile(
    r"\b(section|rule)\s+(\d+[A-Za-z]?)"
    r"(?:\s*\(\s*([A-Za-z0-9]+)\s*\))?",
    re.IGNORECASE
)


def process_query(query: str):

    query = query.strip()

    query = re.sub(
        r"\s+",
        " ",
        query
    )

    return query


def expand_legal_query(query: str):

    query = process_query(query)

    expansions = [query]

    for match in LEGAL_REFERENCE_PATTERN.finditer(query):

        kind = match.group(1).lower()
        number = match.group(2)
        clause = match.group(3)

        expansions.append(f"{kind} {number}")
        expansions.append(number)

        if clause:
            expansions.append(clause)
            expansions.append(f"{number} {clause}")
            expansions.append(f"{number}({clause})")

    # Remove duplicates while preserving order
    return " ".join(
        dict.fromkeys(expansions)
    )