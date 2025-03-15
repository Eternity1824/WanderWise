from fastapi import APIRouter, Query, Path, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from models.PlacePost import Base, engine, get_db
from models.UserNote import UserNote  # Import the UserNote model so it's registered with Base
from models.UserPlaceFavorites import UserPlaceFavorites  # Import the new model
from external.DeepSeek import deepseekapi
from external.GoogleMap import geocode_finder
from core.RoutePlanner import RoutePlanner
import json
from datetime import datetime
from core import process_data
from services.PlaceService import place_service
from services.PostService import post_service
from services.PlacePostService import place_post_service
from services.UserNoteService import user_note_service
from services.UserPlaceFavoritesService import user_place_favorites_service
from schemas.UserNoteSchema import UserNote as UserNoteSchema, UserNoteCreate
from schemas.UserPlaceFavoritesSchema import UserPlaceFavoriteCreate, UserPlaceFavoriteResponse, UserPlaceFavoriteCount

# Create all tables at import time
Base.metadata.create_all(bind=engine)

router = APIRouter()


@router.get("/search/ai-recommend", tags=["search ai"])
async def searchByAiRecommend(content: str = Query(None, description="search content"),
                 mode: str = Query("driving", description="交通方式", enum=["driving", "walking", "bicycling", "transit"])):
    # 传递内容到LLM获取地理点列表
    print("正在请求deepseek接口")
    locations, keywords = deepseekapi.process_user_query(content)
    # 存储所有地点的经纬度信息
    location_coordinates = []

    # 遍历locations列表，获取每个地点的地理编码信息
    for location in locations:
        geocode_result = geocode_finder.get_place_detail(location)

        # 检查结果是否有效
        if geocode_result["status"] == 'OK':
            latitude = geocode_result["geometry"]["location"]["lat"]
            longitude = geocode_result["geometry"]["location"]["lng"]
            if latitude and longitude:
                location_info = {
                    'name': geocode_result.get("name", ""),
                    'latitude': latitude,
                    'longitude': longitude,
                    'formatted_address': geocode_result.get("formatted_address", ""),
                    'formatted_phone_number': geocode_result.get("formatted_phone_number", ""),
                    'rating': geocode_result.get("rating", 0),
                    'url': geocode_result.get("url", ""),
                    'website': geocode_result.get("website", ""),
                    'weekday_text': geocode_result.get("weekday_text", []),
                    'photos': geocode_result.get("photos", [])
                }
        location_coordinates.append(location_info)

    planner = RoutePlanner(location_coordinates)
    southwest_route = planner.plan_route('southwest')
    route_detail = geocode_finder.get_route_details(southwest_route, mode)

    search_results = []
    places_set = set()  # Set to track unique place_ids

    for coordinates in route_detail['sampled_points']:
        latitude = coordinates['latitude']
        longitude = coordinates['longitude']
        places = place_service.search_places_by_location(latitude, longitude)
        if places["total"] > 0:
            for place in places["results"]:
                if place["status"] == 'OK':
                    place_id = place["place_id"]

                    # Skip if we've already processed this place
                    if place_id in places_set:
                        continue

                    # Add to our set of processed places
                    places_set.add(place_id)

                    # Create a new dictionary for each place
                    place_result = {}  # Create new dict inside loop
                    place_result["place"] = place

                    # Get notes for this place
                    notes = []
                    note_ids = place_post_service.get_notes_by_place_id(place_id)
                    for note_id in note_ids:
                        note = post_service.get_post_by_id(note_id)
                        if note:  # Make sure we got a valid note
                            notes.append(note)

                    place_result["notes"] = notes
                    search_results.append(place_result)

    # 返回包含经纬度和搜索结果的数据
    return {
        "route":southwest_route,
        "points":route_detail["all_points"],
        "places":search_results,
        "places_length":len(search_results),
        "mode":mode
    }
@router.get("/search/keyword", tags=["search keyword"])
async def searchByKeyword(keyword: str = Query(None, description="search content")):
    posts = post_service.search_by_keyword(keyword)
    return [{"message":"ok"}]

@router.get("/data/process", tags=["data clean"])
async def dataClean():


    # 创建所有定义的表
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(bind=engine)
    print("数据库表已创建")
    try:
        with open('data/search_contents_2025-03-11.json', 'r', encoding='utf-8') as f:
            posts_data = json.load(f)
    except Exception as e:
        print(f"加载数据失败: {str(e)}")
        posts_data = []  # 或使用示例数据

    valid_posts = process_data.process_data(posts_data, save_interval=50)

    try:
        with open('data/processed_search_contents.json', 'w', encoding='utf-8') as f:
            json.dump(valid_posts, f, ensure_ascii=False, indent=2)
        print(f"成功处理 {len(valid_posts)} 个有效posts，已保存到 processed_search_contents.json")
    except Exception as e:
        print(f"保存最终数据失败: {str(e)}")
    return [{"message": "success"}]

