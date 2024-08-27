import requests
import os
import json

LINE_CHANNEL_ACCESS_TOKEN = os.environ.get('LINE_CHANNEL_ACCESS_TOKEN')
LINE_USER_ID = os.environ.get('LINE_USER_ID')

TARGET_STATIONS = [
    "忠孝新生站",
    "忠孝復興站",
    "忠孝東路四段49巷口",
    "信義大安路口",
    "敦化信義路口",
    "信義敦化路口"
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
            if 'sna' in station and 'sbi' in station:
                station_name = station['sna']
                if any(target in station_name for target in TARGET_STATIONS):
                    available_bikes = station['sbi']
                    results.append(f"{station_name}: {available_bikes}")
        
        print(f"匹配到 {len(results)} 个目标站点")
        if not results:
            print("未找到匹配的站点，显示所有站点名称：")
            for station in data[:20]:  # 显示前20个站点名称
                print(station.get('sna', 'Unknown station name'))
        return results
    except requests.RequestException as e:
        print(f"请求失败: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"JSON 解析失败: {e}")
        return None
    except Exception as e:
        print(f"爬取过程中发生未知错误: {e}")
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
    except requests.RequestException as e:
        print(f"发送 Line 消息时发生错误: {e}")
        print(f"错误响应: {e.response.text if e.response else 'No response'}")

def main():
    print("YouBike 爬虫开始运行...")
    results = scrape_youbike()
    if results:
        print("爬取成功，准备发送 Line 消息...")
        message = "YouBike站點可借車輛數量:\n" + "\n".join(results)
        send_line_message(message)
    else:
        print("爬取失败，未找到数据")
        send_line_message("YouBike爬虫未找到目标站点数据，请检查脚本。")

if __name__ == "__main__":
    main()
