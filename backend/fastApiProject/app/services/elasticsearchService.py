from elasticsearch import Elasticsearch, exceptions
from elasticsearch.helpers import bulk
import json
import logging
from typing import List, Dict, Any, Optional, Union
from ..config import get_settings
import datetime

settings = get_settings()


class ElasticsearchService:
    """ElasticsearchService 处理所有与 Elasticsearch 相关的操作，包括地理查询、关键词查询以及数据导入"""

    def __init__(self):
        """初始化 Elasticsearch 客户端连接"""
        self.es = Elasticsearch(settings.ELASTICSEARCH_URL)
        self.index_name = f"{settings.ELASTICSEARCH_INDEX_PREFIX}posts"
        self.logger = logging.getLogger(__name__)

        # 确保索引存在
        self._create_index_if_not_exists()

    def _create_index_if_not_exists(self) -> None:
        """如果索引不存在则创建索引，设置好映射关系"""
        try:
            if not self.es.indices.exists(index=self.index_name):
                # 创建索引并设置映射
                mappings = {
                    "mappings": {
                        "properties": {
                            "note_id": {"type": "keyword","index":"true"},
                            "type": {"type": "keyword"},
                            "title": {"type": "text", "analyzer": "ik_max_word", "search_analyzer": "ik_smart"},
                            "desc": {"type": "text", "analyzer": "ik_max_word", "search_analyzer": "ik_smart"},
                            "video_url": {"type": "keyword"},
                            "time": {"type": "date"},
                            "last_update_time": {"type": "date"},
                            "user_id": {"type": "keyword"},
                            "nickname": {"type": "keyword"},
                            "avatar": {"type": "keyword"},
                            "liked_count": {"type": "keyword"},
                            "collected_count": {"type": "keyword"},
                            "comment_count": {"type": "keyword"},
                            "share_count": {"type": "keyword"},
                            "ip_location": {"type": "keyword"},
                            "image_list": {"type": "text"},
                            "tag_list": {"type": "text", "analyzer": "ik_max_word", "search_analyzer": "ik_smart"},
                            "last_modify_ts": {"type": "date"},
                            "note_url": {"type": "keyword"},
                            "source_keyword": {"type": "keyword"},
                            "xsec_token": {"type": "keyword"},
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
                            "score": {"type": "integer"}
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
                self.es.indices.create(index=self.index_name, body=mappings)
                self.logger.info(f"索引 {self.index_name} 已创建")
        except exceptions.TransportError as e:
            self.logger.error(f"创建索引时出错: {e}")
            raise

    def import_posts_from_json(self, json_file_path: str) -> Dict[str, Any]:
        """
        从JSON文件导入帖子数据

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
                    "_index": self.index_name,
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
        添加单个帖子到Elasticsearch

        Args:
            post: 包含帖子数据的字典

        Returns:
            Elasticsearch的响应
        """
        try:
            # 处理位置信息
            if "locations" in post and post["locations"]:
                for location in post["locations"]:
                    if "lat" in location and "lng" in location:
                        location["location"] = {
                            "lat": location["lat"],
                            "lon": location["lng"]
                        }

            # 确保note_id存在
            if "note_id" not in post:
                post["note_id"] = f"generated_{datetime.datetime.now().timestamp()}"

            # 添加帖子
            response = self.es.index(
                index=self.index_name,
                id=post["note_id"],
                body=post
            )
            return response

        except Exception as e:
            self.logger.error(f"添加帖子时出错: {e}")
            raise

    def search_by_keyword(self, keyword: str, size: int = 10, from_: int = 0) -> Dict[str, Any]:
        """
        根据关键词搜索帖子

        Args:
            keyword: 搜索关键词
            size: 返回结果数量
            from_: 分页起始位置

        Returns:
            搜索结果
        """
        try:
            query = {
                "query": {
                    "multi_match": {
                        "query": keyword,
                        "fields": ["title^3", "desc^2", "tag_list", "source_keyword"]
                    }
                },
                "size": size,
                "from": from_
            }

            response = self.es.search(index=self.index_name, body=query)
            return self._format_search_results(response)

        except Exception as e:
            self.logger.error(f"关键词搜索时出错: {e}")
            raise

    def search_by_location(self, lat: float, lng: float, distance: str = "10km",
                           size: int = 10, from_: int = 0) -> Dict[str, Any]:
        """
        根据地理位置搜索帖子

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
                },
                "size": size,
                "from": from_
            }

            response = self.es.search(index=self.index_name, body=query)
            return self._format_search_results(response)

        except Exception as e:
            self.logger.error(f"地理位置搜索时出错: {e}")
            raise

    def combined_search(self, keyword: Optional[str] = None,
                        lat: Optional[float] = None, lng: Optional[float] = None,
                        distance: str = "10km", size: int = 10, from_: int = 0) -> Dict[str, Any]:
        """
        组合搜索：关键词 + 地理位置

        Args:
            keyword: 搜索关键词
            lat: 纬度
            lng: 经度
            distance: 搜索半径
            size: 返回结果数量
            from_: 分页起始位置

        Returns:
            搜索结果
        """
        try:
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

            # 如果没有搜索条件，返回所有结果
            if not must_queries:
                query = {
                    "query": {"match_all": {}},
                    "size": size,
                    "from": from_
                }
            else:
                query = {
                    "query": {
                        "bool": {
                            "must": must_queries
                        }
                    },
                    "size": size,
                    "from": from_
                }

            response = self.es.search(index=self.index_name, body=query)
            return self._format_search_results(response)

        except Exception as e:
            self.logger.error(f"组合搜索时出错: {e}")
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

    def get_post_by_id(self, note_id: str) -> Optional[Dict[str, Any]]:
        """
        根据ID获取单个帖子

        Args:
            note_id: 帖子ID

        Returns:
            帖子数据或None（如果不存在）
        """
        try:
            response = self.es.get(index=self.index_name, id=note_id)
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
            response = self.es.delete(index=self.index_name, id=note_id)
            return response
        except Exception as e:
            self.logger.error(f"删除帖子时出错: {e}")
            raise

# 创建单例实例
es_service = ElasticsearchService()