from http.client import HTTPException

from fastapi import APIRouter, Query, Path
from sipbuild.generator.parser.tokens import keywords

from models.PlacePost import Base, engine
from external.DeepSeek import deepseekapi
from external.GoogleMap import geocode_finder
from core.RoutePlanner import RoutePlanner
import json
from core import process_data
from services.PlaceService import place_service
from services.PostService import post_service
from services.PlacePostService import place_post_service
from ai.clustering.Recommend import findKClosestPlaces, findKClosestPosts
router = APIRouter()
@router.get("/search/recommend", tags=["search ai"])
async def searchByRecommend(content: str = Query(None, description="search content"),
                 mode: str = Query("driving", description="交通方式", enum=["driving", "walking", "bicycling", "transit"]),
                            userId: str = Query("0001", description="user id")):
    #根据userId拿到userfector
    keywords = []
    place_ids = set()
    while keywords == []:
        keywords = deepseekapi.associate(content)
    print(keywords)
    for keyword in keywords:
        search_results = post_service.search_by_keyword(keyword=keyword, size=100, score_weight=0.2)
        if search_results["total"] > 0:
            for post in search_results["results"]:
                ids = place_post_service.get_places_by_note_id(post["note_id"])
                for id in ids:
                    place_result = place_service.get_place_by_id(id)
                    if place_result["place_type"] == "view":
                        place_ids.add(id)
    place_ids = list(place_ids)
    recommend_place_ids = findKClosestPlaces(10, place_ids, userId)
    # 存储所有地点的经纬度信息
    location_coordinates = []
    # 遍历locations列表，获取每个地点的地理编码信息
    print(recommend_place_ids)
    for id in recommend_place_ids:
        geocode_result = place_service.get_place_by_id(id)
        print(geocode_result)
        # 检查结果是否有效
        if geocode_result["status"] == 'OK':
            latitude = geocode_result["geometry"]["location"]["lat"]
            longitude = geocode_result["geometry"]["location"]["lng"]
            if latitude and longitude:
                location_info = {
                    'latitude': latitude,
                    'longitude': longitude,
                }
        location_coordinates.append(location_info)
    planner = RoutePlanner(location_coordinates)
    southwest_route = planner.plan_route('southwest')
    print(southwest_route)
    route_detail = geocode_finder.get_route_details(southwest_route, mode)
    print(route_detail)
    search_results = []
    places_set = set()

    for coordinates in route_detail['sampled_points']:
        latitude = coordinates['latitude']
        longitude = coordinates['longitude']
        # 找到相关的places
        restaurants = place_service.search_places_mixed(latitude, longitude, distance="1km", placeType="food_place", size=5)
        views = place_service.search_places_mixed(latitude, longitude, distance="10km", placeType="view", size=5)
        places = []
        if restaurants["total"] > 0:
            places.extend(restaurants["results"])
        if views["total"] > 0:
            places.extend(views["results"])
        for place in places:
            if place["status"] == 'OK':
                place_id = place["place_id"]

                # Skip if we've already processed this place
                if place_id in places_set:
                    continue

                # Add to our set of processed places
                places_set.add(place_id)

                # Create a new dictionary for each place
                place_result = {}
                place_result["place"] = place

                # Get notes for this place
                notes = []
                note_ids = place_post_service.get_notes_by_place_id(place_id)
                for note_id in note_ids:
                    note = post_service.get_post_by_id(note_id)
                    if note:
                        notes.append(note)
                place_result["notes"] = notes
                search_results.append(place_result)

        # 返回包含经纬度和搜索结果的数据
        return {
            "route": southwest_route,
            "points": route_detail["all_points"],
            "places": search_results,
            "places_length": len(search_results),
            "mode": mode
        }
    return [{"message":len(place_ids)}]


