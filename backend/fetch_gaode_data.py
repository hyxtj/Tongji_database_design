"""
fetch_gaode_data.py
------------------
使用高德开放平台 API 获取实时交通或天气等数据，并输出为 JSON。

用法：
    python fetch_gaode_data.py --type traffic --city 北京 --key <你的高德Key>
    python fetch_gaode_data.py --type weather --city 北京 --key <你的高德Key>

依赖：requests
"""
import argparse
import requests
import sys

GAODE_TRAFFIC_URL = "https://restapi.amap.com/v3/traffic/status/circle"
GAODE_WEATHER_URL = "https://restapi.amap.com/v3/weather/weatherInfo"

def fetch_traffic(city, key):
    params = {
        "key": key,
        "center": "121.473701,31.230416",  # 上海人民广场经纬度
        "radius": 5000,
        "extensions": "all"
    }
    resp = requests.get(GAODE_TRAFFIC_URL, params=params)
    print(resp.text)

def fetch_weather(city, key):
    params = {
        "key": key,
        "city": city,
        "extensions": "all"
    }
    resp = requests.get(GAODE_WEATHER_URL, params=params)
    print(resp.text)

def main():
    parser = argparse.ArgumentParser(description="高德API数据抓取脚本")
    parser.add_argument('--type', choices=['traffic', 'weather'], required=True, help='数据类型')
    parser.add_argument('--city', required=True, help='城市名或adcode')
    parser.add_argument('--key', required=True, help='高德开放平台Key')
    args = parser.parse_args()

    if args.type == 'traffic':
        fetch_traffic(args.city, args.key)
    elif args.type == 'weather':
        fetch_weather(args.city, args.key)
    else:
        print('不支持的数据类型')
        sys.exit(1)

if __name__ == "__main__":
    main()
