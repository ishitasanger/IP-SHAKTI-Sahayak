from pydantic import BaseModel
from typing import Optional


class RAGResult(BaseModel):

    text: str

    document: str

    section: Optional[str] = None

    page: Optional[int] = None

    source_file: Optional[str] = None

    score: float

    metadata: dict