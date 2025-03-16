import requests
import json
import logging
from typing import Dict

logger = logging.getLogger(__name__)


class WikipediaFinder:
    """
    维基百科查询工具
    用于根据地点名称查询维基百科的英文简介
    """

    def __init__(self):
        """
        初始化维基百科查询工具
        """
        self.api_url = "https://en.wikipedia.org/w/api.php"

    def get_place_description(self, place_name: str) -> Dict:
        """
        根据地点名称查询维基百科的英文简介

        Args:
            place_name: 地点名称或关键词

        Returns:
            包含地点简介的字典
        """
        # 初始化结果
        result = {
            "status": "ERROR",
            "query": place_name,
            "title": None,
            "description": None,
            "url": None
        }

        try:
            # 步骤1: 搜索维基百科文章
            search_params = {
                "action": "query",
                "list": "search",
                "srsearch": place_name,
                "format": "json",
                "srlimit": 1,  # 只获取最匹配的结果
                "origin": "*"
            }

            search_response = requests.get(self.api_url, params=search_params, timeout=30)
            search_response.raise_for_status()
            search_data = search_response.json()

            # 检查是否找到结果
            if not search_data.get("query", {}).get("search", []):
                result["error_message"] = f"未找到相关维基百科条目: {place_name}"
                return result

            # 获取文章标题
            page_title = search_data["query"]["search"][0]["title"]
            result["title"] = page_title

            # 步骤2: 获取文章摘要
            extract_params = {
                "action": "query",
                "prop": "extracts|info",
                "exintro": True,
                "explaintext": True,  # 获取纯文本
                "inprop": "url",
                "titles": page_title,
                "format": "json",
                "origin": "*"
            }

            extract_response = requests.get(self.api_url, params=extract_params, timeout=30)
            extract_response.raise_for_status()
            extract_data = extract_response.json()

            # 从响应中提取页面ID和内容
            pages = extract_data["query"]["pages"]
            page_id = next(iter(pages))

            if page_id == "-1":
                result["error_message"] = f"无法获取维基百科页面内容: {page_title}"
                return result

            page_data = pages[page_id]

            # 提取描述文本
            if "extract" in page_data:
                extract = page_data["extract"]

                # 获取第一段作为简介
                paragraphs = extract.split("\n")
                description = paragraphs[0].strip() if paragraphs else ""

                # 如果第一段太短，尝试合并前几段
                if len(description) < 100 and len(paragraphs) > 1:
                    description = "\n\n".join([p for p in paragraphs[:3] if p.strip()])

                result["description"] = description

            # 获取页面URL
            if "fullurl" in page_data:
                result["url"] = page_data["fullurl"]

            # 设置状态为成功
            result["status"] = "OK"
            return result

        except Exception as e:
            logger.error(f"获取维基百科描述出错: {e}")
            result["error_message"] = str(e)
            return result


# 创建全局维基百科查询工具实例
wikipedia_finder = WikipediaFinder()


"""def main():
    # 测试获取Space Needle的描述
    place_name = "Space Needle, Seattle"
    print(f"\n获取维基百科描述 ({place_name}):")

    description = wikipedia_finder.get_place_description(place_name)
    if description["status"] == "OK":
        print(f"\n标题: {description['title']}")
        print(f"\n简介: {description['description']}")
        print(f"\n链接: {description['url']}")
    else:
        print(f"\n获取失败: {description.get('error_message')}")


if __name__ == "__main__":
    main()"""