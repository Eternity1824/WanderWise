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

    def get_locations(self, place_name: str, region: Optional[str] = None, language: str = "en") -> Dict:
        """
        根据地点名称或地址查询坐标，返回所有结果

        Args:
            place_name: 地点名称或地址
            region: 首选区域代码，如 "cn"
            language: 结果语言，默认为英文 "en"

        Returns:
            地理编码查询结果，包含多个位置信息
        """
        # 构建请求参数
        params = {
            "address": place_name,
            "key": self.api_key,
            "language": language
        }

        if region:
            params["region"] = region

        # 发送请求
        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            result = response.json()

            # 格式化返回结果
            return self._format_response(result, place_name)
        except Exception as e:
            logger.error(f"地理编码请求错误: {e}")
            return {
                "status": "ERROR",
                "error_message": str(e),
                "query": place_name,
                "results": []
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

    def _format_response(self, api_response: Dict, query: str) -> Dict:
        """
        格式化API响应为更易于使用的格式

        Args:
            api_response: Google Maps API的原始响应
            query: 原始查询

        Returns:
            格式化后的响应
        """
        formatted_response = {
            "status": api_response["status"],
            "query": query,
            "results": []
        }

        # 添加错误信息（如果有）
        if "error_message" in api_response:
            formatted_response["error_message"] = api_response["error_message"]

        # 如果状态为OK，处理结果
        if api_response["status"] == "OK":
            for location in api_response["results"]:
                # 提取核心信息
                formatted_location = {
                    "formatted_address": location["formatted_address"],
                    "latitude": location["geometry"]["location"]["lat"],
                    "longitude": location["geometry"]["location"]["lng"],
                    "location_type": location["geometry"]["location_type"],
                    "place_id": location["place_id"],
                    "types": location["types"]
                }

                # 提取地址组件
                address_components = {}
                for component in location["address_components"]:
                    for type_name in component["types"]:
                        address_components[type_name] = {
                            "long_name": component["long_name"],
                            "short_name": component["short_name"]
                        }

                formatted_location["address_components"] = address_components

                # 添加到结果列表
                formatted_response["results"].append(formatted_location)

        return formatted_response


# 创建全局地理编码查询工具实例
geocode_finder = GeocodeFinder()