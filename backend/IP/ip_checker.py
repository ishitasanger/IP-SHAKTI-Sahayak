from typing import Any, Dict, List

from ..Classification.classifier_wizard import ProductContext
from ..rag.rag_engine import RAGEngine


class IPScreeningResult:
    """
    Structured result returned by the IP relevance checker.

    The IP module is responsible only for identifying potentially
    relevant IP protection domains and retrieving supporting
    IP-related evidence from the IP RAG knowledge base.

    It does not perform a comprehensive search of official
    patent, trademark or design registries.
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

        # Internal RAG/debugging information.
        self.search_queries = search_queries

        # Full retrieved evidence is kept internally.
        self.legal_evidence = legal_evidence

        self.evidence_count = len(legal_evidence)

        self.legal_considerations = legal_considerations
        self.screening_status = screening_status
        self.summary = summary
        self.disclaimer = disclaimer

    def to_dict(self) -> Dict[str, Any]:
        """
        Return only user-facing information.

        Raw retrieved text, similarity scores and search queries
        are NOT exposed to the frontend.

        legal_evidence is converted into a clean list of
        source citations.
        """

        sources = []

        for item in self.legal_evidence:

            source = (
                item.get("source")
                or item.get("document")
                or "Unknown source"
            )

            section = item.get("section")
            page = item.get("page")

            citation = str(source)

            if section and section != "Not specified":
                citation += f" — {section}"

            if page:
                citation += f", Page {page}"

            if citation not in sources:
                sources.append(citation)

        return {
            "product_name": self.product_name,
            "relevant_ip_domains": self.relevant_ip_domains,
            "legal_evidence": sources,
            "evidence_count": len(sources),
            "legal_considerations": self.legal_considerations,
            "screening_status": self.screening_status,
            "summary": self.summary,
            "disclaimer": self.disclaimer,
        }

    def model_dump(self, *args, **kwargs) -> Dict[str, Any]:
        """
        Allows compatibility with Pydantic-style normalization
        used by final_integration.py.
        """
        return self.to_dict()


class IPChecker:
    """
    Preliminary IP relevance screening.

    Responsibilities:
        - Identify potentially relevant IP domains.
        - Build IP-specific search queries.
        - Retrieve evidence ONLY from the IP RAG domain.
        - Provide concise IP-related considerations.

    IP domains currently considered:
        - Patent
        - Trademark
        - Design

    This module does NOT assess:
        - Regulatory compliance
        - TKDL / traditional knowledge
        - ABS / biodiversity compliance

    Those areas are handled independently by their respective
    modules.

    The system also does not perform a comprehensive search of
    official patent, trademark or design registries.
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

        # --------------------------------------------------------
        # Step 1: Identify potentially relevant IP domains
        # --------------------------------------------------------

        relevant_ip_domains = self._identify_ip_domains(product)

        # --------------------------------------------------------
        # Step 2: Build IP-specific RAG search plan
        # --------------------------------------------------------

        search_plan = self._build_search_plan(product)

        # --------------------------------------------------------
        # Step 3: Retrieve ONLY IP-domain evidence
        # --------------------------------------------------------

        legal_evidence = self._retrieve_legal_evidence(
            product=product,
            search_plan=search_plan,
            top_k=top_k,
        )

        # --------------------------------------------------------
        # Step 4: Generate deterministic IP considerations
        # --------------------------------------------------------

        legal_considerations = (
            self._generate_legal_considerations(product)
        )

        # --------------------------------------------------------
        # Step 5: Determine screening status
        # --------------------------------------------------------

        screening_status = (
            self._determine_screening_status(
                legal_evidence
            )
        )

        # --------------------------------------------------------
        # Step 6: Generate summary
        # --------------------------------------------------------

        summary = self._generate_summary(
            product=product,
            relevant_ip_domains=relevant_ip_domains,
            legal_evidence=legal_evidence,
        )

        disclaimer = (
            "This is an automated preliminary IP relevance "
            "screening result and not a legal opinion. The system "
            "retrieves IP-related information from the project's "
            "RAG knowledge base. It does not perform a "
            "comprehensive search of official patent, trademark "
            "or design registries. Professional legal review and "
            "official database searches may be required."
        )

        return IPScreeningResult(
            product_name=product.product_name,

            relevant_ip_domains=relevant_ip_domains,

            # Internal only.
            search_queries=[
                {
                    "query_type": item["query_type"],
                    "query_text": item["query"],
                    "rag_domain": item["rag_domain"],
                }
                for item in search_plan
            ],

            # Full evidence retained internally.
            # to_dict() converts it to clean source citations.
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
        #
        # Patent relevance is screened when there is an
        # innovation / formulation feature that may warrant
        # further patentability or prior-art review.
        #

        if (
            product.innovation_description
            or product.classification.lower()
            in [
                "proprietary formulation",
                "multi-ingredient formulation",
            ]
            or product.ingredient_count > 1
        ):
            domains.append("patent")

        # --------------------------------------------------------
        # TRADEMARK
        # --------------------------------------------------------
        #
        # Commercial use is treated as an indicator that
        # branding/trademark protection may be relevant.
        #

        if product.commercial_use:
            domains.append("trademark")

        # --------------------------------------------------------
        # DESIGN
        # --------------------------------------------------------
        #
        # Do not automatically mark every product as design
        # relevant.
        #
        # The current ProductContext does not contain a dedicated
        # design indicator, so design is not added automatically.
        #

        return domains

    # ============================================================
    # SEARCH PLAN
    # ============================================================

    def _build_search_plan(
        self,
        product: ProductContext,
    ) -> List[Dict[str, str]]:

        search_plan = []

        relevant_domains = self._identify_ip_domains(product)

        # --------------------------------------------------------
        # PATENT
        # --------------------------------------------------------

        if "patent" in relevant_domains:

            query_parts = [
                "patent",
                "Ayurvedic formulation",
                "intellectual property",
                "patentability",
                "prior art",
                "India",
            ]

            if product.innovation_description:
                query_parts.insert(
                    1,
                    product.innovation_description
                )

            search_plan.append(
                {
                    "query_type": "patent",
                    "query": " ".join(query_parts),
                    "rag_domain": "ip",
                }
            )

        # --------------------------------------------------------
        # TRADEMARK
        # --------------------------------------------------------

        if "trademark" in relevant_domains:

            search_plan.append(
                {
                    "query_type": "trademark",
                    "query": (
                        "trademark registration "
                        "brand protection "
                        "intellectual property "
                        "India"
                    ),
                    "rag_domain": "ip",
                }
            )

        # --------------------------------------------------------
        # DESIGN
        # --------------------------------------------------------

        if "design" in relevant_domains:

            search_plan.append(
                {
                    "query_type": "design",
                    "query": (
                        "industrial design protection "
                        "design registration "
                        "intellectual property "
                        "India"
                    ),
                    "rag_domain": "ip",
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

        context = self._build_rag_context(product)

        for search_item in search_plan:

            query = search_item["query"]
            query_type = search_item["query_type"]

            try:

                # IMPORTANT:
                # IP retrieval is explicitly restricted to
                # the IP RAG domain.
                #
                # This prevents Regulatory / ABS / TKDL
                # evidence from appearing in IP results.

                results = self.rag.search(
                    query=query,
                    context=context,
                    filters={
                        "domain": "ip"
                    },
                    top_k=top_k,
                )

                for result in results:

                    parsed_result = self._parse_rag_result(
                        result=result,
                        query_type=query_type,
                        query=query,
                    )

                    # ------------------------------------------------
                    # Deduplicate using source + section + page
                    # ------------------------------------------------

                    evidence_key = (
                        parsed_result.get("source"),
                        parsed_result.get("section"),
                        parsed_result.get("page"),
                    )

                    if evidence_key in seen_evidence:
                        continue

                    seen_evidence.add(evidence_key)

                    evidence.append(parsed_result)

            except Exception as error:

                print("\nIP RAG retrieval warning:")
                print(f"Query type: {query_type}")
                print(f"Error: {error}")

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

        result_dict = self._convert_to_dict(result)

        # --------------------------------------------------------
        # Extract text
        # --------------------------------------------------------

        text = self._extract_value(
            result_dict,
            [
                "text",
                "content",
                "page_content",
                "chunk",
                "document",
            ],
        )

        # --------------------------------------------------------
        # Extract metadata
        # --------------------------------------------------------

        metadata = self._extract_value(
            result_dict,
            [
                "metadata",
            ],
        )

        if not isinstance(metadata, dict):
            metadata = {}

        # --------------------------------------------------------
        # Domain
        # --------------------------------------------------------

        domain = (
            self._extract_value(
                metadata,
                [
                    "domain",
                    "category",
                ],
            )
            or self._extract_value(
                result_dict,
                [
                    "domain",
                    "category",
                ],
            )
        )

        # --------------------------------------------------------
        # Source / document
        # --------------------------------------------------------

        source = (
            self._extract_value(
                metadata,
                [
                    "source",
                    "file_name",
                    "document",
                    "filename",
                ],
            )
            or self._extract_value(
                result_dict,
                [
                    "source",
                    "file_name",
                    "document",
                    "filename",
                ],
            )
        )

        # --------------------------------------------------------
        # Section
        # --------------------------------------------------------

        section = (
            self._extract_value(
                metadata,
                [
                    "section",
                    "section_name",
                ],
            )
            or self._extract_value(
                result_dict,
                [
                    "section",
                    "section_name",
                ],
            )
        )

        # --------------------------------------------------------
        # Page
        # --------------------------------------------------------

        page = (
            self._extract_value(
                metadata,
                [
                    "page",
                    "page_number",
                ],
            )
            or self._extract_value(
                result_dict,
                [
                    "page",
                    "page_number",
                ],
            )
        )

        # --------------------------------------------------------
        # Score
        # --------------------------------------------------------

        score = self._extract_value(
            result_dict,
            [
                "score",
                "similarity_score",
                "distance",
            ],
        )

        return {
            # Internal fields
            "query_type":
                query_type,

            "query":
                query,

            "domain":
                domain,

            "source":
                source,

            "section":
                section,

            "page":
                page,

            "score":
                score,

            "text":
                str(text or ""),
        }

    # ============================================================
    # RESULT CONVERSION
    # ============================================================

    def _convert_to_dict(
        self,
        value: Any,
    ) -> Dict[str, Any]:

        if isinstance(value, dict):
            return value

        if hasattr(value, "model_dump"):
            try:
                return value.model_dump()
            except Exception:
                pass

        if hasattr(value, "dict"):
            try:
                return value.dict()
            except Exception:
                pass

        if hasattr(value, "to_dict"):
            try:
                return value.to_dict()
            except Exception:
                pass

        if hasattr(value, "__dict__"):
            try:
                return vars(value)
            except Exception:
                pass

        return {}

    # ============================================================
    # EXTRACT VALUE
    # ============================================================

    def _extract_value(
        self,
        data: Any,
        keys: List[str],
    ) -> Any:

        if not isinstance(data, dict):
            return None

        for key in keys:

            value = data.get(key)

            if value is not None:
                return value

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
                "formulation description. Patent relevance may "
                "require further review of novelty and existing "
                "prior art."
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
                "formulation. The formulation may warrant "
                "additional patent and prior-art review."
            )

        # --------------------------------------------------------
        # COMMERCIAL USE / TRADEMARK
        # --------------------------------------------------------

        if product.commercial_use:

            considerations.append(
                "The product is intended for commercial use. "
                "Trademark and branding protection may be "
                "relevant."
            )

        # --------------------------------------------------------
        # MULTIPLE INGREDIENTS
        # --------------------------------------------------------

        if product.ingredient_count > 1:

            considerations.append(
                "The product contains multiple ingredients. "
                "The combination and formulation may warrant "
                "additional patentability and prior-art review."
            )

        # --------------------------------------------------------
        # FALLBACK
        # --------------------------------------------------------

        if not considerations:

            considerations.append(
                "No specific patent, trademark or design "
                "relevance indicators were identified from the "
                "currently available product information."
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
                "IP screening completed, but no supporting "
                "IP evidence was retrieved from the current "
                "IP RAG knowledge base."
            )

        return (
            "Preliminary IP relevance screening completed "
            "with RAG-supported IP evidence."
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

        evidence_count = len(legal_evidence)

        if evidence_count == 0:

            return (
                f"Preliminary IP screening for "
                f"'{product.product_name}' identified potential "
                f"relevance to: {domain_text}. No supporting IP "
                f"evidence was retrieved from the current IP "
                f"knowledge base."
            )

        return (
            f"Preliminary IP screening for "
            f"'{product.product_name}' identified potential "
            f"relevance to: {domain_text}. The IP RAG system "
            f"retrieved {evidence_count} supporting IP evidence "
            f"item(s). This screening is intended to identify "
            f"potential IP relevance and does not constitute a "
            f"comprehensive official IP registry search."
        )