def map_citation(result):
    metadata = result["metadata"]

    return {
        "document": metadata.get(
            "document",
            "Unknown document"
        ),
        "section": metadata.get(
            "section",
            "Not specified"
        ),
        "page": metadata.get(
            "page"
        ),
        "source_file": metadata.get(
            "source_file"
        ),
        "source_url": metadata.get(
            "source_url"
        )
    }