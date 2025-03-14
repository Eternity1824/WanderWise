from fastapi import APIRouter, Query
from spyder.plugins.completion.providers.kite.utils.status import status
from models.place_note_model import Base, engine
from external.deepseek import deepseekapi
from external.googlemap import geocode_finder
from services.ElasticSearch import es_service
from core.RoutePlanner import RoutePlanner
import json
from core import dataclean
router = APIRouter()


@router.get("/search", tags=["search"])
async def search(content: str = Query(None, description="search content"),
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
    print(southwest_route)
    route_detail = geocode_finder.get_route_details(southwest_route, mode)

    # 根据经纬度搜索附近的地点
    search_results = []
    seen_note_ids = set()
    print(route_detail)
    for coordinates in route_detail['sampled_points']:
        latitude = coordinates['latitude']
        longitude = coordinates['longitude']
        search_result = es_service.search_by_location(latitude, longitude)
        #print(search_result)
        for post in search_result['results']:
            note_id = post['note_id']
            if note_id not in seen_note_ids:
                search_results.append(post)
                seen_note_ids.add(note_id)

    # 返回包含经纬度和搜索结果的数据
    return {
        "route":southwest_route,
        "points":route_detail["all_points"],
        "posts":search_results,
        "posts_length":len(search_results),
        "mode":mode
    }

@router.get("/data/clean", tags=["data clean"])
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

    valid_posts = dataclean.process_posts(posts_data, save_interval=50)

    try:
        with open('data/processed_search_contents_2025-03-11_final.json', 'w', encoding='utf-8') as f:
            json.dump(valid_posts, f, ensure_ascii=False, indent=2)
        print(f"成功处理 {len(valid_posts)} 个有效posts，已保存到 processed_search_contents_2025-03-11_final.json")
    except Exception as e:
        print(f"保存最终数据失败: {str(e)}")
    return [{"message": "success"}]

@router.get("/data/init/es/post", tags=["es post init"])
async def esInit():
    result = es_service.delete_all_posts()
    print(f"删除了 {result['deleted']} 条数据")
    es_service.import_posts_from_json("data/processed_search_contents_2025-03-11_final.json")
    return [{"message": "ok"}]



