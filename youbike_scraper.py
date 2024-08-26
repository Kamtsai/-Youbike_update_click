import os
import requests
import json
import time
import random

# Line Messaging API
LINE_CHANNEL_ACCESS_TOKEN = os.environ['LINE_CHANNEL_ACCESS_TOKEN']
LINE_USER_ID = os.environ['LINE_USER_ID']  # 您的Line用户ID或群组ID

TARGET_STATIONS = [
    "捷運忠孝新生站(3號出口)",
    "捷運忠孝新生站(4號出口)",
    "捷運忠孝新生站(2號出口)",
    "捷運忠孝新生站(1號出口)",
    "捷運忠孝復興站(2號出口)",
    "忠孝東路四段49巷口",
    "捷運忠孝復興站(3號出口)",
    "信義大安路口(信維大樓)",
    "敦化信義路口(東南側)",
    "信義敦化路口"
]

def scrape_youbike():
    api_url = "https://apis.youbike.com.tw/api/front/station/all?location=taipei&lang=tw&type=2"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'application/json',
        'Referer': 'https://www.youbike.com.tw/',
        'Origin': 'https://www.youbike.com.tw',
    }
    try:
        time.sleep(random.uniform(1, 3))
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        return f"API 请求失败: {e}"
    except json.JSONDecodeError as e:
        return f"JSON 解析错误: {e}"

    results = []

    if isinstance(data, dict) and 'retVal' in data and isinstance(data['retVal'], list):
        stations = data['retVal']
    else:
        return "未找到预期的数据结构"

    for station in stations:
        station_name = station.get('name_tw', '')
        if station_name in TARGET_STATIONS:
            available_bikes = station.get('available_spaces', 'N/A')
            results.append(f"{station_name}: {available_bikes}")

    if not results:
        return "未找到任何匹配的站点信息"

    return "\n".join(results)

def send_line_message(message):
    url = 'https://api.line.me/v2/bot/message/push'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {LINE_CHANNEL_ACCESS_TOKEN}'
    }
    data = {
        'to': LINE_USER_ID,
        'messages': [{'type': 'text', 'text': message}]
    }
    response = requests.post(url, headers=headers, json=data)
    print(f"Line API response: {response.status_code}")
    response.raise_for_status()

if __name__ == "__main__":
    result = scrape_youbike()
    send_line_message(result)
