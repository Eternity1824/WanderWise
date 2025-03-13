from fastapi import APIRouter, Query
from external.deepseek import deepseekapi
from external.googlemap import geocode_finder
router = APIRouter()

@router.get("/search/content", tags=["search"])
async def search(content: str = Query(None, description="search content")):
    #pass content to llm to get geo points list
    locations, keywords = deepseekapi.process_user_query(content)
    print(locations, keywords)
    for location in locations:
        print(geocode_finder.get_locations(location))
    #using return locations to get geocode from googlemap api

    #select posts in es and get ids and features

    #find the k closest points using recommend module and return ids

    #get detail info of posts in es using ids
    return [{"locations": locations, "keywords": keywords}]

@router.get("/data/clean", tags=["data clean"])
async def clean():
    return [{"content": "hello"}]