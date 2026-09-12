from pathlib import Path

from rag.crawler.sources import SOURCES
from rag.crawler.web_loader import load_webpage



BASE_DIR = Path(__file__).resolve().parent / "rag"

OUTPUT_DIR = (
    BASE_DIR
    / "data"
    / "raw"
    / "next_actions"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


def crawl_sources():

    for source in SOURCES:

        print(
            f"\nCrawling: {source['document']}"
        )

        try:

            result = load_webpage(
                source["url"]
            )

            filename = (
                source["document"]
                .replace(" ", "_")
                + ".txt"
            )

            output_path = (
                OUTPUT_DIR / filename
            )

            output_path.write_text(
                result["text"],
                encoding="utf-8"
            )

            print(
                f"Saved: {output_path}"
            )

        except Exception as e:

            print(
                f"ERROR: {source['url']}"
            )

            print(e)


if __name__ == "__main__":
    crawl_sources()