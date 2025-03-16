import requests
import json
import logging
import math
from typing import Dict, List, Any, Optional, Tuple
from config import get_settings

logger = logging.getLogger(__name__)


class GeocodeFinder:
    """
    Google Maps地理编码查询工具
    用于根据地点名称或地址查询坐标和路线规划
    """

    def __init__(self):
        """
        初始化地理编码查询工具
        """
        settings = get_settings()
        self.api_key = settings.GOOGLE_MAPS_API_KEY
        self.base_url = "https://maps.googleapis.com/maps/api/geocode/json"
        self.directions_url = "https://maps.googleapis.com/maps/api/directions/json"
        self.place_search_url = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json"
        self.place_details_url = "https://maps.googleapis.com/maps/api/place/details/json"

    def get_place_detail(self, place_name: str, region: Optional[str] = None, language: str = "en") -> Dict:
        """
        根据地点名称获取详细信息（包括地址、电话、评分、网址、营业时间和照片等）
        只返回前三条照片信息，每条照片只包含URL、高度和宽度

        Args:
            place_name: 地点名称
            region: 偏向的区域代码，例如"us"表示美国
            language: 返回结果的语言

        Returns:
            包含地点详细信息的字典
        """
        try:
            # 第一步：使用 Find Place API 找到地点的 place_id
            search_params = {
                "input": place_name,
                "inputtype": "textquery",
                "key": self.api_key,
                "language": language,
                "fields": "place_id,name,formatted_address,geometry"
            }

            if region:
                search_params["locationbias"] = f"region:{region}"

            search_response = requests.get(self.place_search_url, params=search_params, timeout=30)
            search_response.raise_for_status()
            search_result = search_response.json()

            # 检查搜索结果状态
            if search_result["status"] != "OK" or not search_result.get("candidates"):
                error_msg = f"未找到地点: {place_name}"
                if "error_message" in search_result:
                    error_msg += f" - {search_result['error_message']}"

                logger.error(error_msg)
                return {
                    "status": "ERROR",
                    "error_message": error_msg,
                    "query": place_name,
                    "details": None
                }

            # 获取第一个结果的 place_id
            place_id = search_result["candidates"][0]["place_id"]

            # 第二步：使用 Place Details API 获取详细信息
            details_params = {
                "place_id": place_id,
                "key": self.api_key,
                "language": language,
                "fields": "name,formatted_address,formatted_phone_number,geometry,rating,url,website,opening_hours,place_id,photos,types"
            }

            details_response = requests.get(self.place_details_url, params=details_params, timeout=30)
            details_response.raise_for_status()
            details_result = details_response.json()

            # 检查详情结果状态
            if details_result["status"] != "OK":
                error_msg = f"获取地点详情失败: {place_name}"
                if "error_message" in details_result:
                    error_msg += f" - {details_result['error_message']}"

                logger.error(error_msg)
                return {
                    "status": "ERROR",
                    "error_message": error_msg,
                    "query": place_name,
                    "details": None
                }

            # 提取并格式化详细信息
            place_info = details_result["result"]
            formatted_details = {
                "status": "OK",
                "query": place_name,
                "place_id": place_id,
                "name": place_info.get("name", ""),
                "formatted_address": place_info.get("formatted_address", ""),
                "geometry": {
                    "location": place_info.get("geometry", {}).get("location", {})
                },
                "formatted_phone_number": place_info.get("formatted_phone_number", ""),
                "rating": place_info.get("rating", 0),
                "url": place_info.get("url", ""),
                "website": place_info.get("website", "")
            }

            # 添加场所类型信息
            if "types" in place_info:
                formatted_details["types"] = place_info["types"]

                # 定义食物相关的场所类型列表
                food_related_types = [
                    # 主要食物场所类型
                    "restaurant", "cafe", "bakery", "bar", "food",
                    "meal_takeaway", "meal_delivery", "ice_cream",

                    # 甜品和饮料相关
                    "dessert", "coffee_shop", "tea", "juice_bar",
                    "bubble_tea", "smoothie_shop", "frozen_yogurt",

                    # 快餐和特定食物类型
                    "fast_food", "pizza_restaurant", "sandwich_shop",
                    "donut_shop", "pastry_shop", "confectionery",
                    "patisserie", "chocolate_shop",

                    # 各种餐饮场所
                    "diner", "bistro", "gastropub", "steakhouse",
                    "seafood_restaurant", "sushi_restaurant",
                    "bbq_restaurant", "noodle_shop", "ramen_restaurant",

                    # 酒类场所（通常也提供食物）
                    "wine_bar", "brewery", "pub", "night_club",

                    # 区域性/特色餐厅
                    "chinese_restaurant", "japanese_restaurant",
                    "italian_restaurant", "korean_restaurant",
                    "thai_restaurant", "vietnamese_restaurant",
                    "indian_restaurant", "mexican_restaurant",
                    "middle_eastern_restaurant", "french_restaurant",

                    # 超市和市场（通常有熟食区）
                    "supermarket", "grocery_store", "food_market",
                    "deli", "convenience_store", "market",

                    # 其他可能相关类型
                    "street_food", "hawker_centre", "food_court",
                    "canteen", "buffet", "dim_sum_restaurant",
                    "tapas_restaurant", "cafeteria", "snack_bar",
                    "hotpot_restaurant"
                ]

                # 检查是否为食物相关场所
                if any(food_type in place_info["types"] for food_type in food_related_types):
                    formatted_details["place_type"] = "food_place"
                else:
                    formatted_details["place_type"] = "view"

            # 添加营业时间（如果存在）
            if "opening_hours" in place_info and "weekday_text" in place_info["opening_hours"]:
                formatted_details["weekday_text"] = place_info["opening_hours"]["weekday_text"]

            # 添加照片信息（如果存在），只保留前三张照片，每张只包含URL、高度和宽度
            if "photos" in place_info:
                photos = []
                for photo in place_info["photos"][:3]:  # 只取前三条照片
                    photo_data = {
                        "height": photo.get("height"),
                        "width": photo.get("width"),
                        "photo_url": f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=800&photoreference={photo.get('photo_reference')}&key={self.api_key}"
                    }
                    photos.append(photo_data)

                formatted_details["photos"] = photos

            return formatted_details

        except Exception as e:
            logger.error(f"获取地点详情错误: {e}")
            return {
                "status": "ERROR",
                "error_message": str(e),
                "query": place_name,
                "details": None
            }

    def get_route_details(self,
                          route: List[Dict[str, Any]],
                          mode: str = "DRIVE",
                          language: str = "zh-CN",
                          sample_distance: int = 500,  # 每500米采样一个点
                          max_retries: int = 3) -> Dict:
        """
        获取路线的详细信息，包括polyline和采样后的坐标点

        Args:
            route: 路线途经点列表，每个点包含name、latitude、longitude等字段
            mode: 出行方式，可选值: DRIVE, WALK, BICYCLE, TRANSIT 或 driving, walking, bicycling, transit
            language: 结果语言，默认为中文
            sample_distance: 采样距离(米)，每隔多少米采样一个点用于ES查询
            max_retries: API请求失败时的最大重试次数

        Returns:
            包含路线详细信息的字典，同时包含前端所需的encoded_polyline和后端查询所需的采样点
        """
        if len(route) < 2:
            logger.error("路线至少需要包含起点和终点")
            return {
                "status": "ERROR",
                "error_message": "路线至少需要包含起点和终点",
                "waypoints": route,
                "route_details": None,
                "sampled_points": []
            }

        # 重试机制
        result = None
        error_msg = None

        for attempt in range(max_retries):
            try:
                # 构建起点和终点
                origin = f"{route[0]['latitude']},{route[0]['longitude']}"
                destination = f"{route[-1]['latitude']},{route[-1]['longitude']}"

                # 构建途经点
                waypoints = []
                if len(route) > 2:
                    for point in route[1:-1]:
                        waypoints.append(f"{point['latitude']},{point['longitude']}")

                # 转换travel_mode格式
                travel_mode = self._convert_travel_mode_to_directions(mode)

                # 构建请求参数
                params = {
                    "origin": origin,
                    "destination": destination,
                    "mode": travel_mode,
                    "key": self.api_key,
                    "language": language,
                    "units": "metric",
                    "alternatives": "false"
                }

                # 添加途经点参数
                if waypoints:
                    params["waypoints"] = "|".join(waypoints)

                # 记录请求参数（调试用）
                logger.debug(f"发送请求到 Directions API: {params}")

                # 发送请求到Directions API
                response = requests.get(self.directions_url, params=params, timeout=30)
                response.raise_for_status()
                result = response.json()

                # 检查API响应状态
                if result["status"] != "OK":
                    error_msg = f"Google Directions API返回错误: {result['status']}"
                    if "error_message" in result:
                        error_msg += f" - {result['error_message']}"

                    logger.warning(f"获取路线详情错误(尝试 {attempt + 1}/{max_retries}): {error_msg}")

                    if attempt == max_retries - 1:
                        return {
                            "status": "ERROR",
                            "error_message": error_msg,
                            "waypoints": route,
                            "route_details": None,
                            "sampled_points": []
                        }

                    continue  # 尝试下一次请求

                # 如果成功获取到结果，跳出重试循环
                break

            except Exception as e:
                error_msg = str(e)
                logger.warning(f"获取路线详情错误(尝试 {attempt + 1}/{max_retries}): {error_msg}")
                if attempt == max_retries - 1:
                    # 最后一次尝试也失败了
                    return {
                        "status": "ERROR",
                        "error_message": error_msg,
                        "waypoints": route,
                        "route_details": None,
                        "sampled_points": []
                    }

        # 获取第一条路线
        route_data = result["routes"][0]

        # 提取overview_polyline
        encoded_polyline = route_data.get("overview_polyline", {}).get("points", "")

        # 计算总距离和时间
        total_distance = 0
        total_duration = 0

        for leg in route_data.get("legs", []):
            total_distance += leg.get("distance", {}).get("value", 0)
            total_duration += leg.get("duration", {}).get("value", 0)

        # 处理路线基本信息
        route_details = {
            "encoded_polyline": encoded_polyline,
            "distance_meters": total_distance,
            "duration_seconds": total_duration,
            "legs": len(route_data.get("legs", [])),
            "waypoints": [
                {
                    "name": point.get("name", ""),
                    "latitude": point.get("latitude"),
                    "longitude": point.get("longitude")
                } for point in route
            ]
        }

        # 格式化距离和时间为可读格式
        route_details["distance_text"] = self._format_distance(total_distance)
        route_details["duration_text"] = self._format_duration(total_duration)

        # 解码polyline获取所有坐标点
        all_coordinates = []
        if encoded_polyline:
            try:
                all_coordinates = self._decode_polyline(encoded_polyline)
            except Exception as e:
                logger.error(f"解码polyline错误: {e}")

        # 采样坐标点用于ES查询
        sampled_points = self._sample_points_by_distance(all_coordinates, sample_distance)

        return {
            "status": "OK",
            "waypoints": route,
            "route_details": route_details,
            "sampled_points": sampled_points,
            "all_points": all_coordinates if len(all_coordinates) <= 1000 else sampled_points  # 防止返回过多点
        }

    def _convert_travel_mode_to_directions(self, mode: str) -> str:
        """
        将交通方式转换为Directions API格式

        Args:
            mode: 输入的交通方式

        Returns:
            Directions API格式的交通方式
        """
        mode_map = {
            "DRIVE": "driving",
            "WALK": "walking",
            "BICYCLE": "bicycling",
            "TRANSIT": "transit"
        }

        # 如果是大写格式，转换为小写格式
        if mode.upper() in mode_map:
            return mode_map[mode.upper()]

        # 如果已经是小写格式，检查是否有效
        if mode.lower() in ["driving", "walking", "bicycling", "transit"]:
            return mode.lower()

        # 默认返回驾车模式
        return "driving"

    def _format_duration(self, seconds: int) -> str:
        """
        将秒数格式化为可读时间

        Args:
            seconds: 秒数

        Returns:
            格式化的时间字符串
        """
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        if hours > 0:
            return f"{hours}小时{minutes}分钟"
        elif minutes > 0:
            return f"{minutes}分钟"
        else:
            return f"{seconds}秒"

    def _format_distance(self, meters: int) -> str:
        """
        将米数格式化为可读距离

        Args:
            meters: 米数

        Returns:
            格式化的距离字符串
        """
        if meters >= 1000:
            km = meters / 1000.0
            return f"{km:.1f}公里"
        else:
            return f"{meters}米"

    def _calculate_distance(self, point1: Dict[str, float], point2: Dict[str, float]) -> float:
        """
        计算两点之间的距离(米)

        Args:
            point1: 第一个点，包含latitude和longitude
            point2: 第二个点，包含latitude和longitude

        Returns:
            距离，单位为米
        """
        # 使用哈弗辛公式计算实际距离
        R = 6371000  # 地球半径，单位为米

        lat1_rad = math.radians(point1["latitude"])
        lon1_rad = math.radians(point1["longitude"])
        lat2_rad = math.radians(point2["latitude"])
        lon2_rad = math.radians(point2["longitude"])

        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad

        a = math.sin(dlat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        return R * c

    def _decode_polyline(self, encoded_polyline: str) -> List[Dict[str, float]]:
        """
        解码Google的polyline编码为坐标点列表

        Args:
            encoded_polyline: 编码后的polyline字符串

        Returns:
            解码后的坐标点列表
        """
        coordinates = []
        index = 0
        lat = 0
        lng = 0

        while index < len(encoded_polyline):
            # 解码纬度
            shift, result = 0, 0

            while True:
                if index >= len(encoded_polyline):
                    break
                b = ord(encoded_polyline[index]) - 63
                index += 1
                result |= (b & 0x1f) << shift
                shift += 5
                if b < 0x20:
                    break

            dlat = ~(result >> 1) if (result & 1) else (result >> 1)
            lat += dlat

            # 解码经度
            shift, result = 0, 0

            while True:
                if index >= len(encoded_polyline):
                    break
                b = ord(encoded_polyline[index]) - 63
                index += 1
                result |= (b & 0x1f) << shift
                shift += 5
                if b < 0x20:
                    break

            dlng = ~(result >> 1) if (result & 1) else (result >> 1)
            lng += dlng

            # 添加坐标点
            coordinates.append({
                "latitude": lat * 1e-5,
                "longitude": lng * 1e-5
            })

        return coordinates

    def _sample_points_by_distance(self, points: List[Dict[str, float]], sample_distance: float) -> List[
        Dict[str, float]]:
        """
        按照距离采样点

        Args:
            points: 完整坐标点列表
            sample_distance: 采样距离，单位为米

        Returns:
            采样后的坐标点列表
        """
        if not points:
            return []

        # 始终包含起点
        sampled_points = [points[0]]

        if len(points) == 1:
            return sampled_points

        # 最后一个采样点
        last_sampled = points[0]
        accumulated_distance = 0

        for i in range(1, len(points)):
            # 计算当前点与上一个点的距离
            distance = self._calculate_distance(points[i - 1], points[i])
            accumulated_distance += distance

            # 如果累计距离超过采样距离，添加该点并重置累计距离
            if accumulated_distance >= sample_distance:
                sampled_points.append(points[i])
                last_sampled = points[i]
                accumulated_distance = 0

        # 确保终点被包含
        if sampled_points[-1] != points[-1]:
            sampled_points.append(points[-1])

        return sampled_points


# 创建全局地理编码查询工具实例
geocode_finder = GeocodeFinder()

def main():
    import os
    from dotenv import load_dotenv
    import json

    # 测试通过地点名称获取详细信息
    place_name = "pike market"
    print(f"\n通过地点名称获取详细信息 ({place_name}):")
    place_details = geocode_finder.get_place_detail(place_name)

    # 漂亮地打印整个结果
    print("完整响应结果:")
    print(json.dumps(place_details, indent=2, ensure_ascii=False))

    # 打印关键信息
    if place_details["status"] == "OK":
        print("\n关键信息摘要:")
        print(f"地点名称: {place_details['name']}")
        print(f"地址: {place_details['formatted_address']}")
        print(f"电话: {place_details.get('formatted_phone_number', 'N/A')}")
        print(f"评分: {place_details.get('rating', 'N/A')}")
        print(f"网址: {place_details.get('website', 'N/A')}")

        # 打印位置信息
        location = place_details["geometry"]["location"]
        print(f"位置: 纬度={location.get('lat')}, 经度={location.get('lng')}")

        # 打印照片信息
        if "photos" in place_details:
            print(f"\n包含 {len(place_details['photos'])} 张照片:")
            for i, photo in enumerate(place_details['photos'][:3], 1):  # 只显示前3张
                print(f"照片 {i}: {photo['width']}x{photo['height']}")
                print(f"照片URL: {photo['photo_url']}")

            if len(place_details['photos']) > 3:
                print(f"... 还有 {len(place_details['photos']) - 3} 张照片未显示")


if __name__ == "__main__":
    main()

    """{
        "status": "OK",
        "query": "Ramen DANBO Capitol Hill 1222 E Pine St, Seattle, WA 98122",
        "place_id": "ChIJG6lbkM1qkFQRP8iOMgqQvvo",
        "name": "Ramen DANBO Capitol Hill",
        "formatted_address": "1222 E Pine St, Seattle, WA 98122, USA",
        "geometry": {
            "location": {
                "lat": 47.61540939999999,
                "lng": -122.3162501
            }
        },
        "formatted_phone_number": "(206) 566-5479",
        "rating": 4.5,
        "url": "https://maps.google.com/?cid=18068037128529299519",
        "website": "http://ramendanbo.com/",
        "weekday_text": [
            "Monday: 11:00 AM – 11:00 PM",
            "Tuesday: 11:00 AM – 11:00 PM",
            "Wednesday: 11:00 AM – 11:00 PM",
            "Thursday: 11:00 AM – 11:00 PM",
            "Friday: 11:00 AM – 11:00 PM",
            "Saturday: 11:00 AM – 11:00 PM",
            "Sunday: 11:00 AM – 11:00 PM"
        ],
        "photos": [
            {
                "height": 3024,
                "width": 4032,
                "photo_url": "https://maps.googleapis.com/maps/api/place/photo?maxwidth=800&photoreference=AUy1YQ2sdGAcJ38GxygY5O8RmOZfY1-UB6TtJ3Z9b-okiF9MveK0QquDcDvDvodOGbiCXQP-5DVE1gZUIQE5XBCIGXbadw8uFmBSWiX9qTFn8rKy1s_SVD8u9wj08LlS7mvmH2wZN-_tX5nCa8U_TOjwoASxz1pU36wDHGYSYs6QQ6gRdk_oxI3H1YR_oKgAnLcCTOgiLZOQPs6gTw0CE7QjUaTZe75FYKOz8uojhYXK2W3Evahl30HmihHvyDMGhePv6-nfQug2BrFDxZIJKosPag-fiEOv8iIM29Lyk4xeHQvhhwz0W4QUMYgqRSrJzR9ygVX8peVkKlk&key=AIzaSyD4K_0sPAIWmIE8jandYAlaNqMSTu9jAOY"
            },
            {
                "height": 3000,
                "width": 4000,
                "photo_url": "https://maps.googleapis.com/maps/api/place/photo?maxwidth=800&photoreference=AUy1YQ1dcGhqJVAJxruMFVlVNlbgOzZZW-wAwvv3k5Y1bKbaQVP27m0PGZVw48LAAhKbx5JfUsDypB394Qh3Rb1qA11X55EkN5En4uw80Cr390da4DQilOad5Khk0nMp0KpigGZ4HED1ram9h5RdQ3dOuB282btCJQY9klW5vIsF6_CUzl_9Qq1l7dLxUCtDk668aqeaHk_LgeoRtTR0eYEYPuUc5Auj10kz-J_FswNWbZR_ZKB1bDEg0XnmVfzWTGPYMM6uKLez9fEkB2m9r0krraWy8dzF7J0NEGRz0rcjKVKBg9v5DZJ6UKZyOunyI8F7ETufc9WEetA&key=AIzaSyD4K_0sPAIWmIE8jandYAlaNqMSTu9jAOY"
            },
            {
                "height": 3024,
                "width": 4032,
                "photo_url": "https://maps.googleapis.com/maps/api/place/photo?maxwidth=800&photoreference=AUy1YQ1GX3ylmSWHtPDBHCUcnfHnIUCVEumAX44pwnfed-UZoZQxFQbk22TeLzKxcKvuqsprRThHmt0LRSpLkZKoQV4wwMC7C-h0iG82uXfasPXpybrQ3FRoHNez3rZ5egWrZkveASXIHkXpSvcGCInkAzj8K8dizrkdvOwIvvsHP6k9LGD9uuUSok4emqgTXCu9Yf7ptOexhTsC1OEa4ulT_gyUYz7ovoEqVIwXWmU63-1VUTXzTdSvfvXSDXNXBU1XjPrmiAnqcdcNsJKixrRokE1aqF-PnH1xmVyk0lISicOjsLS8lGN9CsOeTbMiSsnXvCW41Ey6yLw&key=AIzaSyD4K_0sPAIWmIE8jandYAlaNqMSTu9jAOY"
            }
        ]
    }"""