@router.get("/data/init/es", tags=["es init"])
async def esInit(post_path: str = Query("data/processed_search_contents.json", description="search content"),
                 place_path: str = Query("data/place_es_data.json", description="search content"),):
    post_result = post_service.delete_all_posts()
    print(f"删除了 {post_result['deleted']} 条数据")
    post_service.import_posts_from_json(post_path)

    place_result = place_service.delete_all_places()
    print(f"删除了 {place_result['deleted']} 条数据")
    place_service.import_places_from_json(place_path)
    return [{"message": "ok"}]

@router.get("/export/place", tags=["export place"])
async def exportPlace(path: str = Query("data/place_es_data.json", description="search content")):
    res = place_service.export_places_to_json(path)
    return [{"result":res}]

@router.get("/export/place_post", tags=["export place_post"])
async def export_place_post(path: str = Query("data/place_post_mysql_data.json", description="导出文件路径")):
    """
    导出地点-笔记映射数据到JSON文件
    """
    res = place_post_service.export_mappings_to_json(path)
    return {"result": res}

@router.get("/import/place_post", tags=["import place_post"])
async def import_place_post(
    path: str = Query("data/place_post_mysql_data.json", description="导入文件路径"),
    clear: bool = Query(True, description="是否清空现有数据")
):
    """
    从JSON文件导入地点-笔记映射数据
    """
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(bind=engine)
    print("数据库表已创建")
    res = place_post_service.import_mappings_from_json(path, clear)
    return {"result": res}

# User Note endpoints
@router.get("/user/{user_id}/notes/count", response_model=int, tags=["user notes"])
async def get_user_note_count(user_id: str = Path(..., description="User ID")):
    """
    Get the count of posts collected by a user
    """
    return user_note_service.get_user_note_count(user_id)

@router.post("/user/{user_id}/notes/add", response_model=UserNoteSchema, tags=["user notes"])
async def add_user_note(
    user_id: str = Path(..., description="User ID"),
    count: int = Query(1, description="Number to increment the count by")
):
    """
    Add or update a user's post count
    """
    return user_note_service.add_or_update_user_note_count(user_id, count)

@router.get("/users/notes", response_model=list[UserNoteSchema], tags=["user notes"])
async def get_all_user_notes():
    """
    Get all user note records
    """
    return user_note_service.get_all_user_notes()

@router.get("/user/notes/init", tags=["user notes"])
async def init_user_notes_table():
    """
    Initialize the user_notes table (clear and recreate)
    """
    Base.metadata.create_all(bind=engine)
    user_note_service.clear_database()
    return {"message": "User notes table initialized"}

# User Place Favorites endpoints
@router.post("/user/{user_id}/place/{place_id}/favorite", response_model=UserPlaceFavoriteResponse, tags=["user place favorites"])
async def add_place_favorite(
    user_id: str = Path(..., description="User ID"),
    place_id: str = Path(..., description="Place ID")
):
    """
    Add a place to a user's favorites (can be favorited multiple times)
    """
    favorite = user_place_favorites_service.add_favorite(user_id, place_id)
    if not favorite:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to add favorite"
        )
    return favorite

@router.get("/user/{user_id}/favorites", response_model=List[UserPlaceFavoriteResponse], tags=["user place favorites"])
async def get_user_favorites(
    user_id: str = Path(..., description="User ID")
):
    """
    Get all places a user has favorited
    """
    return user_place_favorites_service.get_user_favorites(user_id)

@router.get("/user/{user_id}/favorites/counts", response_model=List[UserPlaceFavoriteCount], tags=["user place favorites"])
async def get_user_favorite_counts(
    user_id: str = Path(..., description="User ID")
):
    """
    Get count of how many times a user favorited each place
    """
    return user_place_favorites_service.get_user_favorite_counts(user_id)

@router.get("/user/{user_id}/favorites/recent", response_model=List[UserPlaceFavoriteResponse], tags=["user place favorites"])
async def get_user_recent_favorites(
    user_id: str = Path(..., description="User ID"),
    limit: int = Query(10, description="Maximum number of records to return")
):
    """
    Get most recently favorited places by a user
    """
    return user_place_favorites_service.get_most_recently_favorited(user_id, limit)

@router.delete("/user/favorites/{favorite_id}", tags=["user place favorites"])
async def remove_favorite(
    favorite_id: int = Path(..., description="Favorite ID to remove")
):
    """
    Remove a specific favorite by ID
    """
    success = user_place_favorites_service.remove_favorite(favorite_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Favorite not found or failed to remove"
        )
    return {"message": "Favorite removed successfully"}