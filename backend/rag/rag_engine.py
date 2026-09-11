from pathlib import Path

from .retrieval.embeddings import embed_query
from .retrieval.vector_store import VectorStore
from .retrieval.bm25 import BM25Index
from .retrieval.hybrid_search import HybridSearch
from .retrieval.reranker import Reranker
from .query.query_processor import process_query
from .models import RAGResult


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"


class RAGEngine:

    def __init__(self):

        self.vector_store = VectorStore(
            DATA_DIR / "chroma_db"
        )

        self.bm25_index = BM25Index(
            DATA_DIR / "bm25.pkl"
        )

        if (DATA_DIR / "bm25.pkl").exists():
            self.bm25_index.load()

        self.hybrid_search = HybridSearch(
            self.vector_store,
            self.bm25_index
        )

        self.reranker = Reranker()

    @staticmethod
    def _context_to_text(context):
        """
        Convert structured context into text suitable
        for retrieval.

        This method is intentionally generic and does not
        assume any feature-specific fields.
        """

        if context is None:
            return ""

        if isinstance(context, str):
            return context

        if isinstance(context, dict):

            parts = []

            for key, value in context.items():

                if value is None:
                    continue

                if isinstance(value, (list, tuple, set)):
                    value = " ".join(
                        str(item)
                        for item in value
                    )

                elif isinstance(value, dict):
                    value = RAGEngine._context_to_text(
                        value
                    )

                parts.append(
                    f"{key}: {value}"
                )

            return " ".join(parts)

        if isinstance(context, (list, tuple, set)):
            return " ".join(
                str(item)
                for item in context
            )

        return str(context)

    def search(
        self,
        query=None,
        context=None,
        filters=None,
        top_k=5
    ):
        """
        Retrieve relevant evidence.

        The calling module can provide:

        - query
        - structured context
        - both query and context
        - optional metadata filters

        The RAG engine performs:

        query/context processing
        -> embeddings
        -> hybrid retrieval
        -> reranking
        -> structured evidence
        """

        # --------------------------------------------------
        # 1. Convert context to retrieval text
        # --------------------------------------------------

        context_text = self._context_to_text(context)

        if query and context_text:

            retrieval_text = (
                f"{query} {context_text}"
            )

        elif query:

            retrieval_text = query

        elif context_text:

            retrieval_text = context_text

        else:

            raise ValueError(
                "Either query or context must be provided."
            )

        # --------------------------------------------------
        # 2. Process query
        # --------------------------------------------------

        retrieval_text = process_query(
            retrieval_text
        )

        # --------------------------------------------------
        # 3. Create query embedding
        # --------------------------------------------------

        query_embedding = embed_query(
            retrieval_text
        )

        # --------------------------------------------------
        # 4. Hybrid retrieval
        # --------------------------------------------------

        # Retrieve more candidates before reranking.
        candidate_k = max(top_k * 2, 10)

        results = self.hybrid_search.search(
            query=retrieval_text,
            query_embedding=query_embedding,
            top_k=candidate_k,
            filters=filters
        )

        # --------------------------------------------------
        # 5. Reranking
        # --------------------------------------------------

        results = self.reranker.rerank(
            query=retrieval_text,
            results=results,
            top_k=top_k
        )

        # --------------------------------------------------
        # 6. Convert to standard RAGResult objects
        # --------------------------------------------------

        final_results = []

        for result in results:

            metadata = result.get(
                "metadata",
                {}
            )

            final_results.append(
                RAGResult(
                    text=result["text"],

                    document=metadata.get(
                        "document",
                        "Unknown"
                    ),

                    section=metadata.get(
                        "section"
                    ),

                    page=metadata.get(
                        "page"
                    ),

                    source_file=metadata.get(
                        "source_file"
                    ),

                    score=result.get(
                        "reranker_score",
                        result.get(
                            "hybrid_score",
                            0
                        )
                    ),

                    metadata=metadata
                )
            )

        return final_results