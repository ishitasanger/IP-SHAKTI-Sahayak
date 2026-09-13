from ..rag.rag_engine import RAGEngine
from ..LLM.answer_generator import AnswerGenerator


class RegulatoryFitCheck:

    def __init__(self):

        self.rag = RAGEngine()
        self.answer_generator = AnswerGenerator()

    # --------------------------------------------------
    # Citation mapping
    # --------------------------------------------------

    @staticmethod
    def map_citation(result):
        """
        Convert a RAGResult into frontend-friendly source metadata.

        Retrieved text is intentionally NOT returned.
        """

        return {
            "document": result.document,
            "section": result.section,
            "page": result.page,
            "source_file": result.source_file,
            "source_url": result.metadata.get("source_url"),
        }

    # --------------------------------------------------
    # Internal evidence mapping
    # --------------------------------------------------

    @staticmethod
    def map_evidence(result):
        """
        Internal representation used by the LLM.

        This is NOT intended for frontend output.
        """

        return {
            "document": result.document,
            "section": result.section,
            "page": result.page,
            "source_file": result.source_file,
            "source_url": result.metadata.get("source_url"),
            "text": result.text,
        }

    # --------------------------------------------------
    # Regulatory evidence retrieval
    # --------------------------------------------------

    def retrieve_evidence(
        self,
        product_context,
        query=None,
        top_k=5
    ):

        return self.rag.search(
            query=query,
            context=product_context,
            filters={
                "domain": "regulatory"
            },
            top_k=top_k
        )

    # --------------------------------------------------
    # Status
    # --------------------------------------------------

    @staticmethod
    def determine_status(evidence):

        if not evidence:
            return "Attention"

        return "Review"

    # --------------------------------------------------
    # Main assessment
    # --------------------------------------------------

    def assess(self, product_context):

        # --------------------------------------------------
        # 1. General regulatory evidence
        # --------------------------------------------------

        general_results = self.retrieve_evidence(
            product_context=product_context,
            top_k=5
        )

        # --------------------------------------------------
        # 2. Regulatory categories
        # --------------------------------------------------

        categories = {

            "licensing":
                "licensing and registration requirements",

            "labelling":
                "labelling and packaging requirements",

            "safety":
                "safety quality and testing requirements",

            "gmp":
                "Good Manufacturing Practices GMP requirements",

            "claims":
                "claims advertising and disease treatment claims",

            "applicable_regulations":
                "applicable regulations rules standards and regulatory framework"
        }

        checks = {}

        # --------------------------------------------------
        # 3. Category evidence
        # --------------------------------------------------

        for category, category_query in categories.items():

            results = self.retrieve_evidence(
                product_context=product_context,
                query=category_query,
                top_k=2
            )

            checks[category] = {

                "status":
                    self.determine_status(results),

                # INTERNAL evidence.
                # Used by AnswerGenerator.
                "evidence": [
                    self.map_evidence(result)
                    for result in results
                ],

                # USER-FACING sources.
                "sources": [
                    self.map_citation(result)
                    for result in results
                ]
            }

        # --------------------------------------------------
        # 4. Prepare internal result for LLM
        # --------------------------------------------------

        llm_result = {

            "checks": checks,

            "general_evidence": [
                self.map_evidence(result)
                for result in general_results[:2]
            ]
        }

        # --------------------------------------------------
        # 5. Generate LLM answer
        # --------------------------------------------------

        llm_answer = (
            self.answer_generator.generate_regulatory_answer(
                product_context,
                llm_result
            )
        )

        # --------------------------------------------------
        # 6. User-facing sources
        # --------------------------------------------------

        sources = []

        for check in checks.values():

            for source in check["sources"]:

                key = (
                    source.get("document"),
                    source.get("section"),
                    source.get("page")
                )

                if key not in [
                    (
                        s.get("document"),
                        s.get("section"),
                        s.get("page")
                    )
                    for s in sources
                ]:
                    sources.append(source)

        for result in general_results[:2]:

            source = self.map_citation(result)

            key = (
                source.get("document"),
                source.get("section"),
                source.get("page")
            )

            if key not in [
                (
                    s.get("document"),
                    s.get("section"),
                    s.get("page")
                )
                for s in sources
            ]:
                sources.append(source)

        # --------------------------------------------------
        # 7. Final USER-FACING result
        # --------------------------------------------------

        return {

            "product_context": product_context,

            "overall_status": (
                "Review required"
                if general_results
                else "Insufficient regulatory evidence"
            ),

            # Each category keeps status + clean sources.
            # Raw text is NOT returned.
            "checks": {
                category: {
                    "status": check["status"],
                    "sources": check["sources"]
                }
                for category, check in checks.items()
            },

            "llm_answer": llm_answer,

            "sources": sources,

            "disclaimer": (
                "This Regulatory FitCheck provides "
                "information based on retrieved regulatory "
                "sources and is not legal advice."
            )
        }


def regulatory_fitcheck(product_context):

    fitcheck = RegulatoryFitCheck()

    return fitcheck.assess(
        product_context
    )