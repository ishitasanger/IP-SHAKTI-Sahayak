from ..rag.rag_engine import RAGEngine
from ..LLM.answer_generator import AnswerGenerator


class TKDLCheck:

    def __init__(self):
        self.rag = RAGEngine()
        self.answer_generator = AnswerGenerator()

    @staticmethod
    def map_citation(result):
        return {
            "document": result.document,
            "section": result.section,
            "page": result.page,
            "source_file": result.source_file,
            "source_url": result.metadata.get("source_url"),
            "text": result.text
        }

    def retrieve_evidence(self, product_context, query=None, top_k=5):

        results = self.rag.search(
            query=query,
            context=product_context,
            filters={
                "domain": "tkdl"
            },
            top_k=top_k
        )

        return results

    @staticmethod
    def determine_status(evidence):

        if not evidence:
            return "Attention"

        return "Review"

    def assess(self, product_context):

        # General TKDL evidence
        general_results = self.retrieve_evidence(
            product_context=product_context,
            top_k=5
        )

        categories = {

            "traditional_knowledge":
                "traditional knowledge associated with the Ayurvedic formulation",

            "prior_art":
                "traditional knowledge as prior art and existing knowledge in Indian systems of medicine",

            "ayurveda_sources":
                "Ayurveda classical texts and published literature used as sources of traditional knowledge",

            "formulation_evidence":
                "formulation ingredients method of preparation usage and bibliographic evidence",

            "tkrc":
                "Traditional Knowledge Resource Classification TKRC and classification of traditional knowledge",

            "patent_relevance":
                "relevance of traditional knowledge to patent novelty inventive step and patent examination",

            "source_information":
                "source books bibliographic information and origin of traditional knowledge",

            "tkdl_database":
                "TKDL database representative formulations searchable traditional knowledge evidence"
        }

        checks = {}

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

        # Prepare final result
        result = {
            "product_context": product_context,

            "overall_status": (
                "TKDL review required"
                if general_results
                else "Insufficient TKDL evidence"
            ),

            "checks": checks,

            "general_evidence": [
                self.map_citation(result)
                for result in general_results
            ],

            "disclaimer": (
                "This TKDL Check provides information based on "
                "retrieved TKDL and traditional knowledge sources. "
                "It does not determine patentability or establish "
                "legal prior art. The underlying published sources "
                "should be independently verified."
            )
        }

        # Generate final explanation using Groq LLM
        result["llm_answer"] = (
            self.answer_generator.generate_regulatory_answer(
                product_context,
                result
            )
        )

        return result


def tkdl_check(product_context):

    checker = TKDLCheck()

    return checker.assess(product_context)