import requests
from bs4 import BeautifulSoup


def load_webpage(url: str):
    headers = {
        "User-Agent": (
            "Mozilla/5.0 "
            "(Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 "
            "(KHTML, like Gecko) "
            "Chrome/131.0 Safari/537.36"
        )
    }

    response = requests.get(
        url,
        headers=headers,
        timeout=30
    )

    response.raise_for_status()

    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )

    # Remove elements that are not useful for RAG.
    for element in soup(
        [
            "script",
            "style",
            "noscript",
            "nav",
            "footer",
            "header"
        ]
    ):
        element.decompose()

    # Prefer the main content area.
    main = (
        soup.find("main")
        or soup.find("article")
        or soup.find("div", class_="content")
        or soup.body
    )

    if main is None:
        raise ValueError(
            f"Could not find useful content in {url}"
        )

    # Extract all visible text while preserving element boundaries.
    text = main.get_text(
        separator="\n",
        strip=True
    )

    lines = []

    for line in text.splitlines():

        line = " ".join(line.split())

        if not line:
            continue

        # Preserve list structure.
        if line.startswith("•"):
            line = "- " + line.lstrip("•").strip()

        lines.append(line)

    cleaned_text = "\n".join(lines)

    return {
        "url": url,
        "text": cleaned_text
    }