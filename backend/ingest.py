from pathlib import Path
import hashlib
import json


from rag.ingestion.loader import load_file
from rag.ingestion.cleaner import clean_documents
from rag.ingestion.chunker import create_chunks


from rag.retrieval.metadata import (
    infer_domain,
    infer_source_type,
    infer_action_type
)


from rag.retrieval.embeddings import create_embeddings
from rag.retrieval.vector_store import VectorStore
from rag.retrieval.bm25 import BM25Index


BASE_DIR = Path(__file__).resolve().parent

RAW_DIR = BASE_DIR / "rag" / "data" / "raw"
DATA_DIR = BASE_DIR / "rag" / "data"

CHROMA_DIR = DATA_DIR / "chroma_db"
BM25_PATH = DATA_DIR / "bm25.pkl"
DOCUMENTS_PATH = DATA_DIR / "documents.json"


SUPPORTED_EXTENSIONS = {
    ".pdf",
    ".html",
    ".htm",
    ".txt"
}


# --------------------------------------------------
# OFFICIAL SOURCE URLS
# --------------------------------------------------
SOURCE_URLS = {
    "ip/next_actions/Patent_Filing_Process.txt":
        "https://ipindia.gov.in/filing-process",

    "ip/next_actions/Trademark_Filing_Process.txt":
        "https://ipindia.gov.in/application-workflow/trademark-filing-process",

    "ip/next_actions/Design_Filing_Process.txt":
        "https://ipindia.gov.in/pages/designs/learn/filing-process-step-by-step",
}

def calculate_file_hash(file_path):

    """
    Calculate SHA-256 hash of a local source file.
    """

    sha256 = hashlib.sha256()

    with open(
        file_path,
        "rb"
    ) as file:

        for block in iter(
            lambda: file.read(
                1024 * 1024
            ),
            b""
        ):

            sha256.update(
                block
            )

    return sha256.hexdigest()


def load_registry():

    if not DOCUMENTS_PATH.exists():
        return {}

    if DOCUMENTS_PATH.stat().st_size == 0:
        return {}

    with open(
        DOCUMENTS_PATH,
        "r",
        encoding="utf-8"
    ) as file:

        data = json.load(
            file
        )

    # Support the old {"documents": {...}} format
    if (
        isinstance(data, dict)
        and "documents" in data
    ):

        return data["documents"]

    # Current format
    if isinstance(data, dict):
        return data

    raise ValueError(
        "Invalid documents.json format. "
        "Expected a JSON object."
    )


def save_registry(registry):

    """
    Save documents.json.
    """

    with open(
        DOCUMENTS_PATH,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            registry,
            file,
            indent=4,
            ensure_ascii=False
        )


def get_source_key(file_path):

    """
    Stable path relative to raw/.
    """

    return file_path.relative_to(
        RAW_DIR
    ).as_posix()


def get_source_url(file_path):

    """
    Return official source URL if configured.
    """

    key = get_source_key(
        file_path
    )

    return SOURCE_URLS.get(
        key
    )


def remove_existing_source(
    vector_store,
    source_key
):

    """
    Remove all Chroma chunks belonging to
    an old version of this source.
    """

    try:

        vector_store.collection.delete(
            where={
                "source_key": source_key
            }
        )

    except Exception as error:

        print(
            f"Warning while removing old source: "
            f"{error}"
        )


