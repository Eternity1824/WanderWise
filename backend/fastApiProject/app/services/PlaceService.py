from typing import Dict, Any, Optional, List
from core.ElasticsearchCore import es_core
from config import get_settings

settings = get_settings()


class PlaceService:
    """PlaceService 处理与地点相关的所有操作"""

    def __init__(self):
        """初始化 PlaceService"""
        self.place_index_name = f"{settings.ELASTICSEARCH_INDEX_PREFIX}places"
        self._create_place_index_if_not_exists()

    def _create_place_index_if_not_exists(self) -> None:
        """如果地点索引不存在则创建索引，设置好映射关系"""
        mappings = {
            "mappings": {
                "properties": {
                    "place_id": {"type": "keyword", "index": "true"},
                    "name": {"type": "text", "analyzer": "ik_max_word", "search_analyzer": "ik_smart"},
                    "location": {"type": "geo_point"},
                    "place_type":{"type": "keyword"},
                }
            },
            "settings": {
                "analysis": {
                    "analyzer": {
                        "ik_smart": {
                            "type": "custom",
                            "tokenizer": "ik_smart"
                        },
                        "ik_max_word": {
                            "type": "custom",
                            "tokenizer": "ik_max_word"
                        }
                    }
                }
            }
        }
        es_core.create_index_if_not_exists(self.place_index_name, mappings)

    def _process_place_data(self, place: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        处理地点数据，添加geo_point字段

        Args:
            place: 原始地点数据

        Returns:
            处理后的地点数据，或者None（如果缺少place_id）
        """
        # 创建数据副本，避免修改原始数据
        place_data = place.copy()

        # 确保place_id存在
        if "place_id" not in place_data:
            return None

        # 添加geo_point格式的位置数据
        if "geometry" in place_data and "location" in place_data["geometry"]:
            place_data["location"] = {
                "lat": place_data["geometry"]["location"]["lat"],
                "lon": place_data["geometry"]["location"]["lng"]
            }

        return place_data

    def add_place(self, place: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        添加单个地点到Elasticsearch，如果已存在相同ID则跳过

        Args:
            place: 包含地点数据的字典（Google Places API返回的格式）

        Returns:
            Elasticsearch的响应，或None（如果地点已存在或缺少place_id）
        """
        # 处理地点数据
        place_data = self._process_place_data(place)
        if not place_data:
            raise ValueError("地点数据必须包含place_id字段")

        # 检查ID是否已存在
        place_id = place_data["place_id"]
        exists = es_core.get_by_id(self.place_index_name, place_id) is not None
        if exists:
            return None

        # 添加地点
        return es_core.add_item(
            index_name=self.place_index_name,
            item=place_data,
            doc_id=place_id
        )

    def import_places_from_json(self, json_file_path: str) -> Dict[str, Any]:
        """
        从JSON文件导入地点数据

        Args:
            json_file_path: JSON文件路径

        Returns:
            包含导入状态信息的字典
        """
        return es_core.import_from_json(
            json_file_path=json_file_path,
            index_name=self.place_index_name,
            process_item_func=self._process_place_data,
            doc_id_field="place_id"
        )

    def get_place_by_id(self, place_id: str) -> Optional[Dict[str, Any]]:
        """
        根据ID获取单个地点

        Args:
            place_id: 地点ID (Google Place ID)

        Returns:
            地点数据或None（如果不存在）
        """
        return es_core.get_by_id(self.place_index_name, place_id)

    def search_places_by_name(self, name: str, size: int = 10, from_: int = 0) -> Dict[str, Any]:
        """
        根据名称搜索地点

        Args:
            name: 搜索关键词
            size: 返回结果数量
            from_: 分页起始位置

        Returns:
            搜索结果
        """
        query = {
            "query": {
                "multi_match": {
                    "query": name,
                    "fields": ["name^3", "formatted_address"]
                }
            },
            "size": size,
            "from": from_
        }

        return es_core.search(self.place_index_name, query)

    def search_places_by_location(self, lat: float, lng: float, distance: str = "1km",
                                 size: int = 10, from_: int = 0) -> Dict[str, Any]:
        """
        根据地理位置搜索地点

        Args:
            lat: 纬度
            lng: 经度
            distance: 搜索半径
            size: 返回结果数量
            from_: 分页起始位置

        Returns:
            搜索结果
        """
        query = {
            "query": {
                "geo_distance": {
                    "distance": distance,
                    "location": {
                        "lat": lat,
                        "lon": lng
                    }
                }
            },
            "sort": [
                {
                    "_geo_distance": {
                        "location": {
                            "lat": lat,
                            "lon": lng
                        },
                        "order": "asc",
                        "unit": "km"
                    }
                }
            ],
            "size": size,
            "from": from_
        }

        return es_core.search(self.place_index_name, query)

    def delete_place(self, place_id: str) -> Dict[str, Any]:
        """
        删除地点

        Args:
            place_id: 地点ID

        Returns:
            Elasticsearch的响应
        """
        return es_core.delete_item(self.place_index_name, place_id)

    def delete_all_places(self) -> Dict[str, Any]:
        """
        删除索引中的所有地点数据

        Returns:
            包含操作结果的字典
        """
        return es_core.delete_all(self.place_index_name)

    def export_places_to_json(self, json_file_path: str, query: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        将地点数据导出到JSON文件，确保与原始Google Places API格式完全一致

        Args:
            json_file_path: 导出的JSON文件路径
            query: 可选的查询参数，用于筛选导出的数据

        Returns:
            包含导出状态信息的字典
        """
        import json
        import time

        # 默认查询所有文档
        if query is None:
            query = {"query": {"match_all": {}}}

        scroll = '2m'
        size = 1000

        # 初始化scroll
        scroll_id = None
        total_docs = 0
        start_time = time.time()

        try:
            # 获取初始结果和scroll_id
            result = es_core.es.search(
                index=self.place_index_name,
                body=query,
                scroll=scroll,
                size=size
            )

            scroll_id = result.get('_scroll_id')
            hits = result.get('hits', {}).get('hits', [])

            # 准备要导出的文档
            export_list = []

            # 处理所有结果
            all_hits = hits.copy()

            # 如果还有更多文档，继续获取
            while len(hits) > 0:
                result = es_core.es.scroll(
                    scroll_id=scroll_id,
                    scroll=scroll
                )

                scroll_id = result.get('_scroll_id')
                hits = result.get('hits', {}).get('hits', [])
                all_hits.extend(hits)

            # 处理所有文档
            for hit in all_hits:
                # 获取原始文档
                place = hit.get('_source', {})

                # 创建一个新的字典，包含所有原始字段
                export_data = {}

                # 添加基本字段
                if "status" in place:
                    export_data["status"] = place["status"]
                else:
                    export_data["status"] = "OK"  # 默认状态

                # 添加query字段（如果有）
                if "query" in place:
                    export_data["query"] = place["query"]

                # ES自己添加的字段，需要排除
                exclude_fields = ["_id", "_index", "_score", "_type"]

                # 复制所有其他字段
                for field, value in place.items():
                    if field not in exclude_fields and field != "location":  # 排除location字段，因为我们已经处理了geometry
                        export_data[field] = value

                # 处理嵌套字段 - geometry
                if "geometry" in place:
                    export_data["geometry"] = place["geometry"]
                elif "location" in place:
                    # 如果有location字段但没有geometry，从location重构geometry
                    export_data["geometry"] = {
                        "location": {
                            "lat": place["location"]["lat"],
                            "lng": place["location"]["lon"]
                        }
                    }

                export_list.append(export_data)
                total_docs += 1

            # 写入JSON文件
            with open(json_file_path, 'w', encoding='utf-8') as f:
                # 如果只有一个文档且需要单独导出
                if len(export_list) == 1 and query.get("query", {}).get("term", {}).get("place_id"):
                    # 单文档模式 - 直接导出为对象
                    json_str = json.dumps(export_list[0], ensure_ascii=False, indent=4)
                    f.write(json_str)
                else:
                    # 多文档模式 - 导出为数组
                    json_str = json.dumps(export_list, ensure_ascii=False, indent=4)
                    f.write(json_str)

            elapsed_time = time.time() - start_time

            return {
                "status": "success",
                "message": f"成功导出 {total_docs} 个文档到 {json_file_path}",
                "total_docs": total_docs,
                "elapsed_time": elapsed_time,
                "file_path": json_file_path
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"导出数据失败: {str(e)}",
                "error": str(e)
            }
        finally:
            # 清理scroll上下文
            if scroll_id:
                try:
                    es_core.es.clear_scroll(scroll_id=scroll_id)
                except:
                    pass

    def search_places_mixed(self, lat: float = None, lng: float = None, distance: str = "1km",
                            placeType: str = None, name: str = None,
                            size: int = 10, from_: int = 0) -> Dict[str, Any]:
        """
        混合查询地点，支持可选组合条件

        Args:
            lat: 可选，纬度
            lng: 可选，经度
            distance: 搜索半径，默认1km
            placeType: 可选，来源关键词
            name: 可选，地点名称关键词
            size: 返回结果数量
            from_: 分页起始位置

        Returns:
            搜索结果
        """
        # 创建bool查询
        bool_query = {
            "bool": {
                "must": []
            }
        }

        # 添加地理位置条件（如果提供）
        if lat is not None and lng is not None:
            geo_query = {
                "geo_distance": {
                    "distance": distance,
                    "location": {
                        "lat": lat,
                        "lon": lng
                    }
                }
            }
            bool_query["bool"]["must"].append(geo_query)

        if placeType is not None:
            keyword_query = {
                "term": {
                    "place_type": placeType                }
            }
            bool_query["bool"]["must"].append(keyword_query)

        # 添加名称搜索条件（如果提供）
        if name is not None:
            name_query = {
                "multi_match": {
                    "query": name,
                    "fields": ["name^3", "formatted_address"]
                }
            }
            bool_query["bool"]["must"].append(name_query)

        # 如果没有任何条件，则搜索所有
        if not bool_query["bool"]["must"]:
            query = {
                "query": {
                    "match_all": {}
                },
                "size": size,
                "from": from_
            }
        else:
            query = {
                "query": bool_query,
                "size": size,
                "from": from_
            }

        # 如果有地理位置条件，添加距离排序
        if lat is not None and lng is not None:
            query["sort"] = [
                {
                    "_geo_distance": {
                        "location": {
                            "lat": lat,
                            "lon": lng
                        },
                        "order": "asc",
                        "unit": "km"
                    }
                }
            ]

        result = es_core.search(self.place_index_name, query)

        return result
# 创建单例实例
place_service = PlaceService()