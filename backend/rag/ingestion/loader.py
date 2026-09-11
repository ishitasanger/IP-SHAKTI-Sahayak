from pathlib import Path
from urllib.parse import urljoin, urlparse

import fitz
import requests
from bs4 import BeautifulSoup


USER_AGENT = "IP-SHAKTI-Sahayak-RAG/1.0"


def load_pdf(pdf_path: str):
    """
    Extract text from a PDF page-by-page.
    """

    pdf_path = Path(pdf_path).resolve()

    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    pages = []

    with fitz.open(pdf_path) as document:
        for page_number, page in enumerate(document, start=1):
            pages.append({
                "text": page.get_text("text"),
                "page": page_number,
                "source": pdf_path.name,
                "source_url": None
            })

    return pages


def _extract_html_text(html: str):
    """
    Extract meaningful text from an HTML document.
    """

    soup = BeautifulSoup(html, "html.parser")

    # Remove non-content elements.
    for element in soup([
        "script",
        "style",
        "noscript",
        "nav",
        "footer",
        "header"
    ]):
        element.decompose()

    # Prefer the main content when available.
    main = soup.find("main")

    if main:
        text = main.get_text(" ", strip=True)
    else:
        text = soup.get_text(" ", strip=True)

    return text


def _extract_links(html: str, base_url: str):
    """
    Extract relevant same-domain links from an HTML page.
    """

    soup = BeautifulSoup(html, "html.parser")

    base_domain = urlparse(base_url).netloc

    links = []

    for anchor in soup.find_all("a", href=True):
        href = anchor["href"].strip()

        if not href:
            continue

        # Ignore non-web links.
        if href.startswith(("#", "javascript:", "mailto:", "tel:")):
            continue

        full_url = urljoin(base_url, href)
        parsed = urlparse(full_url)

        # Only stay on the same official domain.
        if parsed.netloc != base_domain:
            continue

        # Only HTTP(S).
        if parsed.scheme not in ("http", "https"):
            continue

        links.append({
            "url": full_url,
            "anchor": anchor.get_text(" ", strip=True)
        })

    # Remove duplicates while preserving order.
    seen = set()
    unique_links = []

    for link in links:
        if link["url"] not in seen:
            seen.add(link["url"])
            unique_links.append(link)

    return unique_links


def load_html(
    html_path: str,
    source_url: str | None = None,
    follow_links: bool = True
):
    """
    Load a local HTML source.

    If source_url is supplied, relevant same-domain links
    can be followed and their actual content can also be
    incorporated into the corpus.
    """

    html_path = Path(html_path).resolve()

    if not html_path.exists():
        raise FileNotFoundError(f"HTML not found: {html_path}")

    html = html_path.read_text(
        encoding="utf-8",
        errors="ignore"
    )

    pages = []

    # Main local HTML page.
    pages.append({
        "text": _extract_html_text(html),
        "page": None,
        "source": html_path.name,
        "source_url": source_url
    })

    if not follow_links or not source_url:
        return pages

    links = _extract_links(html, source_url)

    for link in links:

        try:
            response = requests.get(
                link["url"],
                headers={"User-Agent": USER_AGENT},
                timeout=20
            )

            response.raise_for_status()

            content_type = response.headers.get(
                "Content-Type",
                ""
            ).lower()

            # We only want HTML pages here.
            if "text/html" not in content_type:
                continue

            linked_text = _extract_html_text(
                response.text
            )

            if not linked_text:
                continue

            parsed = urlparse(link["url"])

            linked_name = (
                Path(parsed.path).name
                or "linked_page"
            )

            pages.append({
                "text": linked_text,
                "page": None,
                "source": linked_name,
                "source_url": link["url"],
                "parent_source": html_path.name
            })

            print(
                f"    Linked page: {link['url']}"
            )

        except requests.RequestException as error:
            print(
                f"    Could not fetch {link['url']}: {error}"
            )

    return pages


def load_file(
    file_path: str,
    source_url: str | None = None,
    follow_links: bool = True
):
    """
    Automatically choose the appropriate loader.
    """

    suffix = Path(file_path).suffix.lower()

    if suffix == ".pdf":
        return load_pdf(file_path)

    if suffix in (".html", ".htm"):
        return load_html(
            file_path,
            source_url=source_url,
            follow_links=follow_links
        )

    raise ValueError(
        f"Unsupported file type: {suffix}"
    )