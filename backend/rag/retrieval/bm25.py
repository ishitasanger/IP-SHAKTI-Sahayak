import pickle
import re
from rank_bm25 import BM25Okapi

from rag.query.query_processor import expand_legal_query


class BM25Index:

    def __init__(self, index_path):

        self.index_path = index_path
        self.documents = []
        self.bm25 = None

    def build(self, chunks):

        self.documents = chunks

        tokenized_documents = [
            self._tokenize(chunk["text"])
            for chunk in chunks
        ]

        self.bm25 = BM25Okapi(tokenized_documents)

    def search(
        self,
        query,
        top_k=10,
        filters=None
    ):

        if self.bm25 is None:
            return []

        # Expand legal references such as Section 3(a)
        lexical_query = expand_legal_query(query)

        tokens = self._tokenize(
            lexical_query
        )

        scores = self.bm25.get_scores(tokens)

        ranked_indices = sorted(
            range(len(scores)),
            key=lambda i: scores[i],
            reverse=True
        )

        results = []

        for index in ranked_indices:

            document = self.documents[index]

            # Apply metadata filters if provided
            if filters:

                metadata = document.get(
                    "metadata",
                    {}
                )

                matches = all(
                    metadata.get(key) == value
                    for key, value in filters.items()
                )

                if not matches:
                    continue

            results.append({
                **document,
                "bm25_score": float(
                    scores[index]
                )
            })

            if len(results) >= top_k:
                break

        return results

    def save(self):

        with open(self.index_path, "wb") as file:
            pickle.dump(
                self.documents,
                file
            )

    def load(self):

        with open(self.index_path, "rb") as file:
            self.documents = pickle.load(file)

        tokenized_documents = [
            self._tokenize(chunk["text"])
            for chunk in self.documents
        ]

        self.bm25 = BM25Okapi(
            tokenized_documents
        )

    @staticmethod
    def _tokenize(text):

        text = text.lower()

        # Keep normal words/numbers and legal references
        tokens = re.findall(
            r"\d+\([a-z0-9]+\)|[a-z0-9]+",
            text
        )

        # Also add components of references such as 3(a)
        expanded_tokens = []

        for token in tokens:

            expanded_tokens.append(token)

            match = re.fullmatch(
                r"(\d+)\(([a-z0-9]+)\)",
                token
            )

            if match:

                expanded_tokens.append(
                    match.group(1)
                )

                expanded_tokens.append(
                    match.group(2)
                )

        return expanded_tokens