"""
Unit and integration tests for FastAPI integration layer (backend/main.py).
Tests:
- GET /docs (Swagger UI availability)
- GET /openapi.json (schema registration for /api/assessment and /api/chat)
- POST /api/assessment (invalid data -> 422 error, valid data -> reaches FinalIntegration)
- POST /api/chat (valid request structure reaches IPShaktiChatbot)
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

# Ensure repository root is on sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_docs_available():
    """Verify that Swagger UI (/docs) is available."""
    response = client.get("/docs")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    assert "swagger-ui" in response.text.lower()
    print("PASS: /docs is accessible and serves Swagger UI.")


def test_openapi_schema_endpoints():
    """Verify that /api/assessment and /api/chat appear in OpenAPI schema."""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    paths = schema.get("paths", {})
    assert "/api/assessment" in paths, "POST /api/assessment missing from OpenAPI"
    assert "post" in paths["/api/assessment"]
    assert "/api/chat" in paths, "POST /api/chat missing from OpenAPI"
    assert "post" in paths["/api/chat"]
    print("PASS: Both /api/assessment and /api/chat are documented in OpenAPI schema.")


def test_assessment_invalid_data_returns_validation_error():
    """Verify that invalid wizard inputs return 422 validation errors, not a 500 crash."""
    # Case 1: Empty payload
    response = client.post("/api/assessment", json={})
    assert response.status_code == 422, f"Expected 422 for empty payload, got {response.status_code}"
    errors = response.json().get("detail", [])
    assert len(errors) > 0, "Expected validation error details"

    # Case 2: Invalid product_type
    invalid_payload = {
        "product_name": "Test Product",
        "product_type": "invalid_unknown_type",
        "classification": "proprietary formulation",
        "intended_use": "stress relief",
        "ingredients": ["Ashwagandha"],
        "jurisdiction": "India"
    }
    response = client.post("/api/assessment", json=invalid_payload)
    assert response.status_code == 422, f"Expected 422 for invalid product_type, got {response.status_code}"
    print("PASS: Invalid assessment data returns 422 validation errors without server crash.")


def test_assessment_valid_data_reaches_final_integration():
    """Verify that a valid assessment request reaches FinalIntegration and returns normalized shape."""
    valid_payload = {
        "product_name": "Ashwagandha Wellness Blend",
        "product_type": "ayurvedic medicine",
        "classification": "proprietary formulation",
        "intended_use": "stress relief and wellness",
        "ingredients": ["Ashwagandha", "Brahmi"],
        "claims": ["reduces stress"],
        "traditional_knowledge": "yes",
        "traditional_knowledge_source": "Charaka Samhita",
        "uses_biological_resources": "yes",
        "biological_resources": ["Ashwagandha", "Brahmi"],
        "jurisdiction": "India"
    }

    mock_run_result = {
        "product_context": {
            "product_name": "Ashwagandha Wellness Blend",
            "product_type": "ayurvedic medicine",
            "classification": "proprietary formulation"
        },
        "ip_assessment": {"status": "ok", "relevant_ip_domains": ["patent", "trademark"]},
        "regulatory_assessment": {"overall_status": "Review"},
        "tkdl_assessment": {"overall_status": "TKDL review required"},
        "abs_assessment": {"overall_status": "ABS review required"},
        "roadmap": {"status": "Action plan generated", "actions": []}
    }

    with patch("backend.main.FinalIntegration") as MockFinalIntegration:
        instance = MockFinalIntegration.return_value
        instance.run.return_value = mock_run_result

        response = client.post("/api/assessment", json=valid_payload)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

        # Verify FinalIntegration was called
        instance.run.assert_called_once()
        passed_input = instance.run.call_args[0][0]
        assert passed_input.product_name == "Ashwagandha Wellness Blend"

        # Verify normalized JSON response shape
        data = response.json()
        assert "legal_report" in data, "Response missing legal_report"
        assert "roadmap" in data, "Response missing roadmap"

        lr = data["legal_report"]
        assert "product_context" in lr
        assert "ip_assessment" in lr
        assert "regulatory_assessment" in lr
        assert "tkdl_assessment" in lr
        assert "abs_assessment" in lr

        assert lr["ip_assessment"]["status"] == "ok"
        assert data["roadmap"]["status"] == "Action plan generated"
        print("PASS: Valid assessment request reaches FinalIntegration and returns normalized shape.")


def test_chat_reaches_chatbot():
    """Verify that POST /api/chat reaches IPShaktiChatbot and returns answer and sources."""
    chat_payload = {
        "question": "Why is ABS compliance relevant to my product?",
        "product_context": {"product_name": "Ashwagandha Herbal Formulation"},
        "legal_report": {"abs_assessment": {"overall_status": "ABS review required"}},
        "roadmap": {"actions": [{"action": "ABS compliance"}]},
        "chat_history": [
            {"role": "user", "content": "Hello"}
        ]
    }

    mock_chat_result = {
        "answer": "ABS compliance is relevant because biological resources are used.",
        "sources": [{"document": "Biological Diversity Act", "section": "Section 3", "page": 1}]
    }

    with patch("backend.main.IPShaktiChatbot") as MockChatbot:
        instance = MockChatbot.return_value
        instance.answer.return_value = mock_chat_result

        response = client.post("/api/chat", json=chat_payload)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

        instance.answer.assert_called_once()
        call_kwargs = instance.answer.call_args[1]
        assert call_kwargs["question"] == "Why is ABS compliance relevant to my product?"
        assert call_kwargs["product_context"] == chat_payload["product_context"]
        assert call_kwargs["legal_report"] == chat_payload["legal_report"]
        assert call_kwargs["roadmap"] == chat_payload["roadmap"]
        assert len(call_kwargs["chat_history"]) == 1

        data = response.json()
        assert data["answer"] == mock_chat_result["answer"]
        assert len(data["sources"]) == 1
        print("PASS: Chat request reaches IPShaktiChatbot and returns expected shape.")


if __name__ == "__main__":
    print("Running API tests...")
    test_docs_available()
    test_openapi_schema_endpoints()
    test_assessment_invalid_data_returns_validation_error()
    test_assessment_valid_data_reaches_final_integration()
    test_chat_reaches_chatbot()
    print("\nALL API TESTS PASSED SUCCESSFULLY!")
