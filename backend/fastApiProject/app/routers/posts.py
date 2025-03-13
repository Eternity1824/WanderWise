from fastapi import APIRouter, Query
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
    print(locations, keywords)

    # 存储所有地点的经纬度信息
    location_coordinates = []

    # 遍历locations列表，获取每个地点的地理编码信息
    for location in locations:
        geocode_result = geocode_finder.get_locations(location)
        print(geocode_result)

        # 检查结果是否有效
        if geocode_result.get('status') == 'OK' and geocode_result.get('results'):
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

    points = geocode_finder.get_route_details(southwest_route, mode)


    # 根据经纬度搜索附近的地点
    search_results = []

    for coordinates in southwest_route:
        latitude = coordinates['latitude']
        longitude = coordinates['longitude']
        search_result = es_service.search_by_location(latitude, longitude, "1km")

        # 为每个位置添加搜索结果
        location_result = {
            'location_info': coordinates,
            'nearby_results': search_result
        }
        search_results.append(location_result)

    # 返回包含经纬度和搜索结果的数据
    return {
        "route":southwest_route,
        "points":points,
        "mode":mode
    }

@router.get("/data/clean", tags=["data clean"])
async def clean():
    return [{"content": "hello"}]