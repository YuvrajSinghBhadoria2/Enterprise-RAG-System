from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from src.pipeline.query_pipeline import QueryPipeline

router = APIRouter()
_pipeline = None

def get_pipeline():
    global _pipeline
    if _pipeline is None:
        _pipeline = QueryPipeline()
    return _pipeline

class QueryRequest(BaseModel):
    query: str
    top_k_retrieval: Optional[int] = 20
    top_k_rerank: Optional[int] = 5
    use_hyde: Optional[bool] = False

class DocResponse(BaseModel):
    content: str
    score: float

class QueryResponse(BaseModel):
    query: str
    answer: str
    context: List[tuple]

@router.post("/chat", response_model=QueryResponse)
async def chat(request: QueryRequest):
    try:
        pipe = get_pipeline()
        
        result = pipe.run(
            query=request.query, 
            top_k_retrieval=request.top_k_retrieval,
            top_k_rerank=request.top_k_rerank
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
