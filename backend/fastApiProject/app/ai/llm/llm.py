import json
import re
from typing import List, Dict, Any, Optional, Tuple
from openai import OpenAI

api_key = "lm-studio"
base_url = "http://10.242.195.117:1234/v1"
model = "llama-3.2-3b-instruct"
class DeepSeekAPI:
    """DeepSeek API 服务封装"""

    def __init__(self):
        """初始化 DeepSeek 客户端

        Args:
            api_key: DeepSeek API密钥
        """
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = model

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
                json_match = re.search(r'\[([^\[\]]|\[(?:[^\[\]]|\[.*?\])*?\])*\]', locations_text, re.DOTALL)
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

    def verify_locations(self, locations: List[str]) -> List[str]:
        """从帖子中提取可能的地理位置

        Args:
            locations: 提取的地点列表，格式为 ["地点名, 城市", ...]

        Returns:
            验证的地点列表，格式为 ["地点名, 城市", ...]
        """
        print("需要验证:", locations)
        prompt = f"""
        Delete all locations not in format ["地点名, 城市", ...], only return the list without extra text.

        ### Locations to Validate:
        {locations}
        """

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "you are a formatting expert, return with specific format"},
                    {"role": "user", "content": prompt},
                ],
                stream=False
            )

            locations_text = response.choices[0].message.content
            print(locations_text)
            import ast

            list_data = ast.literal_eval(locations_text)
            return list_data
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
    def rate_post(self, post: Dict[str, Any]) -> Dict[str, int]:
        """对帖子进行打分

        Args:
            post: 帖子数据

        Returns:
            评分结果，格式为 {"score": 分数}
        """

        # 准备评分提示
        prompt = f"""
        请对这篇美食或旅游点评进行打分（满分100分），评分标准如下：
        1. 内容质量（30分）：描述详细程度、是否有实用信息
        2. 真实性（20分）：是否有实际体验的描述细节
        3. 受欢迎度（50分）：根据用户互动数据评估

        点评信息：
        标题: {post.get('title', '')}
        内容: {post.get('desc', '')}

        用户互动数据：
        点赞数: {post.get('liked_count', '0')}
        收藏数: {post.get('collected_count', '0')}
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
    
    def associate(self, query: str)-> List[str]:
        prompt = f"""
            请根据以下用户查询，从中联想出一些关键词，并将这些关键词与查询进行关联。

            ### **规则**:
            1. 从用户的查询中，提取出最相关的关键词并进行联想。
            2. 你可以进行关键词合并,如西雅图景点，请尽量输出合并关键词，如西雅图景点。
            3. 这些关键词应该是与查询主题、内容或意图最相关的单词或短语。
            4. 返回的关键词列表必须是**简洁**和**相关的**，按优先级排序。
            5. 请避免返回与查询无关的词汇。
            6. 如果输入为英文，请你先翻译成中文

            ### **例子**:
            1. 输入“去西雅图玩”
            2. 输出["“西雅图景点”，", "旅行", “西雅图旅游”， “地点” ...]

            ### **输出格式**:
            ["关键词1", "关键词2", ...]

            用户输入:{query}
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个专业的分析助手，只输出JSON格式结果"},
                    {"role": "user", "content": prompt},
                ],
                stream=False
            )

            result_text = response.choices[0].message.content

            # 解析JSON结果
            try:
                json_match = re.search(r'\[([^\[\]]|\[(?:[^\[\]]|\[.*?\])*?\])*\]', result_text, re.DOTALL)
                if json_match:
                    result_json = json.loads(json_match.group(0))
                    return result_json
                else:
                    print(f"无法在结果中找到JSON: {result_text}")
                    return []
            except json.JSONDecodeError:
                print(f"JSON解析失败: {result_text}")
                return []

        except Exception as e:
            print(f"处理用户查询失败: {str(e)}")
            return []


    def process_user_query(self, query: str) -> Tuple[List[str], List[str]]:
        """
        旅游精准推荐系统：根据用户需求提供具体地点建议

        Args:
            query: 用户的旅游相关提问或搜索内容

        Returns:
            JSON格式的具体地点推荐和关键词提取结果
        """
        prompt = f"""
        你是一个专业的旅游顾问AI。分析以下用户查询，并提供以下信息：

        1. 推荐具体地点列表：
           - 根据用户提到的城市/地区，推荐该地区内与用户兴趣相关的具体场所、景点或目的地
           - 提供尽可能多的特定地点（而非泛泛的区域），例如具体的景点名称、餐厅区域、活动场所等
           - 每个推荐地点必须是明确的地标或场所，不要只返回城市名称
           - 例如：用户提到"西雅图滑雪"，应返回"史蒂文斯山口"、"水晶山"等具体滑雪场所

        2. 提取关键词：
           - 识别用户查询中的活动类型、兴趣或需求（如"滑雪"、"美食"、"徒步"等）

        用户查询: {query}

        以JSON格式返回结果，返回的location后需要拼接城市的名字, 根据地区返回对应的语言，必须注意例如地点在美国，返回英文地点
        {{
            "locations": ["具体地点1", "具体地点2", "具体地点3", ...],
            "keywords": ["关键词1", "关键词2", ...]
        }}

        仅返回JSON对象，不包含任何额外说明或解释。如果无法确定具体地点或关键词，相应列表返回为空。
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

deepseekapi = DeepSeekAPI()