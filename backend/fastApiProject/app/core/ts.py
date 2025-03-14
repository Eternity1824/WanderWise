import json

from services.MysqlService import mysql_service


def process_post(post_id, locations_json):
    """
    处理帖子和相关地点信息

    Args:
        post_id: 帖子ID
        locations_json: 地点信息的JSON字符串
    """
    try:
        # 解析JSON
        locations = json.loads(locations_json)
        print(f"正在处理帖子,post id: {post_id}")

        # 检查是否有地点信息
        if not locations or len(locations) == 0:
            print(f"可能的地点[]")
            print(f"帖子 {post_id} 没有相关地点信息，跳过")
            return

        # 打印可能的地点
        place_names = [loc.get('name', '未知地点') for loc in locations]
        print(f"可能的地点{place_names}")

        # 处理每个地点
        for location in locations:
            # 获取Google Place ID
            place_id = location.get('place_id')
            if not place_id:
                print(f"地点缺少place_id, 跳过")
                continue

            # 注意：这里交换了参数顺序，确保place_id存储Google Place ID，note_id存储帖子ID
            result = mysql_service.add_mapping(
                place_id=place_id,  # Google Place ID
                note_id=post_id  # 帖子ID
            )

            if result:
                print(f"成功添加地点映射: 地点ID={place_id}, 帖子ID={post_id}")

    except json.JSONDecodeError:
        print(f"JSON解析失败: {locations_json}")
        print(f"```json\n{locations_json}\n```")
        print(f"可能的地点[]")
    except Exception as e:
        print(f"处理帖子 {post_id} 时发生错误: {str(e)}")


# 使用示例
if __name__ == "__main__":
    # 示例1: 没有地点
    process_post("66b063f900000000050318f6", "[]")

    # 示例2: 有地点
    example_locations = '[{"place_id":"ChIJAcrA3ZMVkFQRS16FQgt6wqs","name":"Kin Len Thai Night Bites, Seattle"}]'
    process_post("671ea9fc00000000240167ed", example_locations)