# test_api.py 改进版
import sys

sys.path.append('.')  # 确保可以找到app模块

from app.external.googlemap import geocode_finder


def main():
    # 添加查询参数的打印
    place = "Chiang's Gourmet, Seattle"
    region = "us"
    print(f"查询地点: {place}, 区域: {region}")

    result = geocode_finder.get_locations(place, region=region)
    print(result)


if __name__ == "__main__":
    main()