from ..rag.rag_engine import RAGEngine
from ..LLM.answer_generator import AnswerGenerator


class ABSCheck:

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
                "domain": "abs"
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

        # General ABS evidence
        general_results = self.retrieve_evidence(
            product_context=product_context,
            top_k=5
        )

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

        # Prepare ABS result
        result = {

            "product_context": product_context,

            "overall_status": (
                "ABS review required"
                if general_results
                else "Insufficient ABS evidence"
            ),

            "checks": checks,

            "general_evidence": [
                self.map_citation(result)
                for result in general_results
            ],

            "disclaimer": (
                "This ABS Check provides information based on "
                "retrieved biodiversity and access-and-benefit-sharing "
                "sources. It is not legal advice and does not determine "
                "whether a specific approval or benefit-sharing "
                "obligation legally applies."
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


def abs_check(product_context):

    checker = ABSCheck()

    return checker.assess(product_context)