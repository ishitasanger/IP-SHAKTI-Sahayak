from ..rag.rag_engine import RAGEngine
from ..LLM.answer_generator import AnswerGenerator


class ABSCheck:

    def __init__(self):

        self.rag = RAGEngine()
        self.answer_generator = AnswerGenerator()

    # --------------------------------------------------
    # USER-FACING CITATION
    # --------------------------------------------------

    @staticmethod
    def map_citation(result):
        """
        Frontend-facing source information.

        Retrieved text is NOT exposed.
        """

        return {
            "document": result.document,
            "section": result.section,
            "page": result.page,
            "source_file": result.source_file,
            "source_url": result.metadata.get("source_url"),
        }

    # --------------------------------------------------
    # INTERNAL EVIDENCE
    # --------------------------------------------------

    @staticmethod
    def map_evidence(result):
        """
        Internal evidence representation used by the LLM.
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
    # RAG RETRIEVAL
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
                "domain": "abs"
            },
            top_k=top_k
        )

    # --------------------------------------------------
    # STATUS
    # --------------------------------------------------

    @staticmethod
    def determine_status(evidence):

        if not evidence:
            return "Attention"

        return "Review"

    # --------------------------------------------------
    # MAIN ASSESSMENT
    # --------------------------------------------------

    def assess(self, product_context):

        # --------------------------------------------------
        # 1. General ABS evidence
        # --------------------------------------------------

        general_results = self.retrieve_evidence(
            product_context=product_context,
            top_k=5
        )

        # --------------------------------------------------
        # 2. ABS categories
        # --------------------------------------------------

        categories = {

            "biological_resource":
                "access to biological resources and use of biological resources",

            "traditional_knowledge":
                "associated traditional knowledge and traditional knowledge related to biological resources",

            "access_requirements":
                "requirements and procedures for access to biological resources",

            "benefit_sharing":
                "access and benefit sharing ABS benefit sharing obligations and mechanisms",

            "research_and_bio_utilization":
                "research bio-survey and bio-utilization of biological resources",

            "commercial_use":
                "commercial utilization of biological resources and associated knowledge",

            "intellectual_property":
                "patent intellectual property rights and biological resources associated traditional knowledge",

            "applicable_framework":
                "applicable Biological Diversity Act Rules ABS regulations and benefit sharing framework"
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

                # INTERNAL
                "evidence": [
                    self.map_evidence(result)
                    for result in results
                ],

                # FRONTEND
                "sources": [
                    self.map_citation(result)
                    for result in results
                ]
            }

        # --------------------------------------------------
        # 4. Prepare compact LLM input
        # --------------------------------------------------

        llm_result = {

            "checks": checks,

            "general_evidence": [
                self.map_evidence(result)
                for result in general_results[:2]
            ]
        }

        # --------------------------------------------------
        # 5. Generate ABS explanation
        # --------------------------------------------------

        llm_answer = (
            self.answer_generator.generate_abs_answer(
                product_context,
                llm_result
            )
        )

        # --------------------------------------------------
        # 6. Collect clean sources
        # --------------------------------------------------

        sources = []

        for check in checks.values():

            for source in check["sources"]:

                key = (
                    source.get("document"),
                    source.get("section"),
                    source.get("page")
                )

                existing_keys = [
                    (
                        s.get("document"),
                        s.get("section"),
                        s.get("page")
                    )
                    for s in sources
                ]

                if key not in existing_keys:
                    sources.append(source)

        for result in general_results[:2]:

            source = self.map_citation(result)

            key = (
                source.get("document"),
                source.get("section"),
                source.get("page")
            )

            existing_keys = [
                (
                    s.get("document"),
                    s.get("section"),
                    s.get("page")
                )
                for s in sources
            ]

            if key not in existing_keys:
                sources.append(source)

        # --------------------------------------------------
        # 7. Final USER-FACING result
        # --------------------------------------------------

        return {

            "product_context": product_context,

            "overall_status": (
                "ABS review required"
                if general_results
                else "Insufficient ABS evidence"
            ),

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
                "This ABS Check provides information based on "
                "retrieved biodiversity and access-and-benefit-sharing "
                "sources. It is not legal advice and does not determine "
                "whether a specific approval or benefit-sharing "
                "obligation legally applies."
            )
        }


def abs_check(product_context):

    checker = ABSCheck()

    return checker.assess(
        product_context
    )