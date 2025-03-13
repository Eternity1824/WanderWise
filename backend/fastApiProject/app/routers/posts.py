from fastapi import APIRouter, Query
from external.deepseek import deepseekapi

router = APIRouter()

@router.get("/search/content", tags=["search"])
async def search(content: str = Query(None, description="search content")):
    #pass content to llm to get geo points list
    locations, keywords = deepseekapi.process_user_query(content)
    print(locations, keywords)
    return [{"locations": locations, "keywords": keywords}]

@router.get("/data/clean", tags=["data clean"])
async def clean():
    return [{"content": "hello"}]