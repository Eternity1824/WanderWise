import json
import re
from typing import List, Dict, Any, Optional, Tuple
from openai import OpenAI
from config import get_settings
settings = get_settings()
class DeepSeekAPI:
    """DeepSeek API 服务封装"""

    def __init__(self, api_key: str):
        """初始化 DeepSeek 客户端

        Args:
            api_key: DeepSeek API密钥
        """
        self.client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
        self.model = "deepseek-chat"

    def extract_locations(self, post: Dict[str, Any]) -> List[str]:
        """从帖子中提取可能的地理位置

        Args:
            post: 包含标题、描述、标签等信息的帖子数据

        Returns:
            提取的地点列表，格式为 ["地点名, 城市", ...]
        """
        prompt = f"""
        请从以下小红书帖子中提取所有可能的地理位置（精确到餐馆名或者景点名）（餐厅、景点等名称和地址）。
        重要: 提取的每个地点名称必须包含来源关键词中的城市名称作为后缀，例如"洞庭春, Seattle"而不是仅"洞庭春"。
        仅返回JSON格式的地点列表，不要有任何其他文字。如果没有找到就返回空的列表即可。
        格式: ["洞庭春, Seattle", ...]

        帖子标题: {post.get('title', '')}
        帖子内容: {post.get('desc', '')}
        标签: {post.get('tag_list', '')}
        来源关键词: {post.get('source_keyword', '')}
        """

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个专业的地理位置提取助手，只输出JSON格式结果"},
                    {"role": "user", "content": prompt},
                ],
                stream=False
            )

            locations_text = response.choices[0].message.content

            # 尝试解析返回的JSON
            try:
                # 查找方括号内的JSON数组
                json_match = re.search(r'\[.*\]', locations_text, re.DOTALL)
                if json_match:
                    locations_json = json.loads(json_match.group(0))
                    return locations_json
                else:
                    print(f"无法在结果中找到JSON: {locations_text}")
                    return []
            except json.JSONDecodeError:
                print(f"JSON解析失败: {locations_text}")
                return []

        except Exception as e:
            print(f"DeepSeek API调用失败: {str(e)}")
            return []

    def rate_post(self, post: Dict[str, Any], locations: List[Dict[str, Any]]) -> Dict[str, int]:
        """对帖子进行打分

        Args:
            post: 帖子数据
            locations: 地点数据列表，包含坐标和地址

        Returns:
            评分结果，格式为 {"score": 分数}
        """
        # 处理locations信息，避免格式化错误
        locations_addresses = []
        locations_coords = []

        for loc in locations:
            try:
                locations_addresses.append(str(loc.get('formatted_address', '')))
                locations_coords.append(f"{loc.get('lat', '')}, {loc.get('lng', '')}")
            except (KeyError, TypeError) as e:
                print(f"处理location信息时出错: {e}, location: {loc}")

        # 准备评分提示
        prompt = f"""
        请对这篇美食或旅游点评进行打分（满分100分），评分标准如下：
        1. 内容质量（30分）：描述详细程度、是否有实用信息
        2. 真实性（20分）：是否有实际体验的描述细节
        3. 有用程度（20分）：对其他用户的参考价值
        4. 受欢迎度（30分）：根据用户互动数据评估

        点评信息：
        标题: {post.get('title', '')}
        内容: {post.get('desc', '')}
        地点: {', '.join(locations_addresses)}
        坐标: {', '.join(locations_coords)}

        用户互动数据：
        点赞数: {post.get('liked_count', '0')}
        收藏数: {post.get('collected_count', '0')}
        评论数: {post.get('comment_count', '0')}
        分享数: {post.get('share_count', '0')}

        格式为JSON:
        {{"score": 分数}}
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个专业的美食和旅游内容评分助手，只输出JSON格式结果"},
                    {"role": "user", "content": prompt},
                ],
                stream=False
            )

            score_result = response.choices[0].message.content

            # 尝试解析返回的JSON
            try:
                # 查找花括号内的JSON对象
                json_match = re.search(r'\{.*\}', score_result, re.DOTALL)
                if json_match:
                    score_json = json.loads(json_match.group(0))
                    return score_json
                else:
                    return {"score": 70}
            except json.JSONDecodeError:
                return {"score": 70}

        except Exception as e:
            print(f"评分API调用失败: {str(e)}")
            return {"score": 60}

    def process_user_query(self, query: str) -> Tuple[List[str], List[str]]:
        """处理用户提问，提取潜在地点和关键词

        Args:
            query: 用户的提问或搜索内容

        Returns:
            包含两个列表的元组: (地点列表, 关键词列表)
        """
        prompt = f"""
        请分析以下用户查询，提取两类信息：
        1. 可能的地理位置或旅游目的地
        2. 关键词（如美食、景点、购物、历史等主题）

        用户查询: {query}

        以JSON格式返回结果，格式如下:
        {{
            "locations": ["地点1", "地点2", ...],
            "keywords": ["关键词1", "关键词2", ...]
        }}

        只返回JSON结果，不要有其他文字。如果某类信息未找到，则返回空列表。如果分析不出来对应结果, 两个列表都可以为空。
        """

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个专业的旅游查询分析助手，只输出JSON格式结果"},
                    {"role": "user", "content": prompt},
                ],
                stream=False
            )

            result_text = response.choices[0].message.content

            # 解析JSON结果
            try:
                # 查找花括号内的JSON对象
                json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
                if json_match:
                    result_json = json.loads(json_match.group(0))
                    locations = result_json.get("locations", [])
                    keywords = result_json.get("keywords", [])
                    return locations, keywords
                else:
                    print(f"无法在结果中找到JSON: {result_text}")
                    return [], []
            except json.JSONDecodeError:
                print(f"JSON解析失败: {result_text}")
                return [], []

        except Exception as e:
            print(f"处理用户查询失败: {str(e)}")
            return [], []

deepseekapi = DeepSeekAPI(settings.DEEP_SEEK_API_KEY)