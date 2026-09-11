from sentence_transformers import SentenceTransformer


MODEL_NAME = "BAAI/bge-small-en-v1.5"

embedding_model = SentenceTransformer(MODEL_NAME)


def create_embeddings(texts):
    return embedding_model.encode(
        texts,
        normalize_embeddings=True
    )


def embed_query(query):
    return embedding_model.encode(
        query,
        normalize_embeddings=True
    )