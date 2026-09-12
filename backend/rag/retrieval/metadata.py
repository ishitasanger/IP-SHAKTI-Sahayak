from pathlib import Path

import re


def infer_source_type(path: Path):
    """
    Infer legal source type from its folder.
    """

    parts = [
        part.lower()
        for part in path.parts
    ]

    if "acts" in parts:
        return "statute"

    if "rules" in parts:
        return "rules"

    if "guidelines" in parts:
        return "guideline"

    if "manuals" in parts:
        return "manual"

    if "regulations" in parts:
        return "regulation"

    if "next_actions" in parts:
        return "procedure"

    return "document"


def infer_domain(path: Path):
    """
    Domain comes from the top-level raw folder:
    ip / regulatory / tkdl / abs
    """

    parts = [
        part.lower()
        for part in path.parts
    ]

    for domain in (
        "ip",
        "regulatory",
        "tkdl",
        "abs"
    ):
        if domain in parts:
            return domain

    return "general"


def infer_action_type(path: Path):
    parts = [part.lower() for part in path.parts]

    # Action types should only be assigned to procedural
    # / next-action documents, not Acts, Rules, or Guidelines.
    if "next_actions" not in parts:
        return "general"

    path_text = " ".join(parts)

    if "patent" in path_text:
        return "patent_filing"

    if "trademark" in path_text:
        return "trademark_registration"

    if "design" in path_text:
        return "design_registration"

    if "licensing" in path_text:
        return "regulatory_licensing"

    if "abs" in path_text:
        return "abs_compliance"

    if "tkdl" in path_text or "prior_art" in path_text or "prior-art" in path_text:
        return "tk_prior_art"

    return "general"

def clean_document_name(filename: str):
    name = Path(filename).stem

    name = re.sub(
        r"[_\-]+",
        " ",
        name
    )

    name = re.sub(
        r"\s+",
        " ",
        name
    )

    return name.strip()


def attach_metadata(
    chunks,
    file_path,
    jurisdiction="India"
):
    """
    Attach consistent metadata to every chunk.
    """

    file_path = Path(file_path)

    domain = infer_domain(file_path)
    source_type = infer_source_type(file_path)
    action_type = infer_action_type(file_path)

    for chunk in chunks:

        metadata = {
            "document": clean_document_name(
                chunk["source"]
            ),

            "domain": domain,

            "jurisdiction": jurisdiction,

            "source_type": source_type,

            "action_type": action_type,

            "source_file": str(
                file_path.relative_to(
                    file_path.parents[4]
                )
            ),

            "page": chunk.get("page"),

            "section": (
                chunk.get("section")
                or "Not specified"
            )
        }

        if chunk.get("source_url"):
            metadata["source_url"] = (
                chunk["source_url"]
            )

        if chunk.get("parent_source"):
            metadata["parent_source"] = (
                chunk["parent_source"]
            )

        chunk["metadata"] = metadata

    return chunks