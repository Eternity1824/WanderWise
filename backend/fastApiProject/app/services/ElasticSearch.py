from elasticsearch import Elasticsearch, exceptions
from elasticsearch.helpers import bulk
import json
import logging
from typing import List, Dict, Any, Optional, Union
from config import get_settings
import datetime

settings = get_settings()


class ElasticsearchService:
    """ElasticsearchService 处理所有与 Elasticsearch 相关的操作，包括地理查询、关键词查询以及数据导入"""

    def __init__(self):
        """初始化 Elasticsearch 客户端连接"""
        self.es = Elasticsearch(settings.ELASTICSEARCH_URL)
        self.post_index_name = f"{settings.ELASTICSEARCH_INDEX_PREFIX}posts"
        self.place_index_name = f"{settings.ELASTICSEARCH_INDEX_PREFIX}places"
        self.logger = logging.getLogger(__name__)

        # 确保索引存在
        self._create_post_index_if_not_exists()
        self._create_place_index_if_not_exists()

    def _create_post_index_if_not_exists(self) -> None:
        """如果帖子索引不存在则创建索引，设置好映射关系"""
        try:
            if not self.es.indices.exists(index=self.post_index_name):
                # 创建索引并设置映射
                mappings = {
                    "mappings": {
                        "properties": {
                            "note_id": {"type": "keyword","index":"true"},
                            "title": {"type": "text", "analyzer": "ik_max_word", "search_analyzer": "ik_smart"},
                            "desc": {"type": "text", "analyzer": "ik_max_word", "search_analyzer": "ik_smart"},
                            "user_id": {"type": "keyword"},
                            "nickname": {"type": "keyword"},
                            "tag_list": {"type": "text", "analyzer": "ik_max_word", "search_analyzer": "ik_smart"},
                            "source_keyword": {"type": "keyword"},
                            "locations": {
                                "type": "nested",
                                "properties": {
                                    "formatted_address": {"type": "text"},
                                    "lat": {"type": "float"},
                                    "lng": {"type": "float"},
                                    "place_id": {"type": "keyword"},
                                    "location_type": {"type": "keyword"},
                                    "location": {"type": "geo_point"}
                                }
                            },
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
                self.es.indices.create(index=self.post_index_name, body=mappings)
                self.logger.info(f"索引 {self.post_index_name} 已创建")
        except exceptions.TransportError as e:
            self.logger.error(f"创建帖子索引时出错: {e}")
            raise

    def _create_place_index_if_not_exists(self) -> None:
        """如果地点索引不存在则创建索引，设置好映射关系"""
        try:
            if not self.es.indices.exists(index=self.place_index_name):
                # 创建索引并设置映射
                mappings = {
                    "mappings": {
                        "properties": {
                            "place_id": {"type": "keyword", "index": "true"},
                            "name": {"type": "text", "analyzer": "ik_max_word", "search_analyzer": "ik_smart"},
                            "location": {"type": "geo_point"}
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
                self.es.indices.create(index=self.place_index_name, body=mappings)
                self.logger.info(f"索引 {self.place_index_name} 已创建")
        except exceptions.TransportError as e:
            self.logger.error(f"创建地点索引时出错: {e}")
            raise

    # 帖子相关方法 - 保持原有实现不变
    def import_posts_from_json(self, json_file_path: str) -> Dict[str, Any]:
        """
        从JSON文件导入帖子数据，排除image_list字段

        Args:
            json_file_path: JSON文件路径

        Returns:
            包含导入状态信息的字典
        """
        try:
            with open(json_file_path, 'r', encoding='utf-8') as f:
                posts = json.load(f)

            if not isinstance(posts, list):
                posts = [posts]

            # 预处理数据并准备批量导入
            actions = []
            for post in posts:
                # 移除image_list字段
                if "image_list" in post:
                    del post["image_list"]

                # 处理位置信息，添加geo_point字段
                if "locations" in post and post["locations"]:
                    for location in post["locations"]:
                        if "lat" in location and "lng" in location:
                            location["location"] = {
                                "lat": location["lat"],
                                "lon": location["lng"]
                            }

                # 格式化时间戳
                for time_field in ["time", "last_update_time", "last_modify_ts"]:
                    if time_field in post and post[time_field]:
                        # 确保时间戳是整数
                        post[time_field] = int(post[time_field])

                action = {
                    "_index": self.post_index_name,
                    "_id": post["note_id"],
                    "_source": post
                }
                actions.append(action)

            # 执行批量导入
            if actions:
                success, failed = bulk(self.es, actions, stats_only=True)
                return {
                    "success": success,
                    "failed": failed,
                    "total": len(actions)
                }
            return {"success": 0, "failed": 0, "total": 0}

        except Exception as e:
            self.logger.error(f"导入JSON数据时出错: {e}")
            raise

    def add_post(self, post: Dict[str, Any]) -> Dict[str, Any]:
        """
        添加单个帖子到Elasticsearch，排除image_list字段

        Args:
            post: 包含帖子数据的字典

        Returns:
            Elasticsearch的响应
        """
        try:
            # 创建数据副本，避免修改原始数据
            post_data = post.copy()

            # 移除image_list字段
            if "image_list" in post_data:
                del post_data["image_list"]

            # 处理位置信息
            if "locations" in post_data and post_data["locations"]:
                for location in post_data["locations"]:
                    if "lat" in location and "lng" in location:
                        location["location"] = {
                            "lat": location["lat"],
                            "lon": location["lng"]
                        }

            # 确保note_id存在
            if "note_id" not in post_data:
                post_data["note_id"] = f"generated_{datetime.datetime.now().timestamp()}"

            # 添加帖子
            response = self.es.index(
                index=self.post_index_name,
                id=post_data["note_id"],
                body=post_data
            )
            return response

        except Exception as e:
            self.logger.error(f"添加帖子时出错: {e}")
            raise

    def search_by_keyword(self, keyword: str, size: int = 10, from_: int = 0,
                          score_weight: float = 0.5) -> Dict[str, Any]:
        """
        根据关键词搜索帖子

        Args:
            keyword: 搜索关键词
            size: 返回结果数量
            from_: 分页起始位置
            score_weight: 自定义分数权重

        Returns:
            搜索结果
        """
        try:
            # 构建关键词查询
            base_query = {
                "multi_match": {
                    "query": keyword,
                    "fields": ["title^3", "desc^2", "tag_list", "source_keyword"]
                }
            }

            # 是否需要考虑score字段
            if score_weight <= 0:
                query = {
                    "query": base_query,
                    "size": size,
                    "from": from_
                }
            else:
                # 使用function_score来结合自定义分数
                query = {
                    "query": {
                        "function_score": {
                            "query": base_query,
                            "functions": [
                                {
                                    "field_value_factor": {
                                        "field": "score",
                                        "factor": score_weight,
                                        "modifier": "log1p",
                                        "missing": 0
                                    }
                                }
                            ],
                            "boost_mode": "multiply"
                        }
                    },
                    "size": size,
                    "from": from_
                }

            response = self.es.search(index=self.post_index_name, body=query)
            return self._format_search_results(response)
        except Exception as e:
            self.logger.error(f"关键词搜索时出错: {e}")
            raise

    def search_by_location(self, lat: float, lng: float, distance: str = "1km",
                           size: int = 10, from_: int = 0,
                           score_weight: float = 0.5) -> Dict[str, Any]:
        """
        根据地理位置搜索帖子

        Args:
            lat: 纬度
            lng: 经度
            distance: 搜索半径
            size: 返回结果数量
            from_: 分页起始位置
            score_weight: 自定义分数权重

        Returns:
            搜索结果
        """
        try:
            # 构建地理位置查询
            geo_query = {
                "nested": {
                    "path": "locations",
                    "query": {
                        "geo_distance": {
                            "distance": distance,
                            "locations.location": {
                                "lat": lat,
                                "lon": lng
                            }
                        }
                    }
                }
            }

            # 是否需要考虑score字段
            if score_weight <= 0:
                query = {
                    "query": geo_query,
                    "size": size,
                    "from": from_
                }
            else:
                # 使用function_score来结合自定义分数
                query = {
                    "query": {
                        "function_score": {
                            "query": geo_query,
                            "functions": [
                                {
                                    "field_value_factor": {
                                        "field": "score",
                                        "factor": score_weight,
                                        "modifier": "log1p",
                                        "missing": 0
                                    }
                                }
                            ],
                            "boost_mode": "multiply"
                        }
                    },
                    "size": size,
                    "from": from_
                }

            response = self.es.search(index=self.post_index_name, body=query)
            return self._format_search_results(response)
        except Exception as e:
            self.logger.error(f"地理位置搜索时出错: {e}")
            raise

    def combined_search(self, keyword: Optional[str] = None,
                        lat: Optional[float] = None, lng: Optional[float] = None,
                        distance: str = "1km", size: int = 10, from_: int = 0,
                        score_weight: float = 0.5) -> Dict[str, Any]:
        """
        组合搜索：关键词 + 地理位置 + 自定义分数权重

        Args:
            keyword: 搜索关键词
            lat: 纬度
            lng: 经度
            distance: 搜索半径
            size: 返回结果数量
            from_: 分页起始位置
            score_weight: 自定义分数权重

        Returns:
            搜索结果
        """
        try:
            # 基本查询条件
            must_queries = []
            # 添加关键词搜索
            if keyword:
                must_queries.append({
                    "multi_match": {
                        "query": keyword,
                        "fields": ["title^3", "desc^2", "tag_list", "source_keyword"]
                    }
                })

            # 添加地理位置搜索
            if lat is not None and lng is not None:
                must_queries.append({
                    "nested": {
                        "path": "locations",
                        "query": {
                            "geo_distance": {
                                "distance": distance,
                                "locations.location": {
                                    "lat": lat,
                                    "lon": lng
                                }
                            }
                        }
                    }
                })

            # 基本查询
            base_query = {
                "bool": {
                    "must": must_queries if must_queries else [{"match_all": {}}]
                }
            }

            # 如果不需要考虑score字段，使用基本查询
            if score_weight <= 0:
                query = {
                    "query": base_query,
                    "size": size,
                    "from": from_
                }
            else:
                # 使用function_score来结合自定义分数
                query = {
                    "query": {
                        "function_score": {
                            "query": base_query,
                            "functions": [
                                {
                                    "field_value_factor": {
                                        "field": "score",
                                        "factor": score_weight,
                                        "modifier": "log1p",  # 使用log(1+x)来避免0分的问题
                                        "missing": 0  # 如果字段不存在，默认值为0
                                    }
                                }
                            ],
                            "boost_mode": "multiply"  # 将函数得分与查询得分相乘
                        }
                    },
                    "size": size,
                    "from": from_
                }

            response = self.es.search(index=self.post_index_name, body=query)
            return self._format_search_results(response)

        except Exception as e:
            self.logger.error(f"组合搜索时出错: {e}")
            raise

    def get_post_by_id(self, note_id: str) -> Optional[Dict[str, Any]]:
        """
        根据ID获取单个帖子

        Args:
            note_id: 帖子ID

        Returns:
            帖子数据或None（如果不存在）
        """
        try:
            response = self.es.get(index=self.post_index_name, id=note_id)
            return response.get("_source")
        except exceptions.NotFoundError:
            return None
        except Exception as e:
            self.logger.error(f"获取帖子时出错: {e}")
            raise

    def delete_post(self, note_id: str) -> Dict[str, Any]:
        """
        删除帖子

        Args:
            note_id: 帖子ID

        Returns:
            Elasticsearch的响应
        """
        try:
            response = self.es.delete(index=self.post_index_name, id=note_id)
            return response
        except Exception as e:
            self.logger.error(f"删除帖子时出错: {e}")
            raise

    def delete_all_posts(self) -> Dict[str, Any]:
        """
        删除索引中的所有帖子数据

        Returns:
            包含操作结果的字典
        """
        try:
            # 使用delete_by_query删除所有文档
            response = self.es.delete_by_query(
                index=self.post_index_name,
                body={
                    "query": {
                        "match_all": {}
                    }
                },
                refresh=True  # 确保操作立即可见
            )

            self.logger.info(f"已删除索引 {self.post_index_name} 中的所有文档")
            return {
                "success": True,
                "deleted": response.get("deleted", 0),
                "total": response.get("total", 0),
                "failures": response.get("failures", [])
            }
        except exceptions.TransportError as e:
            self.logger.error(f"删除所有帖子时出错: {e}")
            return {
                "success": False,
                "error": str(e)
            }
        except Exception as e:
            self.logger.error(f"删除所有帖子时出错: {e}")
            raise

    def add_place(self, place: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        添加单个地点到Elasticsearch，如果已存在相同ID则跳过

        Args:
            place: 包含地点数据的字典（Google Places API返回的格式）

        Returns:
            Elasticsearch的响应，或None（如果地点已存在）
        """
        try:
            # 创建数据副本，避免修改原始数据
            place_data = place.copy()

            # 确保place_id存在
            if "place_id" not in place_data:
                self.logger.error("地点数据缺少place_id字段")
                raise ValueError("地点数据必须包含place_id字段")

            # 检查ID是否已存在
            place_id = place_data["place_id"]
            if self.es.exists(index=self.place_index_name, id=place_id):
                self.logger.info(f"地点ID {place_id} 已存在，跳过添加")
                return None

            # 添加geo_point格式的位置数据
            if "geometry" in place_data and "location" in place_data["geometry"]:
                place_data["location"] = {
                    "lat": place_data["geometry"]["location"]["lat"],
                    "lon": place_data["geometry"]["location"]["lng"]
                }

            # 添加地点
            response = self.es.index(
                index=self.place_index_name,
                id=place_data["place_id"],
                body=place_data
            )
            return response

        except Exception as e:
            self.logger.error(f"添加地点时出错: {e}")
            raise

    def import_places_from_json(self, json_file_path: str) -> Dict[str, Any]:
        """
        从JSON文件导入地点数据

        Args:
            json_file_path: JSON文件路径

        Returns:
            包含导入状态信息的字典
        """
        try:
            with open(json_file_path, 'r', encoding='utf-8') as f:
                places = json.load(f)

            if not isinstance(places, list):
                places = [places]

            # 预处理数据并准备批量导入
            actions = []
            for place in places:
                # 确保place_id存在
                if "place_id" not in place:
                    self.logger.warning(f"跳过缺少place_id的地点数据")
                    continue

                # 添加geo_point格式的位置数据
                if "geometry" in place and "location" in place["geometry"]:
                    place["location"] = {
                        "lat": place["geometry"]["location"]["lat"],
                        "lon": place["geometry"]["location"]["lng"]
                    }

                action = {
                    "_index": self.place_index_name,
                    "_id": place["place_id"],
                    "_source": place
                }
                actions.append(action)

            # 执行批量导入
            if actions:
                success, failed = bulk(self.es, actions, stats_only=True)
                return {
                    "success": success,
                    "failed": failed,
                    "total": len(actions)
                }
            return {"success": 0, "failed": 0, "total": 0}

        except Exception as e:
            self.logger.error(f"导入地点JSON数据时出错: {e}")
            raise

    def get_place_by_id(self, place_id: str) -> Optional[Dict[str, Any]]:
        """
        根据ID获取单个地点

        Args:
            place_id: 地点ID (Google Place ID)

        Returns:
            地点数据或None（如果不存在）
        """
        try:
            response = self.es.get(index=self.place_index_name, id=place_id)
            return response.get("_source")
        except exceptions.NotFoundError:
            return None
        except Exception as e:
            self.logger.error(f"获取地点时出错: {e}")
            raise

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
        try:
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

            response = self.es.search(index=self.place_index_name, body=query)
            return self._format_search_results(response)
        except Exception as e:
            self.logger.error(f"地点名称搜索时出错: {e}")
            raise

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
        try:
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

            response = self.es.search(index=self.place_index_name, body=query)
            return self._format_search_results(response)
        except Exception as e:
            self.logger.error(f"地点地理位置搜索时出错: {e}")
            raise

    def delete_place(self, place_id: str) -> Dict[str, Any]:
        """
        删除地点

        Args:
            place_id: 地点ID

        Returns:
            Elasticsearch的响应
        """
        try:
            response = self.es.delete(index=self.place_index_name, id=place_id)
            return response
        except Exception as e:
            self.logger.error(f"删除地点时出错: {e}")
            raise

    def delete_all_places(self) -> Dict[str, Any]:
        """
        删除索引中的所有地点数据

        Returns:
            包含操作结果的字典
        """
        try:
            # 使用delete_by_query删除所有文档
            response = self.es.delete_by_query(
                index=self.place_index_name,
                body={
                    "query": {
                        "match_all": {}
                    }
                },
                refresh=True  # 确保操作立即可见
            )

            self.logger.info(f"已删除索引 {self.place_index_name} 中的所有文档")
            return {
                "success": True,
                "deleted": response.get("deleted", 0),
                "total": response.get("total", 0),
                "failures": response.get("failures", [])
            }
        except exceptions.TransportError as e:
            self.logger.error(f"删除所有地点时出错: {e}")
            return {
                "success": False,
                "error": str(e)
            }
        except Exception as e:
            self.logger.error(f"删除所有地点时出错: {e}")
            raise

    def _format_search_results(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        格式化搜索结果

        Args:
            response: Elasticsearch 原始响应

        Returns:
            格式化后的搜索结果
        """
        hits = response.get("hits", {})
        total = hits.get("total", {}).get("value", 0)
        max_score = hits.get("max_score")
        results = []

        for hit in hits.get("hits", []):
            result = hit.get("_source", {})
            result["_score"] = hit.get("_score")
            results.append(result)

        return {
            "total": total,
            "max_score": max_score,
            "results": results
        }

# 创建单例实例
es_service = ElasticsearchService()
if __name__ == "__main__":
    print(es_service.get_post_by_id("6420b0080000000011010d6e"))
