from sentence_transformers import CrossEncoder
import re


MODEL_NAME = "BAAI/bge-reranker-base"


class Reranker:

    def __init__(self):
        self.model = CrossEncoder(MODEL_NAME)

    def rerank(self, query, results, top_k=5):

        if not results:
            return []

        pairs = [
            [query, result["text"]]
            for result in results
        ]

        scores = self.model.predict(pairs)

        legal_references = self._extract_legal_references(query)

        for result, score in zip(results, scores):

            final_score = float(score)

            # Give priority to results containing
            # the exact legal reference requested.
            if legal_references:

                text = result["text"].lower()

                for reference in legal_references:

                    if self._reference_present(
                        reference,
                        text
                    ):
                        final_score += 0.50
                        break

            result["reranker_score"] = final_score

        results.sort(
            key=lambda x: x["reranker_score"],
            reverse=True
        )

        return results[:top_k]

    @staticmethod
    def _extract_legal_references(query):

        pattern = re.compile(
            r"\b(section|rule)\s+"
            r"(\d+[a-z]?)"
            r"(?:\s*\(\s*([a-z0-9]+)\s*\))?",
            re.IGNORECASE
        )

        references = []

        for match in pattern.finditer(query):

            kind = match.group(1).lower()
            number = match.group(2)
            clause = match.group(3)

            if clause:
                references.append(
                    f"{kind} {number}({clause})"
                )
            else:
                references.append(
                    f"{kind} {number}"
                )

        return references

    @staticmethod
    def _reference_present(reference, text):

        # Section 3(a), Rule 14(2), etc.
        match = re.match(
            r"(section|rule)\s+"
            r"(\d+[a-z]?)"
            r"(?:\(([^)]+)\))?",
            reference,
            re.IGNORECASE
        )

        if not match:
            return False

        kind = match.group(1)
        number = match.group(2)
        clause = match.group(3)

        # Exact form:
        # Section 3(a)
        if clause:

            exact_pattern = (
                rf"\b{kind}\s+"
                rf"{re.escape(number)}"
                rf"\s*\(\s*"
                rf"{re.escape(clause)}"
                rf"\s*\)"
            )

            if re.search(
                exact_pattern,
                text,
                re.IGNORECASE
            ):
                return True

            # PDF may contain:
            # 3. Section 3 ... (a)
            # rather than "Section 3(a)"
            number_pattern = (
                rf"\b{re.escape(number)}\s*\."
            )

            clause_pattern = (
                rf"\(\s*"
                rf"{re.escape(clause)}"
                rf"\s*\)"
            )

            return bool(
                re.search(number_pattern, text)
                and re.search(clause_pattern, text)
            )

        # Section 3 / Rule 14
        pattern = (
            rf"\b{kind}\s+"
            rf"{re.escape(number)}\b"
        )

        return bool(
            re.search(
                pattern,
                text,
                re.IGNORECASE
            )
        )