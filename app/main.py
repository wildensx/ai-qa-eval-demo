import os
from pathlib import Path

from fastapi import FastAPI, Header, HTTPException, Query
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from .assistant import answer
from .documents import DOCUMENTS

app = FastAPI(title="Lumen Travel policy assistant (demo)")
UI = Path(__file__).with_name("ui.html")


class Question(BaseModel):
    question: str = Field(min_length=3, max_length=500)


def require_key(x_api_key):
    if x_api_key != os.environ.get("DEMO_API_KEY", "demo-key"):
        raise HTTPException(status_code=401, detail="Invalid or missing API key")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/documents")
def list_documents(limit: int = Query(10, ge=1, le=50), offset: int = Query(0, ge=0)):
    page = DOCUMENTS[offset:offset + limit]
    return {"total": len(DOCUMENTS), "limit": limit, "offset": offset,
            "items": [{"id": d["id"], "title": d["title"]} for d in page]}


@app.get("/documents/{doc_id}")
def get_document(doc_id: str):
    for doc in DOCUMENTS:
        if doc["id"] == doc_id:
            return doc
    raise HTTPException(status_code=404, detail="Document not found")


@app.post("/ask")
def ask(body: Question, x_api_key: str | None = Header(default=None)):
    require_key(x_api_key)
    return answer(body.question)


@app.get("/", response_class=HTMLResponse)
def ui():
    return UI.read_text(encoding="utf-8")
