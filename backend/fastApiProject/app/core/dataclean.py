from external.deepseek import deepseekapi
from external.googlemap import geocode_finder
from services.ElasticSearch import es_service
from services.MysqlService import mysql_service
import json


def process_posts(posts_data, save_interval=50):
    """处理所有posts，每50条保存一次"""
    valid_posts = []
    i = 0

    for post in posts_data:
        print(f"正在处理第{i + 1}条post,post id: {post['note_id']}")
        # 使用DeepSeek提取地理位置
        potential_locations = deepseekapi.extract_locations(post)
        print(f"可能的地点{potential_locations}")
        coordinates_list = []  # 存储所有地点的经纬度

        # 对每个潜在地点查询坐标
        for location in potential_locations:
            place_detail = geocode_finder.get_place_detail(location)

            if place_detail["status"] == "OK":
                place_id = place_detail['place_id']
                note_id = post['note_id']

                # 将映射添加到MySQL
                mysql_service.add_mapping(place_id, note_id)

                # 将地点添加到Elasticsearch
                es_service.add_place(place_detail)

                # 只提取经纬度信息
                if 'geometry' in place_detail and 'location' in place_detail['geometry']:
                    coordinates = {
                        'latitude': place_detail['geometry']['location']['lat'],
                        'longitude': place_detail['geometry']['location']['lng'],
                        'place_id': place_detail['place_id'],
                        'name': place_detail.get('name', '')
                    }
                    coordinates_list.append(coordinates)

        # 如果找到了地理位置，则保留这个post
        if coordinates_list:
            # 使用DeepSeek对post进行评分
            score_info = deepseekapi.rate_post(post)

            # 将地理位置和评分信息添加到post中
            enriched_post = post.copy()
            enriched_post["locations"] = coordinates_list  # 只存储经纬度信息
            enriched_post["score"] = score_info.get("score", 0)

            valid_posts.append(enriched_post)

        i += 1

        # 每处理save_interval条帖子保存一次
        if i % save_interval == 0:
            try:
                with open(f'processed_search_contents_2025-03-11_part_{i // save_interval}.json', 'w',
                          encoding='utf-8') as f:
                    json.dump(valid_posts, f, ensure_ascii=False, indent=2)
                print(f"已处理 {i} 条帖子，找到 {len(valid_posts)} 个有效posts，已保存中间结果")
            except Exception as e:
                print(f"保存中间数据失败: {str(e)}")

    return valid_posts


