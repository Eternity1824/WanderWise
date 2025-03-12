import requests
import logging
from typing import Dict, List, Any, Optional
from ..config import get_settings

logger = logging.getLogger(__name__)


class GeocodeFinder:
    """
    Google Maps地理编码查询工具
    用于根据地点名称或地址查询坐标
    """

    def __init__(self):
        """
        初始化地理编码查询工具
        """
        settings = get_settings()
        self.api_key = settings.GOOGLE_MAPS_API_KEY
        self.base_url = "https://maps.googleapis.com/maps/api/geocode/json"

    def get_locations(self, place_name: str, region: Optional[str] = None, language: str = "en") -> Dict:
        """
        根据地点名称或地址查询坐标，返回所有结果

        Args:
            place_name: 地点名称或地址
            region: 首选区域代码，如 "cn"
            language: 结果语言，默认为中文 "zh-CN"

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