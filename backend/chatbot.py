from .rag.rag_engine import RAGEngine
from .LLM.chat_answer import ChatAnswerGenerator


class IPShaktiChatbot:

    def __init__(self):
        self.rag = RAGEngine()
        self.answer_generator = ChatAnswerGenerator()

    def answer(
        self,
        question,
        product_context=None,
        legal_report=None,
        roadmap=None,
        chat_history=None
    ):

        question_lower = question.lower()

        # --------------------------------------------------
        # Determine the most relevant legal domain
        # --------------------------------------------------

        filters = None

        if any(word in question_lower for word in [
            "abs",
            "benefit sharing",
            "biological resource",
            "biodiversity",
            "nba",
            "sbb"
        ]):
            filters = {"domain": "abs"}

        elif any(word in question_lower for word in [
            "tkdl",
            "traditional knowledge",
            "prior art"
        ]):
            filters = {"domain": "tkdl"}

        elif any(word in question_lower for word in [
            "patent",
            "trademark",
            "design",
            "copyright",
            "intellectual property",
            "ip"
        ]):
            filters = {"domain": "ip"}

        elif any(word in question_lower for word in [
            "licensing",
            "license",
            "labelling",
            "labeling",
            "gmp",
            "safety",
            "regulatory",
            "registration",
            "claims"
        ]):
            filters = {"domain": "regulatory"}

        # --------------------------------------------------
        # Retrieve relevant legal evidence
        # --------------------------------------------------

        results = self.rag.search(
            query=question,
            filters=filters,
            top_k=5
        )

        retrieved_evidence = []
        sources = []

        for result in results:

            # Full evidence for the LLM
            retrieved_evidence.append({
                "document": result.document,
                "section": result.section,
                "page": result.page,
                "source_url": result.metadata.get("source_url"),
                "text": result.text
            })

            # Clean source information for the frontend
            source = result.document

            if result.section and result.section != "Not specified":
                source += f" — {result.section}"

            if result.page:
                source += f", Page {result.page}"

            sources.append(source)

        # --------------------------------------------------
        # Generate grounded answer using LLM
        # --------------------------------------------------

        answer = self.answer_generator.generate_answer(
            question=question,
            product_context=product_context,
            legal_report=legal_report,
            roadmap=roadmap,
            chat_history=chat_history,
            retrieved_evidence=retrieved_evidence
        )

        return {
            "answer": answer,
            "sources": sources
        }