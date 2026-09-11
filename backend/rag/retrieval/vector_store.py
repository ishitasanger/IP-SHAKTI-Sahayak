import chromadb


class VectorStore:

    def __init__(self, persist_directory):

        self.client = chromadb.PersistentClient(
            path=str(persist_directory)
        )

        self.collection = (
            self.client.get_or_create_collection(
                name="ip_shakti",
                metadata={
                    "hnsw:space": "cosine"
                }
            )
        )

    def add_chunks(self, chunks, embeddings):

        self.collection.upsert(
            ids=[
                chunk["id"]
                for chunk in chunks
            ],

            documents=[
                chunk["text"]
                for chunk in chunks
            ],

            embeddings=embeddings.tolist(),

            metadatas=[
                chunk["metadata"]
                for chunk in chunks
            ]
        )

    def search(
        self,
        query_embedding,
        n_results=10,
        where=None
    ):

        return self.collection.query(
            query_embeddings=[
                query_embedding.tolist()
            ],
            n_results=n_results,
            where=where
        )