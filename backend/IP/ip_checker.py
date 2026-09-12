from typing import Any, Dict, List, Optional

from Classification.classifier_wizard import ProductContext
from rag.rag_engine import RAGEngine


class IPScreeningResult:
    """
    Structured result returned by the IP and legal relevance checker.
    """

    def __init__(
        self,
        product_name: str,
        relevant_ip_domains: List[str],
        search_queries: List[Dict[str, str]],
        legal_evidence: List[Dict[str, Any]],
        legal_considerations: List[str],
        screening_status: str,
        summary: str,
        disclaimer: str,
    ):
        self.product_name = product_name
        self.relevant_ip_domains = relevant_ip_domains
        self.search_queries = search_queries
        self.legal_evidence = legal_evidence
        self.evidence_count = len(legal_evidence)
        self.legal_considerations = legal_considerations
        self.screening_status = screening_status
        self.summary = summary
        self.disclaimer = disclaimer

    def to_dict(self) -> Dict[str, Any]:

        return {
            "product_name": self.product_name,
            "relevant_ip_domains": self.relevant_ip_domains,
            "search_queries": self.search_queries,
            "legal_evidence": self.legal_evidence,
            "evidence_count": self.evidence_count,
            "legal_considerations": self.legal_considerations,
            "screening_status": self.screening_status,
            "summary": self.summary,
            "disclaimer": self.disclaimer,
        }


