from importlib import import_module

try:
    _fastapi = import_module("fastapi")
    FastAPI = _fastapi.FastAPI
    HTTPException = _fastapi.HTTPException
    CORSMiddleware = import_module("fastapi.middleware.cors").CORSMiddleware
except ImportError as exc:
    raise RuntimeError(
        "FastAPI is required to run this application. Install it with "
        "'pip install fastapi uvicorn'."
    ) from exc
try:
    BaseModel = import_module("pydantic").BaseModel
except ImportError as exc:
    raise RuntimeError(
        "Pydantic is required to run this application. Install it with "
        "'pip install pydantic'."
    ) from exc
from .rag.rag_engine import RAGEngine

# Initialize FastAPI App
app = FastAPI(title="IP-SHAKTI-Sahayak API")

# Setup CORS to allow Next.js frontend calls
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize RAG Engine
rag = RAGEngine()

class ChatRequest(BaseModel):
    question: str

@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        query = request.question.strip()
        if not query:
            raise HTTPException(status_code=400, detail="Question cannot be empty.")
        
        # Retrieve top results using your RAGEngine
        results = rag.search(query=query, top_k=5)
        
        if not results:
            return {"response": "No relevant IP legal documents found for your query."}

        # Format retrieved evidence into a response text
        response_text = "### Retrieved Legal Evidence:\n\n"
        for index, result in enumerate(results, start=1):
            response_text += f"**{index}. Document:** {result.document} (Section: {result.section}, Page: {result.page})\n"
            response_text += f"**Excerpt:** {result.text}\n\n"

        return {"response": response_text}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import subprocess
    import sys

    subprocess.run(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "backend.main:app",
            "--host",
            "127.0.0.1",
            "--port",
            "8000",
            "--reload",
        ],
        check=True,
    )