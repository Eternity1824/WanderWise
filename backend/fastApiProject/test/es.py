import json
import time
import os
import sys
import logging
import argparse

# 设置日志记录
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 添加项目根目录到 Python 路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../.."))
sys.path.append(project_root)

# 尝试导入 ElasticsearchService
try:
    from backend.fastApiProject.app.services.elasticsearchService import ElasticsearchService, es_service
    logger.info("成功导入 ElasticsearchService")
except ImportError as e:
    logger.error(f"导入 ElasticsearchService 失败: {e}")
    # 如果导入失败，尝试直接创建 ElasticsearchService 实例
    sys.exit(1)

def import_and_test():
    """导入整个 JSON 文件并测试搜索功能"""
    parser = argparse.ArgumentParser(description='导入 JSON 数据到 Elasticsearch 并测试')
    parser.add_argument('--file', default='processed_search_contents_2025-03-11_final.json',
                        help='JSON数据文件路径')
    parser.add_argument('--use-existing', action='store_true',
                        help='使用现有的单例实例而不是创建新实例')
    args = parser.parse_args()

    # 确定文件路径
    file_path = args.file
    if not os.path.isabs(file_path):
        file_path = os.path.join(current_dir, file_path)

    if not os.path.exists(file_path):
        logger.error(f"文件不存在: {file_path}")
        return

    logger.info(f"使用数据文件: {file_path}")

    # 使用单例实例或创建新实例
    if args.use_existing:
        service = es_service
        logger.info("使用现有的 ElasticsearchService 单例实例")
    else:
        service = ElasticsearchService()
        logger.info("创建了新的 ElasticsearchService 实例")

    # 开始导入
    try:
        logger.info("开始导入数据...")
        result = service.import_posts_from_json(file_path)
        logger.info(f"导入结果: 成功 {result['success']}, 失败 {result['failed']}, 总计 {result['total']}")

        # 刷新索引以确保数据可搜索
        service.es.indices.refresh(index=service.index_name)
        logger.info(f"索引 {service.index_name} 已刷新")

        # 等待一会儿确保索引完成
        time.sleep(2)

        # 加载数据进行测试
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 如果数据是列表，获取第一条数据的位置进行测试
        if isinstance(data, list) and len(data) > 0:
            first_item = data[0]
            if "locations" in first_item and first_item["locations"]:
                first_location = first_item["locations"][0]
                lat, lng = first_location["lat"], first_location["lng"]
                test_location_search(service, lat, lng)

            # 测试关键词搜索
            if "title" in first_item and first_item["title"]:
                # 从标题中提取一个关键词
                keywords = first_item["title"].split()
                if keywords:
                    test_keyword_search(service, keywords[0])

            # 测试组合查询
            if "locations" in first_item and first_item["locations"] and "title" in first_item and first_item["title"]:
                first_location = first_item["locations"][0]
                lat, lng = first_location["lat"], first_location["lng"]
                keyword = first_item["title"].split()[0] if first_item["title"].split() else "美食"
                test_combined_search(service, keyword, lat, lng)

    except Exception as e:
        logger.error(f"导入或测试过程中出错: {e}", exc_info=True)

def test_location_search(service, lat, lng):
    """测试地理位置搜索"""
    logger.info(f"测试地理位置搜索: ({lat}, {lng})")
    try:
        result = service.search_by_location(lat, lng, distance="5km", size=5)
        logger.info(f"地理位置搜索结果: 找到 {result['total']} 条记录")
        if result['total'] > 0:
            logger.info(f"首条结果: {result['results'][0]}")
    except Exception as e:
        logger.error(f"地理位置搜索测试失败: {e}")

def test_keyword_search(service, keyword):
    """测试关键词搜索"""
    logger.info(f"测试关键词搜索: '{keyword}'")
    try:
        result = service.search_by_keyword(keyword, size=5)
        logger.info(f"关键词搜索结果: 找到 {result['total']} 条记录")
        if result['total'] > 0:
            logger.info(f"首条结果: {result['results'][0].get('title')}")
    except Exception as e:
        logger.error(f"关键词搜索测试失败: {e}")

def test_combined_search(service, keyword, lat, lng):
    """测试组合搜索"""
    logger.info(f"测试组合搜索: 关键词 '{keyword}', 位置 ({lat}, {lng})")
    try:
        result = service.combined_search(keyword=keyword, lat=lat, lng=lng, distance="5km", size=5)
        logger.info(f"组合搜索结果: 找到 {result['total']} 条记录")
        if result['total'] > 0:
            logger.info(f"首条结果: {result['results'][0].get('title')}")
    except Exception as e:
        logger.error(f"组合搜索测试失败: {e}")

if __name__ == "__main__":
    import_and_test()