class IPChecker:
    """
    Preliminary IP and legal relevance screening.

    This module uses the existing project RAG pipeline.

    Current RAG knowledge base domains observed during testing:

        - regulatory
        - abs

    The system does NOT perform a patent registry search
    or trademark registry search.

    It identifies potentially relevant IP domains and retrieves
    supporting legal evidence from the existing knowledge base.
    """

    def __init__(self):

        self.rag = RAGEngine()

    # ============================================================
    # PUBLIC METHOD
    # ============================================================

    def check_ip(
        self,
        product: ProductContext,
        top_k: int = 3,
    ) -> IPScreeningResult:

        relevant_ip_domains = self._identify_ip_domains(product)

        search_plan = self._build_search_plan(product)

        legal_evidence = self._retrieve_legal_evidence(
            product=product,
            search_plan=search_plan,
            top_k=top_k,
        )

        legal_considerations = (
            self._generate_legal_considerations(product)
        )

        screening_status = (
            self._determine_screening_status(
                legal_evidence
            )
        )

        summary = self._generate_summary(
            product=product,
            relevant_ip_domains=relevant_ip_domains,
            legal_evidence=legal_evidence,
        )

        disclaimer = (
            "This is an automated preliminary IP and legal "
            "relevance screening result and not a legal opinion. "
            "The current system retrieves relevant legal and "
            "regulatory information from the project's RAG "
            "knowledge base. It does not perform a comprehensive "
            "search of patent, trademark, design or other official "
            "IP registries. Professional legal review and official "
            "database searches may be required."
        )

        return IPScreeningResult(

            product_name=product.product_name,

            relevant_ip_domains=relevant_ip_domains,

            search_queries=[
                {
                    "query_type": item["query_type"],
                    "query_text": item["query"],
                    "rag_domain": item["rag_domain"],
                }
                for item in search_plan
            ],

            legal_evidence=legal_evidence,

            legal_considerations=legal_considerations,

            screening_status=screening_status,

            summary=summary,

            disclaimer=disclaimer,
        )

    # ============================================================
    # IP DOMAIN IDENTIFICATION
    # ============================================================

    def _identify_ip_domains(
        self,
        product: ProductContext,
    ) -> List[str]:

        domains = []

        # --------------------------------------------------------
        # PATENT
        # --------------------------------------------------------

        if product.innovation_description:

            domains.append("patent")

        elif (
            product.classification
            in [
                "proprietary formulation",
                "multi-ingredient formulation",
            ]
        ):

            domains.append("patent")

        elif product.ingredient_count > 1:

            domains.append("patent")

        # --------------------------------------------------------
        # TRADEMARK
        # --------------------------------------------------------

        if product.commercial_use:

            domains.append("trademark")

        # --------------------------------------------------------
        # TRADITIONAL KNOWLEDGE
        # --------------------------------------------------------

        if (
            str(product.traditional_knowledge).lower()
            == "yes"
        ):

            domains.append(
                "traditional knowledge relevance"
            )

        # --------------------------------------------------------
        # BIOLOGICAL RESOURCES
        # --------------------------------------------------------

        if (
            str(product.uses_biological_resources).lower()
            == "yes"
        ):

            domains.append(
                "biological resource relevance"
            )

        # --------------------------------------------------------
        # REMOVE DUPLICATES
        # --------------------------------------------------------

        unique_domains = []

        for domain in domains:

            if domain not in unique_domains:

                unique_domains.append(domain)

        return unique_domains

    # ============================================================
    # SEARCH PLAN
    # ============================================================

    def _build_search_plan(
        self,
        product: ProductContext,
    ) -> List[Dict[str, str]]:

        search_plan = []

        # --------------------------------------------------------
        # PRODUCT / REGULATORY QUERY
        # --------------------------------------------------------

        if product.product_type:

            query = (
                f"{product.product_type} "
                f"{product.classification} "
                f"{product.form} "
                f"India legal requirements"
            )

            search_plan.append(
                {
                    "query_type": "product_regulatory",
                    "query": query,
                    "rag_domain": "regulatory",
                }
            )

        # --------------------------------------------------------
        # AYURVEDIC / PROPRIETARY FORMULATION
        # --------------------------------------------------------

        product_type = (
            product.product_type.lower()
            if product.product_type
            else ""
        )

        classification = (
            product.classification.lower()
            if product.classification
            else ""
        )

        if (
            "ayurvedic" in product_type
            or "proprietary" in classification
        ):

            query = (
                "Ayurvedic patent or proprietary medicine "
                "formulation ingredients India "
                "legal requirements"
            )

            search_plan.append(
                {
                    "query_type": "ayurvedic_formulation",
                    "query": query,
                    "rag_domain": "regulatory",
                }
            )

        # --------------------------------------------------------
        # INGREDIENTS
        # --------------------------------------------------------

        if product.ingredients:

            ingredients_text = " ".join(
                product.ingredients
            )

            query = (
                f"{ingredients_text} "
                f"{product.product_type} "
                f"India legal requirements"
            )

            search_plan.append(
                {
                    "query_type": "ingredients",
                    "query": query,
                    "rag_domain": "regulatory",
                }
            )

        # --------------------------------------------------------
        # BIOLOGICAL RESOURCES → ABS
        # --------------------------------------------------------

        if (
            str(product.uses_biological_resources).lower()
            == "yes"
        ):

            biological_resources = (
                product.biological_resources
                or product.ingredients
            )

            resources_text = " ".join(
                biological_resources
            )

            query = (
                f"{resources_text} "
                "biological resources "
                "India biodiversity law "
                "intellectual property rights "
                "approval requirements"
            )

            search_plan.append(
                {
                    "query_type": "biological_resources",
                    "query": query,
                    "rag_domain": "abs",
                }
            )

        # --------------------------------------------------------
        # TRADITIONAL KNOWLEDGE
        # --------------------------------------------------------

        if (
            str(product.traditional_knowledge).lower()
            == "yes"
        ):

            source = (
                product.traditional_knowledge_source
                or "traditional knowledge"
            )

            query = (
                f"{source} "
                "traditional knowledge "
                "Ayurvedic formulation "
                "intellectual property "
                "India"
            )

            # We do not assume that a tkdl domain definitely
            # exists because the diagnostic did not confirm it.
            #
            # The RAG search is performed without forcing
            # domain=tkdl.

            search_plan.append(
                {
                    "query_type": "traditional_knowledge",
                    "query": query,
                    "rag_domain": "auto",
                }
            )

        # --------------------------------------------------------
        # INNOVATION DESCRIPTION
        # --------------------------------------------------------

        if product.innovation_description:

            query = (
                f"{product.innovation_description} "
                "intellectual property "
                "legal considerations India"
            )

            search_plan.append(
                {
                    "query_type": "innovation",
                    "query": query,
                    "rag_domain": "auto",
                }
            )

        # --------------------------------------------------------
        # COMMERCIAL PRODUCT
        # --------------------------------------------------------

        if product.commercial_use:

            query = (
                f"{product.product_name} "
                "commercial product "
                "brand intellectual property "
                "India"
            )

            search_plan.append(
                {
                    "query_type": "commercial_use",
                    "query": query,
                    "rag_domain": "auto",
                }
            )

        return search_plan

    # ============================================================
    # RAG RETRIEVAL
    # ============================================================

    def _retrieve_legal_evidence(
        self,
        product: ProductContext,
        search_plan: List[Dict[str, str]],
        top_k: int,
    ) -> List[Dict[str, Any]]:

        evidence = []

        seen_evidence = set()

        context = self._build_rag_context(
            product
        )

        for search_item in search_plan:

            query = search_item["query"]

            rag_domain = (
                search_item["rag_domain"]
            )

            query_type = (
                search_item["query_type"]
            )

            try:

                # ------------------------------------------------
                # DOMAIN-SPECIFIC RETRIEVAL
                # ------------------------------------------------

                if rag_domain in [
                    "regulatory",
                    "abs",
                ]:

                    results = self.rag.search(

                        query=query,

                        context=context,

                        filters={
                            "domain": rag_domain
                        },

                        top_k=top_k,
                    )

                # ------------------------------------------------
                # AUTOMATIC RETRIEVAL
                # ------------------------------------------------

                else:

                    results = self.rag.search(

                        query=query,

                        context=context,

                        top_k=top_k,
                    )

                # ------------------------------------------------
                # EXTRACT RESULTS
                # ------------------------------------------------

                for result in results:

                    parsed_result = (
                        self._parse_rag_result(
                            result=result,
                            query_type=query_type,
                            query=query,
                        )
                    )

                    evidence_key = (
                        parsed_result["text"][:250]
                    )

                    if evidence_key in seen_evidence:

                        continue

                    seen_evidence.add(
                        evidence_key
                    )

                    evidence.append(
                        parsed_result
                    )

            except Exception as error:

                print(
                    "\nRAG retrieval warning:"
                )

                print(
                    f"Query type: {query_type}"
                )

                print(
                    f"Error: {error}"
                )

        return evidence

    # ============================================================
    # BUILD RAG CONTEXT
    # ============================================================

    def _build_rag_context(
        self,
        product: ProductContext,
    ) -> Dict[str, Any]:

        return {

            "product_name":
                product.product_name,

            "product_type":
                product.product_type,

            "classification":
                product.classification,

            "form":
                product.form,

            "ingredients":
                product.ingredients,

            "intended_use":
                product.intended_use,

            "claims":
                product.claims,

            "traditional_knowledge":
                product.traditional_knowledge,

            "traditional_knowledge_source":
                product.traditional_knowledge_source,

            "uses_biological_resources":
                product.uses_biological_resources,

            "biological_resources":
                product.biological_resources,

            "commercial_use":
                product.commercial_use,

            "jurisdiction":
                product.jurisdiction,
        }

    # ============================================================
    # PARSE RAG RESULT
    # ============================================================

    def _parse_rag_result(
        self,
        result: Any,
        query_type: str,
        query: str,
    ) -> Dict[str, Any]:

        result_dict = self._convert_to_dict(
            result
        )

        text = self._extract_value(
            result_dict,
            [
                "text",
                "content",
                "document",
                "page_content",
                "chunk",
            ],
        )

        metadata = self._extract_value(
            result_dict,
            [
                "metadata"
            ],
        )

        if not isinstance(
            metadata,
            dict
        ):

            metadata = {}

        domain = self._extract_value(
            metadata,
            [
                "domain",
                "category",
            ],
        )

        source = self._extract_value(
            metadata,
            [
                "source",
                "file_name",
                "document",
                "filename",
            ],
        )

        page = self._extract_value(
            metadata,
            [
                "page",
                "page_number",
            ],
        )

        score = self._extract_value(
            result_dict,
            [
                "score",
                "similarity_score",
                "distance",
            ],
        )

        return {

            "query_type":
                query_type,

            "query":
                query,

            "domain":
                domain,

            "source":
                source,

            "page":
                page,

            "score":
                score,

            "text":
                str(text),
        }

    # ============================================================
    # RESULT CONVERSION
    # ============================================================

    def _convert_to_dict(
        self,
        result: Any,
    ) -> Dict[str, Any]:

        if isinstance(
            result,
            dict
        ):

            return result

        if hasattr(
            result,
            "dict"
        ):

            try:

                return result.dict()

            except Exception:

                pass

        if hasattr(
            result,
            "model_dump"
        ):

            try:

                return result.model_dump()

            except Exception:

                pass

        if hasattr(
            result,
            "__dict__"
        ):

            return result.__dict__

        return {

            "text":
                str(result)
        }

    # ============================================================
    # EXTRACT VALUE
    # ============================================================

    def _extract_value(
        self,
        data: Dict[str, Any],
        possible_keys: List[str],
    ) -> Optional[Any]:

        for key in possible_keys:

            if key in data:

                return data[key]

        return None

    # ============================================================
    # LEGAL CONSIDERATIONS
    # ============================================================

    def _generate_legal_considerations(
        self,
        product: ProductContext,
    ) -> List[str]:

        considerations = []

        # --------------------------------------------------------
        # PATENT / INNOVATION
        # --------------------------------------------------------

        if product.innovation_description:

            considerations.append(

                "The product includes an innovation or "
                "formulation description. Patent relevance "
                "may require further review of novelty and "
                "existing prior art."
            )

        # --------------------------------------------------------
        # PROPRIETARY FORMULATION
        # --------------------------------------------------------

        if (
            product.classification.lower()
            == "proprietary formulation"
        ):

            considerations.append(

                "The product is described as a proprietary "
                "formulation. The formulation and its claims "
                "may require additional IP and regulatory review."
            )

        # --------------------------------------------------------
        # COMMERCIAL USE
        # --------------------------------------------------------

        if product.commercial_use:

            considerations.append(

                "The product is intended for commercial use. "
                "Trademark and branding considerations may be "
                "relevant."
            )

        # --------------------------------------------------------
        # TRADITIONAL KNOWLEDGE
        # --------------------------------------------------------

        if (
            str(product.traditional_knowledge).lower()
            == "yes"
        ):

            considerations.append(

                "The product involves traditional knowledge. "
                "Traditional knowledge and prior-art "
                "considerations may be relevant during "
                "IP evaluation."
            )

        # --------------------------------------------------------
        # BIOLOGICAL RESOURCES
        # --------------------------------------------------------

        if (
            str(product.uses_biological_resources).lower()
            == "yes"
        ):

            considerations.append(

                "The product uses biological resources. "
                "Access and benefit-sharing or biodiversity "
                "law considerations may require review."
            )

        # --------------------------------------------------------
        # INGREDIENTS
        # --------------------------------------------------------

        if product.ingredient_count > 1:

            considerations.append(

                "The product contains multiple ingredients. "
                "The combination and formulation may require "
                "additional prior-art and formulation review."
            )

        # --------------------------------------------------------
        # DEFAULT
        # --------------------------------------------------------

        if not considerations:

            considerations.append(

                "No specific IP or legal relevance indicators "
                "were identified from the currently available "
                "product information."
            )

        return considerations

    # ============================================================
    # SCREENING STATUS
    # ============================================================

    def _determine_screening_status(
        self,
        legal_evidence: List[Dict[str, Any]],
    ) -> str:

        if len(legal_evidence) == 0:

            return (
                "Screening completed, but no legal evidence "
                "was retrieved from the current RAG knowledge base."
            )

        return (
            "Preliminary IP and legal relevance screening "
            "completed with RAG-supported legal evidence."
        )

    # ============================================================
    # SUMMARY
    # ============================================================

    def _generate_summary(
        self,
        product: ProductContext,
        relevant_ip_domains: List[str],
        legal_evidence: List[Dict[str, Any]],
    ) -> str:

        domain_text = (
            ", ".join(relevant_ip_domains)
            if relevant_ip_domains
            else "no specific IP domains"
        )

        evidence_count = len(
            legal_evidence
        )

        if evidence_count == 0:

            return (

                f"Preliminary screening for "
                f"'{product.product_name}' identified "
                f"potential relevance to: {domain_text}. "
                f"No supporting legal evidence was retrieved "
                f"from the current RAG knowledge base."
            )

        evidence_domains = []

        for item in legal_evidence:

            domain = item.get(
                "domain"
            )

            if (
                domain
                and domain not in evidence_domains
            ):

                evidence_domains.append(
                    str(domain)
                )

        evidence_domain_text = (
            ", ".join(evidence_domains)
            if evidence_domains
            else "the current legal knowledge base"
        )

        return (

            f"Preliminary screening for "
            f"'{product.product_name}' identified "
            f"potential relevance to: {domain_text}. "
            f"The existing RAG system retrieved "
            f"{evidence_count} supporting legal evidence "
            f"item(s), primarily from: "
            f"{evidence_domain_text}. "
            f"This evidence is intended to support preliminary "
            f"legal relevance analysis and does not constitute "
            f"a comprehensive IP registry search."
        )