@router.get("/search/ai-recommend", tags=["search ai"])
async def searchByAiRecommend(content: str = Query(None, description="search content"),
                 mode: str = Query("driving", description="交通方式", enum=["driving", "walking", "bicycling", "transit"])):
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
    places_set = set()

    for coordinates in route_detail['sampled_points']:
        latitude = coordinates['latitude']
        longitude = coordinates['longitude']
        #找到相关的places
        restaurants = place_service.search_places_mixed(latitude, longitude,distance= "100km", placeType ="food_place",size = 10)
        views = place_service.search_places_mixed(latitude, longitude, distance= "100km", placeType="view", size = 10)
        places = []
        if restaurants["total"] > 0:
            places.extend(restaurants["results"])
        if views["total"] > 0:
            places.extend(views["results"])
        for place in places:
            if place["status"] == 'OK':
                place_id = place["place_id"]

                # Skip if we've already processed this place
                if place_id in places_set:
                    continue

                # Add to our set of processed places
                places_set.add(place_id)

                # Create a new dictionary for each place
                place_result = {}
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
async def searchByKeyword(keyword: str = Query(None, description="search content"),
                          userId: str = Query("0001", description="user id")):
    keywords = []
    while keywords == []:
        keywords = deepseekapi.associate(keyword)
    print(keywords)
    post_ids = set()
    for k in keywords:
        search_results = post_service.search_by_keyword(k, size = 100, score_weight=0.2)
        if search_results["total"] > 0:
            for result in search_results["results"]:
                for id in result["note_id"]:
                    post_ids.add(id)
    post_ids = list(post_ids)
    recommend_post_ids = findKClosestPosts(10, post_ids, userId)

    search_results = []
    places_set = set()
    for post_id in recommend_post_ids:
        place_ids = place_post_service.get_places_by_note_id(post_id)
        for place_id in place_ids:
            place = place_service.get_place_by_id(place_id)
            if place["status"] == 'OK':
                place_id = place["place_id"]

                # Skip if we've already processed this place
                if place_id in places_set:
                    continue

                # Add to our set of processed places
                places_set.add(place_id)

                # Create a new dictionary for each place
                place_result = {}
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


    # 返回包含经纬度和搜索结果的数据 - 注意这个return被移到了循环外部
    return {
        "places": search_results,
        "places_length": len(search_results),
    }



@router.get("/data/process", tags=["data clean"])
async def dataProcess():
    # 创建所有定义的表
    #Base.metadata.drop_all(engine)
    Base.metadata.create_all(bind=engine)
    print("数据库表已创建")
    try:
        with open('data/merged_posts.json', 'r', encoding='utf-8') as f:
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

@router.get("/data/clear", tags=["data clear"])
async def dataClear():
    Base.metadata.drop_all(engine)
    place_service.delete_all_places()
    post_service.delete_all_posts()
    return [{"message": "success"}]

@router.get("/data/init/es", tags=["es init"])
async def esInit(post_path: str = Query("data/post_es_data.json", description="search content"),
                 place_path: str = Query("data/place_es_data.json", description="search content"),):
    post_result = post_service.delete_all_posts()
    print(f"删除了 {post_result['deleted']} 条数据")
    post_service.import_posts_from_json(post_path)

    place_result = place_service.delete_all_places()
    print(f"删除了 {place_result['deleted']} 条数据")
    place_service.import_places_from_json(place_path)
    return [{"message": "ok"}]

@router.get("/export/es/data", tags=["export data"])
async def export_es_data(
        place_path: str = Query("data/place_es_data.json", description="Path to save place data"),
        post_path: str = Query("data/post_es_data.json", description="Path to save post data")
):
    # 导出地点数据
    place_result = place_service.export_places_to_json(place_path)

    # 导出帖子数据
    post_result = post_service.export_posts_to_json(post_path)

    # 返回两个操作的结果
    return {
        "place_export": place_result,
        "post_export": post_result
    }
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


@router.get("/export/user/place", tags=["export user_place"])
async def export_user_place(
        user_id: str = Query("0001", description="User ID to export places for")):
    # Check if user_id is provided
    if user_id is None:
        return {"error": "user_id query parameter is required"}
    """
    Export a user's places with frequency counts.
    Reads post IDs from user_posts.txt and creates user_places.txt with place IDs and counts.
    """
    try:
        # Define file paths
        input_file = f"data/user{user_id}_posts.txt"
        output_file = f"data/user{user_id}_places.txt"

        # Read post IDs from file
        post_ids = []
        try:
            with open(input_file, 'r') as f:
                post_ids = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            return {"error": f"Input file not found: {input_file}"}

        if not post_ids:
            return {"message": "No posts found for this user"}

        # Collect all places with counts
        place_counter = {}
        for post_id in post_ids:
            places = place_post_service.get_places_by_note_id(post_id)
            for place in places:
                # Handle both string place_ids and object place with id attribute
                place_id = place if isinstance(place, str) else place.id
                if place_id in place_counter:
                    place_counter[place_id] += 1
                else:
                    place_counter[place_id] = 1

        # Sort places by frequency (descending)
        sorted_places = sorted(place_counter.items(), key=lambda x: x[1], reverse=True)

        # Write results to output file
        with open(output_file, 'w') as f:
            for place_id, count in sorted_places:
                f.write(f"{place_id} {count}\n")

        return {
            "message": "User places exported successfully",
            "input_file": input_file,
            "output_file": output_file,
            "post_count": len(post_ids),
            "place_count": len(place_counter)
        }
    except Exception as e:
        return {"error": f"Failed to export user places: {str(e)}"}
