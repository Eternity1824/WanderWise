from elasticsearch import Elasticsearch, exceptions
from elasticsearch.helpers import bulk
import json
import logging
from typing import List, Dict, Any, Optional, Union
from config import get_settings

settings = get_settings()


class ElasticsearchCore:
    """ElasticsearchCore 提供与 Elasticsearch 连接及基础操作的功能"""

    def __init__(self):
        """初始化 Elasticsearch 客户端连接"""
        self.es = Elasticsearch(settings.ELASTICSEARCH_URL)
        self.logger = logging.getLogger(__name__)

    def create_index_if_not_exists(self, index_name: str, mappings: Dict[str, Any]) -> None:
        """如果索引不存在则创建索引，设置好映射关系"""
        try:
            if not self.es.indices.exists(index=index_name):
                # 创建索引并设置映射
                self.es.indices.create(index=index_name, body=mappings)
                self.logger.info(f"索引 {index_name} 已创建")
        except exceptions.TransportError as e:
            self.logger.error(f"创建索引时出错: {e}")
            raise

    def import_from_json(self, json_file_path: str, index_name: str,
                         process_item_func, doc_id_field: str) -> Dict[str, Any]:
        """
        从JSON文件导入数据

        Args:
            json_file_path: JSON文件路径
            index_name: 索引名称
            process_item_func: 处理每个项目的函数
            doc_id_field: 文档ID字段名

        Returns:
            包含导入状态信息的字典
        """
        try:
            with open(json_file_path, 'r', encoding='utf-8') as f:
                items = json.load(f)

            if not isinstance(items, list):
                items = [items]

            # 预处理数据并准备批量导入
            actions = []
            for item in items:
                # 处理数据
                processed_item = process_item_func(item)
                if processed_item:
                    action = {
                        "_index": index_name,
                        "_id": processed_item[doc_id_field],
                        "_source": processed_item
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

    def add_item(self, index_name: str, item: Dict[str, Any],
                 doc_id: str) -> Dict[str, Any]:
        """
        添加单个项目到Elasticsearch

        Args:
            index_name: 索引名称
            item: 项目数据
            doc_id: 文档ID

        Returns:
            Elasticsearch的响应
        """
        try:
            response = self.es.index(
                index=index_name,
                id=doc_id,
                body=item
            )
            return response
        except Exception as e:
            self.logger.error(f"添加项目时出错: {e}")
            raise

    def search(self, index_name: str, query: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行搜索

        Args:
            index_name: 索引名称
            query: 查询条件

        Returns:
            搜索结果
        """
        try:
            response = self.es.search(index=index_name, body=query)
            return self._format_search_results(response)
        except Exception as e:
            self.logger.error(f"搜索时出错: {e}")
            raise

    def get_by_id(self, index_name: str, doc_id: str) -> Optional[Dict[str, Any]]:
        """
        根据ID获取单个项目

        Args:
            index_name: 索引名称
            doc_id: 文档ID

        Returns:
            项目数据或None（如果不存在）
        """
        try:
            response = self.es.get(index=index_name, id=doc_id)
            return response.get("_source")
        except exceptions.NotFoundError:
            return None
        except Exception as e:
            self.logger.error(f"获取项目时出错: {e}")
            raise

    def delete_item(self, index_name: str, doc_id: str) -> Dict[str, Any]:
        """
        删除项目

        Args:
            index_name: 索引名称
            doc_id: 文档ID

        Returns:
            Elasticsearch的响应
        """
        try:
            response = self.es.delete(index=index_name, id=doc_id)
            return response
        except Exception as e:
            self.logger.error(f"删除项目时出错: {e}")
            raise

    def delete_all(self, index_name: str) -> Dict[str, Any]:
        """
        删除索引中的所有数据

        Args:
            index_name: 索引名称

        Returns:
            包含操作结果的字典
        """
        try:
            # 使用delete_by_query删除所有文档
            response = self.es.delete_by_query(
                index=index_name,
                body={
                    "query": {
                        "match_all": {}
                    }
                },
                refresh=True  # 确保操作立即可见
            )

            self.logger.info(f"已删除索引 {index_name} 中的所有文档")
            return {
                "success": True,
                "deleted": response.get("deleted", 0),
                "total": response.get("total", 0),
                "failures": response.get("failures", [])
            }
        except exceptions.TransportError as e:
            self.logger.error(f"删除所有项目时出错: {e}")
            return {
                "success": False,
                "error": str(e)
            }
        except Exception as e:
            self.logger.error(f"删除所有项目时出错: {e}")
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

    def export_to_json(self, index_name: str, json_file_path: str, query: dict = None, scroll: str = '2m',
                       size: int = 1000) -> dict:
        """
        将Elasticsearch索引的数据导出到JSON文件

        Args:
            index_name: 索引名称
            json_file_path: 导出的JSON文件路径
            query: 可选的查询参数，用于筛选导出的数据
            scroll: scroll参数，默认为2分钟
            size: 每批次获取的文档数量

        Returns:
            包含导出状态信息的字典
        """
        import json
        import time

        # 默认查询所有文档
        if query is None:
            query = {"query": {"match_all": {}}}

        # 初始化scroll
        scroll_id = None
        total_docs = 0
        start_time = time.time()

        try:
            # 获取初始结果和scroll_id
            result = self.es.search(
                index=index_name,
                body=query,
                scroll=scroll,
                size=size
            )

            scroll_id = result.get('_scroll_id')
            hits = result.get('hits', {}).get('hits', [])
            total_docs_estimate = result.get('hits', {}).get('total', {})
            if isinstance(total_docs_estimate, dict):
                total_docs_estimate = total_docs_estimate.get('value', 0)

            # 打开文件
            with open(json_file_path, 'w', encoding='utf-8') as f:
                # 写入文件头
                f.write('[\n')

                # 写入第一批结果
                for i, hit in enumerate(hits):
                    doc = hit.get('_source', {})
                    json_str = json.dumps(doc, ensure_ascii=False)

                    # 除了最后一个文档外，所有文档后面都要加逗号
                    if i < len(hits) - 1 or total_docs_estimate > len(hits):
                        f.write(json_str + ',\n')
                    else:
                        f.write(json_str + '\n')

                    total_docs += 1

                # 如果还有更多文档，继续获取
                while len(hits) > 0:
                    result = self.es.scroll(
                        scroll_id=scroll_id,
                        scroll=scroll
                    )

                    scroll_id = result.get('_scroll_id')
                    hits = result.get('hits', {}).get('hits', [])

                    # 写入后续批次结果
                    for i, hit in enumerate(hits):
                        doc = hit.get('_source', {})
                        json_str = json.dumps(doc, ensure_ascii=False)

                        # 除了最后一个文档外，所有文档后面都要加逗号
                        if i < len(hits) - 1 or len(hits) == size:
                            f.write(json_str + ',\n')
                        else:
                            f.write(json_str + '\n')

                        total_docs += 1

                # 写入文件尾
                f.write(']')

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
                    self.es.clear_scroll(scroll_id=scroll_id)
                except:
                    pass

# 创建单例实例
es_core = ElasticsearchCore()