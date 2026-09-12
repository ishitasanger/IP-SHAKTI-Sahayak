"""
Regression test proving that a Pydantic-style assessment result with model_dump()
can pass through FinalIntegration.run() and roadmap generation without an AttributeError.
"""

import sys
from pathlib import Path
from typing import Any, Dict, List
from unittest.mock import MagicMock, patch
from pydantic import BaseModel

# Ensure repository root is on sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from backend.final_integration import FinalIntegration, normalize_assessment
from backend.IP.ip_checker import IPScreeningResult
from backend.Classification.classifier_wizard import WizardInput


class MockPydanticAssessment(BaseModel):
    product_name: str = "Ashwagandha Wellness Blend"
    relevant_ip_domains: List[str] = ["patent", "trademark"]
    screening_status: str = "Screening complete"
    summary: str = "IP screening identified patent and trademark domains."
    disclaimer: str = "Preliminary screening only."


def test_normalize_assessment_behavior():
    """Verify normalize_assessment converts model_dump() objects, preserves dicts, and leaves others."""
    # 1. Pydantic BaseModel instance with model_dump()
    pydantic_obj = MockPydanticAssessment()
    normalized_pydantic = normalize_assessment(pydantic_obj)
    assert isinstance(normalized_pydantic, dict)
    assert normalized_pydantic["relevant_ip_domains"] == ["patent", "trademark"]
    assert normalized_pydantic["product_name"] == "Ashwagandha Wellness Blend"

    # 2. IPScreeningResult instance with model_dump()
    ip_result = IPScreeningResult(
        product_name="Herbal Tea",
        relevant_ip_domains=["patent"],
        search_queries=[],
        legal_evidence=[],
        legal_considerations=[],
        screening_status="Complete",
        summary="Summary test",
        disclaimer="Disclaimer test",
    )
    normalized_ip = normalize_assessment(ip_result)
    assert isinstance(normalized_ip, dict)
    assert normalized_ip["relevant_ip_domains"] == ["patent"]

    # 3. Already a dictionary -> keep unchanged
    raw_dict = {"status": "ok", "overall_status": "Review"}
    normalized_dict = normalize_assessment(raw_dict)
    assert normalized_dict is raw_dict

    # 4. None or primitive -> unchanged
    assert normalize_assessment(None) is None
    assert normalize_assessment("string_val") == "string_val"
    assert normalize_assessment(123) == 123
    print("PASS: normalize_assessment handles model_dump, dicts, and primitives correctly.")


def test_final_integration_run_with_pydantic_assessment():
    """
    Regression test: verify that when orchestrator returns a Pydantic-style assessment
    with model_dump(), FinalIntegration.run() normalizes it and roadmap generation
    succeeds without "'MockPydanticAssessment' object has no attribute 'get'".
    """
    final_integration = FinalIntegration()

    # Mock the orchestrator to return a Pydantic model for ip_assessment
    pydantic_ip_assessment = MockPydanticAssessment()

    mock_orchestrator_result = {
        "product_context": {"product_name": "Ashwagandha Wellness Blend"},
        "ip_assessment": pydantic_ip_assessment,
        "regulatory_assessment": {"overall_status": "Review", "checks": {}},
        "tkdl_assessment": {"overall_status": "TKDL review required"},
        "abs_assessment": {"overall_status": "ABS review required"},
    }

    wizard_input = WizardInput(
        product_name="Ashwagandha Wellness Blend",
        product_type="ayurvedic medicine",
        classification="proprietary formulation",
        intended_use="stress relief",
        ingredients=["Ashwagandha"],
    )

    with patch.object(final_integration.orchestrator, "run", return_value=mock_orchestrator_result):
        # Mock RAG retrieval inside roadmap generator so test doesn't depend on external network/Groq
        with patch.object(final_integration.roadmap_generator, "retrieve_action_evidence", return_value=[]):
            result = final_integration.run(wizard_input)

    # Verify no AttributeError occurred
    assert "roadmap" in result
    assert isinstance(result["roadmap"], dict)
    assert "actions" in result["roadmap"]

    # Verify that the final returned assessment object contains dictionary for ip_assessment
    assert isinstance(result["ip_assessment"], dict), "ip_assessment was not normalized to dict in final result"
    assert result["ip_assessment"]["relevant_ip_domains"] == ["patent", "trademark"]

    # Verify roadmap actions were generated from the normalized ip_assessment domains
    actions = result["roadmap"]["actions"]
    action_types = [a["action_type"] for a in actions]
    assert "patent_filing" in action_types
    assert "trademark_registration" in action_types
    print("PASS: Pydantic-style assessment successfully passes through FinalIntegration.run() and roadmap generation.")


