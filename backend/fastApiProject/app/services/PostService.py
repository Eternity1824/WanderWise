import datetime
from typing import Dict, Any, Optional
from core.ElasticsearchCore import es_core
from config import get_settings

settings = get_settings()


class PostService:
    """PostService 处理与帖子相关的所有操作"""

    def __init__(self):
        """初始化 PostService"""
        self.post_index_name = f"{settings.ELASTICSEARCH_INDEX_PREFIX}posts"
        self._create_post_index_if_not_exists()

    def _create_post_index_if_not_exists(self) -> None:
        """如果帖子索引不存在则创建索引，设置好映射关系"""
        mappings = {
            "mappings": {
                "properties": {
                    "note_id": {"type": "keyword", "index": "true"},
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
        es_core.create_index_if_not_exists(self.post_index_name, mappings)

    def _process_post_data(self, post: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理帖子数据，移除image_list字段并添加geo_point字段

        Args:
            post: 原始帖子数据

        Returns:
            处理后的帖子数据
        """
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

        # 格式化时间戳
        for time_field in ["time", "last_update_time", "last_modify_ts"]:
            if time_field in post_data and post_data[time_field]:
                # 确保时间戳是整数
                post_data[time_field] = int(post_data[time_field])

        return post_data

    def import_posts_from_json(self, json_file_path: str) -> Dict[str, Any]:
        """
        从JSON文件导入帖子数据

        Args:
            json_file_path: JSON文件路径

        Returns:
            包含导入状态信息的字典
        """
        return es_core.import_from_json(
            json_file_path=json_file_path,
            index_name=self.post_index_name,
            process_item_func=self._process_post_data,
            doc_id_field="note_id"
        )

    def add_post(self, post: Dict[str, Any]) -> Dict[str, Any]:
        """
        添加单个帖子到Elasticsearch

        Args:
            post: 包含帖子数据的字典

        Returns:
            Elasticsearch的响应
        """
        post_data = self._process_post_data(post)
        return es_core.add_item(
            index_name=self.post_index_name,
            item=post_data,
            doc_id=post_data["note_id"]
        )

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

        return es_core.search(self.post_index_name, query)

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

        return es_core.search(self.post_index_name, query)

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

        return es_core.search(self.post_index_name, query)

    def get_post_by_id(self, note_id: str) -> Optional[Dict[str, Any]]:
        """
        根据ID获取单个帖子

        Args:
            note_id: 帖子ID

        Returns:
            帖子数据或None（如果不存在）
        """
        return es_core.get_by_id(self.post_index_name, note_id)

    def delete_post(self, note_id: str) -> Dict[str, Any]:
        """
        删除帖子

        Args:
            note_id: 帖子ID

        Returns:
            Elasticsearch的响应
        """
        return es_core.delete_item(self.post_index_name, note_id)

    def delete_all_posts(self) -> Dict[str, Any]:
        """
        删除索引中的所有帖子数据

        Returns:
            包含操作结果的字典
        """
        return es_core.delete_all(self.post_index_name)

    def export_posts_to_json(self, json_file_path: str, query: Dict[str, Any] = None) -> Dict[str, Any]:
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
                index=self.post_index_name,
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
                post = hit.get('_source', {})

                # 创建一个新的字典，包含所有原始字段
                export_data = {}

                # 添加query字段（如果有）
                if "query" in post:
                    export_data["query"] = post["query"]

                # ES自己添加的字段，需要排除
                exclude_fields = ["_id", "_index", "_score", "_type"]

                # 复制所有其他字段
                for field, value in post.items():
                    if field not in exclude_fields:  # 排除location字段，因为我们已经处理了geometry
                        export_data[field] = value


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
# 创建单例实例
post_service = PostService()
