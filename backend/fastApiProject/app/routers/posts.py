from fastapi import APIRouter, Query
from spyder.plugins.completion.providers.kite.utils.status import status

from external.deepseek import deepseekapi
from external.googlemap import geocode_finder
from services.elasticsearchService import es_service
from core.RoutePlanner import RoutePlanner
router = APIRouter()


@router.get("/search", tags=["search"])
async def search(content: str = Query(None, description="search content"),
                 mode: str = Query("driving", description="交通方式", enum=["driving", "walking", "bicycling", "transit"])):
    # 传递内容到LLM获取地理点列表
    print("正在请求deepseek接口")
    locations, keywords = deepseekapi.process_user_query(content)
    print(locations)

    # 存储所有地点的经纬度信息
    location_coordinates = []

    # 遍历locations列表，获取每个地点的地理编码信息
    for location in locations:
        geocode_result = geocode_finder.get_place_detail(location)
        print(geocode_result)

        # 检查结果是否有效
        if geocode_result["status"] == 'OK':
            for result in geocode_result.get('results', []):
                # 提取经纬度
                latitude = result.get('latitude')
                longitude = result.get('longitude')

                if latitude and longitude:
                    location_info = {
                        'name': location,
                        'latitude': latitude,
                        'longitude': longitude,
                        'formatted_address': result.get('formatted_address', ''),
                        'place_id': result.get('place_id', '')
                    }
                    location_coordinates.append(location_info)
    planner = RoutePlanner(location_coordinates)
    southwest_route = planner.plan_route('southwest')

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
async def clean():
    return [{"content": "hello"}]

@router.get("/data/init/es", tags=["es init"])
async def esInit():
    # 删除所有帖子数据
    result = es_service.delete_all_posts()
    print(f"删除了 {result['deleted']} 条数据")
    es_service.import_posts_from_json("data/processed_search_contents_2025-03-11_final.json")
    return [{"message": "ok"}]