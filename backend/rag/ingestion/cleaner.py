import re


def clean_text(text: str):
    text = text.replace("\x00", " ")

    # Remove excessive whitespace
    text = re.sub(r"\s+", " ", text)

    # Remove repeated page-number patterns
    text = re.sub(
        r"\bPage\s+\d+\b",
        "",
        text,
        flags=re.IGNORECASE
    )

    return text.strip()


def clean_documents(documents):
    for document in documents:
        document["text"] = clean_text(document["text"])

    return documents