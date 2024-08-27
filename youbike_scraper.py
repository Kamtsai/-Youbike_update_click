import requests
import os
import json
import sys

LINE_CHANNEL_ACCESS_TOKEN = os.environ.get('LINE_CHANNEL_ACCESS_TOKEN')
LINE_USER_ID = os.environ.get('LINE_USER_ID')

TARGET_STATIONS = [
    "YouBike2.0_捷運忠孝新生站(3號出口)",
    "YouBike2.0_捷運忠孝新生站(4號出口)",
    "YouBike2.0_捷運忠孝新生站(2號出口)",
    "YouBike2.0_捷運忠孝新生站(1號出口)",
    "YouBike2.0_捷運忠孝復興站(2號出口)",
    "YouBike2.0_忠孝東路四段49巷口",
    "YouBike2.0_捷運忠孝復興站(3號出口)",
    "YouBike2.0_信義大安路口(信維大樓)",
    "YouBike2.0_敦化信義路口(東南側)",
    "YouBike2.0_信義敦化路口"
]

def scrape_youbike():
    print("开始爬取 YouBike 数据...")
    url = "https://tcgbusfs.blob.core.windows.net/dotapp/youbike/v2/youbike_immediate.json"
    try:
        response = requests.get(url)
        response.raise_for_status()
        print(f"API 响应状态: {response.status_code}")
        data = response.json()
        print(f"获取到 {len(data)} 个站点")

        results = []
        for station in data:
            if station['sna'] in TARGET_STATIONS:
                available_bikes = station['sbi']
                results.append(f"{station['sna']}: {available_bikes}")
        
        print(f"匹配到 {len(results)} 个目标站点")
        return "\n".join(results)
    except Exception as e:
        print(f"爬取过程中发生错误: {e}")
        return None

def send_line_message(message):
    print("开始发送 Line 消息...")
    if not LINE_CHANNEL_ACCESS_TOKEN or not LINE_USER_ID:
        print("错误: LINE_CHANNEL_ACCESS_TOKEN 或 LINE_USER_ID 未设置")
        return
    
    url = 'https://api.line.me/v2/bot/message/push'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {LINE_CHANNEL_ACCESS_TOKEN}'
    }
    data = {
        'to': LINE_USER_ID,
        'messages': [{'type': 'text', 'text': message}]
    }
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        print(f"Line 消息发送成功，响应状态: {response.status_code}")
    except Exception as e:
        print(f"发送 Line 消息时发生错误: {e}")

def main():
    print("YouBike 爬虫开始运行...")
    result = scrape_youbike()
    if result:
        print("爬取成功，准备发送 Line 消息...")
        send_line_message(f"YouBike站點可借車輛數量:\n{result}")
    else:
        print("爬取失败，未找到数据")
        send_line_message("YouBike爬虫未找到目标站点数据，请检查脚本。")

if __name__ == "__main__":
    main()