def test_final_integration_run_with_ipscreeningresult():
    """
    Regression test: verify that real IPScreeningResult object passes through
    FinalIntegration.run() and roadmap generation without "'IPScreeningResult' object has no attribute 'get'".
    """
    final_integration = FinalIntegration()

    ip_screening_result = IPScreeningResult(
        product_name="Ayush Herbal Formula",
        relevant_ip_domains=["trademark", "design"],
        search_queries=[],
        legal_evidence=[],
        legal_considerations=[],
        screening_status="Screening complete",
        summary="Identified trademark and design relevance.",
        disclaimer="Not legal advice.",
    )

    mock_orchestrator_result = {
        "product_context": {"product_name": "Ayush Herbal Formula"},
        "ip_assessment": ip_screening_result,
        "regulatory_assessment": {"overall_status": "No action", "checks": {}},
        "tkdl_assessment": {"overall_status": "No review"},
        "abs_assessment": {"overall_status": "No review"},
    }

    wizard_input = WizardInput(
        product_name="Ayush Herbal Formula",
        product_type="herbal medicine",
        classification="proprietary formulation",
        intended_use="skin care",
        ingredients=["Neem"],
    )

    with patch.object(final_integration.orchestrator, "run", return_value=mock_orchestrator_result):
        with patch.object(final_integration.roadmap_generator, "retrieve_action_evidence", return_value=[]):
            result = final_integration.run(wizard_input)

    assert "roadmap" in result
    assert isinstance(result["ip_assessment"], dict), "ip_assessment was not normalized to dict in final result"
    assert result["ip_assessment"]["relevant_ip_domains"] == ["trademark", "design"]

    action_types = [a["action_type"] for a in result["roadmap"]["actions"]]
    assert "trademark_registration" in action_types
    assert "design_registration" in action_types
    print("PASS: IPScreeningResult object successfully passes through FinalIntegration.run() and roadmap generation.")


def test_roadmap_evidence_retrieval_receives_and_filter():
    """
    Regression test confirming roadmap evidence retrieval passes exactly one
    top-level $and filter to the RAG search method for Chroma compatibility.
    """
    from backend.Roadmap.roadmap import RoadmapGenerator

    generator = RoadmapGenerator()
    action = {
        "action": "Patent filing",
        "action_type": "patent_filing",
        "domain": "ip",
        "query": "procedure for patent filing in India",
        "priority": 1,
    }

    with patch.object(generator.rag, "search", return_value=[]) as mock_search:
        generator.retrieve_action_evidence(action)

        mock_search.assert_called_once()
        call_kwargs = mock_search.call_args.kwargs
        filters = call_kwargs.get("filters", {})

        # Confirm exactly one top-level filter key and that it is "$and"
        assert list(filters.keys()) == ["$and"], f"Expected only ['$and'] as top-level key, got {list(filters.keys())}"
        and_clauses = filters["$and"]
        assert isinstance(and_clauses, list), f"Expected list for $and, got {type(and_clauses)}"
        assert {"domain": "ip"} in and_clauses
        assert {"jurisdiction": "India"} in and_clauses
        assert {"action_type": "patent_filing"} in and_clauses
        print("PASS: Roadmap evidence retrieval passes exactly one top-level $and filter.")


if __name__ == "__main__":
    print("Running FinalIntegration regression tests...")
    test_normalize_assessment_behavior()
    test_final_integration_run_with_pydantic_assessment()
    test_final_integration_run_with_ipscreeningresult()
    test_roadmap_evidence_retrieval_receives_and_filter()
    print("\nALL REGRESSION TESTS PASSED!")
