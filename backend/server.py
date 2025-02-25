from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict
import uuid
import requests

app = FastAPI()

documents = {}

class Document(BaseModel):
    title: str
    content: str
    metadata: Dict[str, str]

class SearchQuery(BaseModel):
    query: str
    top_k: int = 5

class ChatRequest(BaseModel):
    session_id: str
    message: str

@app.post("/api/documents")
def add_document(doc: Document):
    doc_id = str(uuid.uuid4())
    documents[doc_id] = doc.dict()
    return {"document_id": doc_id, "status": "success"}

@app.post("/api/search")
def search_documents(query: SearchQuery):
    results = [
        {"document_id": doc_id, "title": doc["title"], "snippet": doc["content"][:100]}
        for doc_id, doc in documents.items()
    ]
    return {"results": results[: query.top_k]}

@app.post("/api/chat")
def chat_with_ai(request: ChatRequest):
    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={"Authorization": f"Bearer YOUR_OPENAI_API_KEY"},
        json={
            "model": "gpt-4",
            "messages": [
                {"role": "system", "content": "あなたは企業のFAQ AIです。"},
                {"role": "user", "content": request.message},
            ],
            "temperature": 0.7,
        },
    )
    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="LLM APIエラー")
    return {"response": response.json()["choices"][0]["message"]["content"], "source_documents": list(documents.keys())}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
