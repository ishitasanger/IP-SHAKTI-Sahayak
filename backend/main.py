from typing import Any, Dict, List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .Classification.classifier_wizard import WizardInput
from .final_integration import FinalIntegration
from .chatbot import IPShaktiChatbot

# Initialize FastAPI App
app = FastAPI(
    title="IP-SHAKTI-Sahayak API",
    description="FastAPI integration layer for IP-SHAKTI Sahayak IP and regulatory guidance.",
    version="1.0.0",
)

# Setup CORS to allow Next.js frontend calls during development
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    question: str
    product_context: Optional[Dict[str, Any]] = Field(default_factory=dict)
    legal_report: Optional[Dict[str, Any]] = Field(default_factory=dict)
    roadmap: Optional[Dict[str, Any]] = Field(default_factory=dict)
    chat_history: Optional[List[ChatMessage]] = Field(default_factory=list)


@app.post("/api/assessment")
async def assessment_endpoint(wizard_input: WizardInput):
    """
    Accepts wizard input, runs the multi-domain IP, Regulatory, TKDL, and ABS
    assessments along with roadmap generation via FinalIntegration, and returns
    the normalized legal report and roadmap.
    """
    try:
        result = FinalIntegration().run(wizard_input)
        return {
            "legal_report": {
                "product_context": result.get("product_context"),
                "ip_assessment": result.get("ip_assessment"),
                "regulatory_assessment": result.get("regulatory_assessment"),
                "tkdl_assessment": result.get("tkdl_assessment"),
                "abs_assessment": result.get("abs_assessment"),
            },
            "roadmap": result.get("roadmap") or {},
        }
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    """
    Accepts user question, product context, legal report, roadmap, and chat history,
    and returns source-grounded answers from IPShaktiChatbot.
    """
    try:
        result = IPShaktiChatbot().answer(
            question=request.question,
            product_context=request.product_context,
            legal_report=request.legal_report,
            roadmap=request.roadmap,
            chat_history=request.chat_history,
        )
        return result
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )