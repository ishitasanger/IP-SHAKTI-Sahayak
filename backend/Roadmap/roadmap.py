from typing import Any, Dict, List

from rag.rag_engine import RAGEngine


class RoadmapGenerator:
    """
    Generates an actionable roadmap from the assessment results.

    The roadmap does NOT hardcode legal/procedural information.
    It identifies the required action pathway, retrieves relevant
    procedural evidence through RAG, and returns grounded actions.
    """

    # These are retrieval intents, NOT legal answers.
    ACTION_PATHWAYS = {
        "patent": {
            "action": "Patent filing",
            "action_type": "patent_filing",
            "domain": "ip",
            "query": (
                "procedure, requirements and official route "
                "for filing a patent application in India"
            ),
        },

        "trademark": {
            "action": "Trademark registration",
            "action_type": "trademark_registration",
            "domain": "ip",
            "query": (
                "procedure, requirements and official route "
                "for trademark registration in India"
            ),
        },

        "design": {
            "action": "Design registration",
            "action_type": "design_registration",
            "domain": "ip",
            "query": (
                "procedure, requirements and official route "
                "for design registration in India"
            ),
        },

        "licensing": {
            "action": "Regulatory licensing and compliance",
            "action_type": "regulatory_licensing",
            "domain": "regulatory",
            "query": (
                "licensing registration requirements and "
                "regulatory compliance procedure in India"
            ),
        },

        "tk": {
            "action": "Traditional knowledge / prior-art review",
            "action_type": "tk_prior_art",
            "domain": "tkdl",
            "query": (
                "traditional knowledge prior art verification "
                "and TKDL review procedure in India"
            ),
        },

        "abs": {
            "action": "ABS compliance",
            "action_type": "abs_compliance",
            "domain": "abs",
            "query": (
                "access benefit sharing ABS compliance "
                "procedure requirements and official process in India"
            ),
        },
    }

    def __init__(self, top_k: int = 5):
        self.rag = RAGEngine()
        self.top_k = top_k

    # ---------------------------------------------------------
    # 1. Identify required actions from assessment results
    # ---------------------------------------------------------

    def identify_actions(
        self,
        ip_assessment: Dict[str, Any] | None = None,
        regulatory_assessment: Dict[str, Any] | None = None,
        tkdl_assessment: Dict[str, Any] | None = None,
        abs_assessment: Dict[str, Any] | None = None,
    ) -> List[Dict[str, Any]]:

        actions = []

        # -------------------------
        # IP
        # -------------------------

        if ip_assessment:
            domains = ip_assessment.get("relevant_ip_domains", [])

            if self._contains(domains, "patent"):
                actions.append(
                    self._create_action("patent", priority=1)
                )

            if self._contains(domains, "trademark"):
                actions.append(
                    self._create_action("trademark", priority=2)
                )

            if self._contains(domains, "design"):
                actions.append(
                    self._create_action("design", priority=3)
                )

        # -------------------------
        # Regulatory
        # -------------------------

        if regulatory_assessment:
            checks = regulatory_assessment.get("checks", {})

            if self._assessment_needs_action(checks):
                actions.append(
                    self._create_action("licensing", priority=4)
                )

        # -------------------------
        # TKDL
        # -------------------------

        if tkdl_assessment:
            overall_status = str(
                tkdl_assessment.get("overall_status", "")
            ).lower()

            if (
                "review" in overall_status
                or "attention" in overall_status
            ):
                actions.append(
                    self._create_action("tk", priority=5)
                )

        # -------------------------
        # ABS
        # -------------------------

        if abs_assessment:
            overall_status = str(
                abs_assessment.get("overall_status", "")
            ).lower()

            if (
                "review" in overall_status
                or "attention" in overall_status
            ):
                actions.append(
                    self._create_action("abs", priority=6)
                )

        return actions

    # ---------------------------------------------------------
    # 2. Create action pathway
    # ---------------------------------------------------------

    def _create_action(
        self,
        pathway: str,
        priority: int
    ) -> Dict[str, Any]:

        config = self.ACTION_PATHWAYS[pathway]

        return {
            "priority": priority,
            "domain": config["domain"],
            "action": config["action"],
            "action_type": config["action_type"],
            "query": config["query"],
        }

    # ---------------------------------------------------------
    # 3. Retrieve procedural evidence from RAG
    # ---------------------------------------------------------

    def retrieve_action_evidence(
        self,
        action: Dict[str, Any]
    ) -> List[Dict[str, Any]]:

        results = self.rag.search(
            query=action["query"],
            filters={
                "domain": action["domain"],
                "jurisdiction": "India",
                "action_type": action["action_type"],
            },
            top_k=self.top_k,
        )

        evidence = []

        for result in results:
            evidence.append(
                {
                    "document": result.document,
                    "section": result.section,
                    "page": result.page,
                    "source_file": result.source_file,
                    "source_url": result.metadata.get(
                        "source_url"
                    ),
                    "text": result.text,
                    "score": result.score,
                }
            )

        return evidence

    # ---------------------------------------------------------
    # 4. Generate roadmap
    # ---------------------------------------------------------

    def generate(
        self,
        ip_assessment: Dict[str, Any] | None = None,
        regulatory_assessment: Dict[str, Any] | None = None,
        tkdl_assessment: Dict[str, Any] | None = None,
        abs_assessment: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:

        actions = self.identify_actions(
            ip_assessment=ip_assessment,
            regulatory_assessment=regulatory_assessment,
            tkdl_assessment=tkdl_assessment,
            abs_assessment=abs_assessment,
        )

        roadmap_actions = []

        for action in actions:

            evidence = self.retrieve_action_evidence(action)

            roadmap_actions.append(
                {
                    "priority": action["priority"],
                    "domain": action["domain"],
                    "action": action["action"],
                    "action_type": action["action_type"],
                    "evidence": evidence,
                    "human_escalation": self._needs_human_escalation(
                        action,
                        evidence
                    ),
                }
            )

        return {
            "status": (
                "Action plan generated"
                if roadmap_actions
                else "No immediate action identified"
            ),
            "actions": roadmap_actions,
            "disclaimer": (
                "This roadmap provides information based on "
                "retrieved official sources and is not legal advice."
            ),
        }

    # ---------------------------------------------------------
    # Helpers
    # ---------------------------------------------------------

    @staticmethod
    def _contains(items: Any, keyword: str) -> bool:

        if not isinstance(items, list):
            return False

        keyword = keyword.lower()

        return any(
            keyword in str(item).lower()
            for item in items
        )

    @staticmethod
    def _assessment_needs_action(
        checks: Dict[str, Any]
    ) -> bool:

        if not checks:
            return False

        for check in checks.values():

            if isinstance(check, dict):

                status = str(
                    check.get("status", "")
                ).lower()

                if status in {
                    "attention",
                    "review",
                    "required",
                    "applicable",
                }:
                    return True

        return False

    @staticmethod
    def _needs_human_escalation(
        action: Dict[str, Any],
        evidence: List[Dict[str, Any]]
    ) -> bool:

        # No reliable procedural evidence → human review.
        if not evidence:
            return True

        # Patent/TK/ABS decisions can require professional review
        # when evidence is insufficient or interpretation is needed.
        if action["action_type"] in {
            "patent_filing",
            "tk_prior_art",
            "abs_compliance",
        }:
            return True

        return False


# -------------------------------------------------------------
# Convenience function
# -------------------------------------------------------------

def generate_roadmap(
    ip_assessment=None,
    regulatory_assessment=None,
    tkdl_assessment=None,
    abs_assessment=None,
):

    generator = RoadmapGenerator()

    return generator.generate(
        ip_assessment=ip_assessment,
        regulatory_assessment=regulatory_assessment,
        tkdl_assessment=tkdl_assessment,
        abs_assessment=abs_assessment,
    )