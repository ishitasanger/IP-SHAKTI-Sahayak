class HybridSearch:

    def __init__(self, vector_store, bm25_index):
        self.vector_store = vector_store
        self.bm25_index = bm25_index

    def search(
        self,
        query,
        query_embedding,
        top_k=10,
        filters=None
    ):
        """
        Perform hybrid retrieval using:
        - Dense vector search
        - BM25 keyword search
        - Reciprocal Rank Fusion (RRF)

        Metadata filters are applied to both
        retrieval methods.
        """

        # Retrieve more candidates than the final
        # number so that RRF has enough candidates
        candidate_k = max(top_k * 2, 20)

        # -------------------------
        # Dense retrieval
        # -------------------------

        dense_results = self.vector_store.search(
            query_embedding=query_embedding,
            n_results=candidate_k,
            where=filters
        )

        dense_items = []

        if dense_results.get("ids"):

            ids = dense_results["ids"][0]
            texts = dense_results["documents"][0]
            metadatas = dense_results["metadatas"][0]

            for i in range(len(ids)):

                dense_items.append({
                    "id": ids[i],
                    "text": texts[i],
                    "metadata": metadatas[i]
                })

        # -------------------------
        # BM25 retrieval
        # -------------------------

        bm25_results = self.bm25_index.search(
            query,
            top_k=candidate_k,
            filters=filters
        )

        # -------------------------
        # Reciprocal Rank Fusion
        # -------------------------

        rrf_k = 60

        combined = {}

        # Dense ranking
        for rank, item in enumerate(
            dense_items,
            start=1
        ):

            item_id = item["id"]

            if item_id not in combined:

                combined[item_id] = {
                    "id": item_id,
                    "text": item["text"],
                    "metadata": item["metadata"],
                    "hybrid_score": 0.0
                }

            combined[item_id]["hybrid_score"] += (
                1.0 / (rrf_k + rank)
            )

        # BM25 ranking
        for rank, item in enumerate(
            bm25_results,
            start=1
        ):

            item_id = item["id"]

            if item_id not in combined:

                combined[item_id] = {
                    "id": item_id,
                    "text": item["text"],
                    "metadata": item["metadata"],
                    "hybrid_score": 0.0
                }

            combined[item_id]["hybrid_score"] += (
                1.0 / (rrf_k + rank)
            )

        # -------------------------
        # Final ranking
        # -------------------------

        results = sorted(
            combined.values(),
            key=lambda x: x["hybrid_score"],
            reverse=True
        )

        return results[:top_k]