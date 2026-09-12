from ..rag.rag_engine import RAGEngine
from ..LLM.answer_generator import AnswerGenerator


class RegulatoryFitCheck:

    def __init__(self):
        """
        Initialize the existing RAG engine.

        Regulatory FitCheck does NOT modify the RAG pipeline.
        It only uses RAGEngine.search().
        """

        self.rag = RAGEngine()
        self.answer_generator = AnswerGenerator()

    # --------------------------------------------------
    # Citation mapping
    # --------------------------------------------------

    @staticmethod
    def map_citation(result):
        """
        Convert a RAGResult into a frontend-friendly citation.
        """

        return {
            "document": result.document,
            "section": result.section,
            "page": result.page,
            "source_file": result.source_file,
            "source_url": result.metadata.get("source_url"),
            "text": result.text
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
        """
        Retrieve regulatory evidence from the existing RAG.

        IMPORTANT:
        This module explicitly chooses:

            domain = regulatory

        RAG does not decide the domain.
        """

        results = self.rag.search(
            query=query,
            context=product_context,
            filters={
                "domain": "regulatory"
            },
            top_k=top_k
        )

        return results

    # --------------------------------------------------
    # Basic status determination
    # --------------------------------------------------

    @staticmethod
    def determine_status(evidence):
        """
        Basic evidence-based status.

        This is intentionally simple for the prototype.

        The status does NOT claim that the product is legally
        compliant. It only indicates whether regulatory
        evidence was found for the check.
        """

        if not evidence:
            return "Attention"

        return "Review"

    # --------------------------------------------------
    # Main Regulatory FitCheck
    # --------------------------------------------------

    def assess(self, product_context):
        """
        Perform the Regulatory FitCheck.

        product_context can come directly from the frontend
        today.

        Later, the Classification Wizard can provide the same
        structure automatically.
        """

        # ----------------------------------------------
        # 1. Retrieve general regulatory evidence
        # ----------------------------------------------

        general_results = self.retrieve_evidence(
            product_context=product_context,
            top_k=5
        )

        # ----------------------------------------------
        # 2. Regulatory categories
        # ----------------------------------------------

        categories = {
            "licensing": "licensing and registration requirements",

            "labelling": "labelling and packaging requirements",

            "safety": "safety, quality and testing requirements",

            "gmp": "Good Manufacturing Practices GMP requirements",

            "claims": "claims, advertising and disease treatment claims",

            "applicable_regulations": (
                "applicable regulations, rules, standards "
                "and regulatory framework"
            )
        }

        checks = {}

        # ----------------------------------------------
        # 3. Retrieve evidence for each category
        # ----------------------------------------------

        for category, category_query in categories.items():

            results = self.retrieve_evidence(
                product_context=product_context,
                query=category_query,
                top_k=3
            )

            checks[category] = {
                "status": self.determine_status(results),

                "evidence": [
                    self.map_citation(result)
                    for result in results
                ]
            }

        # ----------------------------------------------
        # 4. Overall result
        # ----------------------------------------------

        result = {
            "product_context": product_context,

            "overall_status": (
                "Review required"
                if general_results
                else "Insufficient evidence"
            ),

            "checks": checks,

            "general_evidence": [
                self.map_citation(result)
                for result in general_results
            ],

            "disclaimer": (
                "This Regulatory FitCheck provides "
                "information based on retrieved regulatory "
                "sources and is not legal advice."
            )
        }

        # ----------------------------------------------
        # 5. Generate final explanation using Groq LLM
        # ----------------------------------------------

        result["llm_answer"] = (
            self.answer_generator.generate_regulatory_answer(
                product_context,
                result
            )
        )

        return result


# ------------------------------------------------------
# Convenience function
# ------------------------------------------------------

def regulatory_fitcheck(product_context):
    """
    Simple function that teammates can call.

    Example:

        result = regulatory_fitcheck(product_context)
    """

    fitcheck = RegulatoryFitCheck()

    return fitcheck.assess(
        product_context
    )