def main():

    RAW_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    registry = load_registry()

    vector_store = VectorStore(
        CHROMA_DIR
    )

    all_files = [
        path
        for path in RAW_DIR.rglob("*")
        if (
            path.is_file()
            and path.suffix.lower()
            in SUPPORTED_EXTENSIONS
        )
    ]

    if not all_files:

        print(
            "No supported source files found."
        )

        print(
            f"Put sources inside: {RAW_DIR}"
        )

        return

    print(
        f"Found {len(all_files)} source files."
    )

    changed_chunks = []

    # --------------------------------------------------
    # PROCESS ONLY NEW / CHANGED FILES
    # --------------------------------------------------

    for file_path in all_files:

        source_key = get_source_key(
            file_path
        )

        current_hash = calculate_file_hash(
            file_path
        )

        previous = registry.get(
            source_key
        )

        # ----------------------------------------------
        # UNCHANGED
        # ----------------------------------------------

        if (
            previous
            and previous.get("file_hash")
            == current_hash
        ):

            print(
                f"\nSKIP: {source_key}"
            )

            continue

        # ----------------------------------------------
        # NEW / CHANGED
        # ----------------------------------------------

        if previous:

            print(
                f"\nCHANGED: {source_key}"
            )

            remove_existing_source(
                vector_store,
                source_key
            )

        else:

            print(
                f"\nNEW: {source_key}"
            )

        print(
            f"  Processing: {file_path.name}"
        )

        source_url = get_source_url(
            file_path
        )

        # Load PDF / HTML / TXT
        documents = load_file(
            str(file_path),
            source_url=source_url,
            follow_links=True
        )

        documents = clean_documents(
            documents
        )

        chunks = create_chunks(
            documents
        )

        # ----------------------------------------------
        # METADATA
        # ----------------------------------------------

        domain = infer_domain(
            file_path
        )

        source_type = infer_source_type(
            file_path
        )

        action_type = infer_action_type(
            file_path
        )

        # Attach metadata to every chunk
        for chunk in chunks:

            metadata = {
                "document": Path(
                    chunk["source"]
                ).stem,

                "domain": domain,

                "jurisdiction": "India",

                "source_type": source_type,

                "action_type": action_type,

                "source_file": source_key,

                "source_key": source_key,

                "page": (
                    chunk.get("page")
                    if chunk.get("page")
                    else 0
                ),

                "section": (
                    chunk.get("section")
                    or "Not specified"
                )
            }

            if chunk.get("source_url"):

                metadata[
                    "source_url"
                ] = chunk["source_url"]

            if chunk.get("parent_source"):

                metadata[
                    "parent_source"
                ] = chunk["parent_source"]

            chunk["metadata"] = metadata

        changed_chunks.extend(
            chunks
        )

        # ----------------------------------------------
        # REGISTRY
        # ----------------------------------------------

        registry[source_key] = {

            "source_key": source_key,

            "source_file": source_key,

            "file_hash": current_hash,

            "domain": domain,

            "source_type": source_type,

            "action_type": action_type,

            "source_url": source_url,

            "chunks": len(chunks)
        }

        print(
            f"  Chunks created: "
            f"{len(chunks)}"
        )

        print(
            f"  Action type: "
            f"{action_type}"
        )

    # --------------------------------------------------
    # NOTHING NEW
    # --------------------------------------------------

    if not changed_chunks:

        print(
            "\nNo new or changed sources."
        )

        print(
            "Existing indexes are already up to date."
        )

        return

    # --------------------------------------------------
    # EMBEDDINGS
    # --------------------------------------------------

    print(
        f"\nCreating embeddings for "
        f"{len(changed_chunks)} new chunks..."
    )

    texts = [
        chunk["text"]
        for chunk in changed_chunks
    ]

    embeddings = create_embeddings(
        texts
    )

    # --------------------------------------------------
    # CHROMA
    # --------------------------------------------------

    print(
        "\nAdding chunks to ChromaDB..."
    )

    vector_store.add_chunks(
        changed_chunks,
        embeddings
    )

    # --------------------------------------------------
    # BM25
    # --------------------------------------------------

    print(
        "\nRebuilding BM25 index..."
    )

    # BM25 needs the complete corpus.
    all_chunks = []

    for source in registry.values():

        # Chroma is the authoritative storage
        # for already-indexed chunks.
        results = vector_store.collection.get(
            where={
                "source_key": source["source_key"]
            }
        )

        ids = results.get(
            "ids",
            []
        )

        texts = results.get(
            "documents"
        ) or []

        metadatas = results.get(
            "metadatas",
            []
        )

        for i in range(
            len(ids)
        ):

            metadata = (
                metadatas[i]
                if metadatas
                and i < len(metadatas)
                else {}
            ) or {}

            all_chunks.append({
                "id": ids[i],

                "text": (
                    texts[i]
                    if texts[i] is not None
                    else ""
                ),

                "metadata": metadata
            })

    bm25 = BM25Index(
        BM25_PATH
    )

    bm25.build(
        all_chunks
    )

    bm25.save()

    # --------------------------------------------------
    # REGISTRY
    # --------------------------------------------------

    save_registry(
        registry
    )

    print(
        "\nIngestion completed."
    )

    print(
        f"New/changed chunks: "
        f"{len(changed_chunks)}"
    )

    print(
        f"Tracked sources: "
        f"{len(registry)}"
    )


if __name__ == "__main__":
    main()