import requests
import os
import json

def scrape_youbike():
    api_url = "https://apis.youbike.com.tw/api/front/station/all?location=taipei&lang=tw&type=2"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'application/json',
        'Referer': 'https://www.youbike.com.tw/',
        'Origin': 'https://www.youbike.com.tw',
    }
    
    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()
        data = response.json()

        if not isinstance(data, dict) or 'retVal' not in data or not isinstance(data['retVal'], list):
            print("Unexpected data structure")
            return []

        stations = data['retVal']
        
        target_stations = [
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

        results = []
        for station in stations:
            station_name = station.get('name_tw', '')
            if station_name in target_stations:
                available_bikes = station.get('available_spaces', 'N/A')
                results.append(f"{station_name}: {available_bikes}")

        return results

    except requests.RequestException as e:
        print(f"Request failed: {e}")
        return []
    except json.JSONDecodeError as e:
        print(f"JSON parsing failed: {e}")
        return []
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return []

# 移除了主函数和自动运行的代码


# import requests
# import os
# import json
# import time
# import random

# LINE_CHANNEL_ACCESS_TOKEN = os.environ.get('LINE_CHANNEL_ACCESS_TOKEN')
# LINE_USER_ID = os.environ.get('LINE_USER_ID')

# TARGET_STATIONS = [
#     "捷運忠孝新生站(3號出口)",
#     "捷運忠孝新生站(4號出口)",
#     "捷運忠孝新生站(2號出口)",
#     "捷運忠孝新生站(1號出口)",
#     "捷運忠孝復興站(2號出口)",
#     "忠孝東路四段49巷口",
#     "捷運忠孝復興站(3號出口)",
#     "信義大安路口(信維大樓)",
#     "敦化信義路口(東南側)",
#     "信義敦化路口"
# ]


# def scrape_youbike():
#     api_url = "https://apis.youbike.com.tw/api/front/station/all?location=taipei&lang=tw&type=2"
#     headers = {
#         'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
#         'Accept': 'application/json',
#         'Referer': 'https://www.youbike.com.tw/',
#         'Origin': 'https://www.youbike.com.tw',
#     }
#     print(f"正在请求 API URL: {api_url}")
#     try:
#         time.sleep(random.uniform(1, 3))
#         response = requests.get(api_url, headers=headers)
#         response.raise_for_status()
#         print(f"API 请求成功，状态码: {response.status_code}")
#         data = response.json()
#         print(f"API 返回数据类型: {type(data)}")
#         print(f"API 返回数据结构: {json.dumps(data, ensure_ascii=False, indent=2)[:500]}")  # 打印前500个字符
#     except requests.RequestException as e:
#         print(f"API 请求失败: {e}")
#         return []
#     except json.JSONDecodeError as e:
#         print(f"JSON 解析错误: {e}")
#         return []

#     results = []
#     all_stations = []

#     if isinstance(data, dict) and 'retVal' in data and isinstance(data['retVal'], list):
#         stations = data['retVal']
#     else:
#         print(f"未找到预期的数据结构")
#         return []

#     for station in stations:
#         station_name = station.get('name_tw', '')
#         all_stations.append(station_name)
#         if station_name in TARGET_STATIONS:
#             available_bikes = station.get('available_spaces', 'N/A')
#             results.append(f"{station_name}: {available_bikes}")

#     if not results:
#         print("未找到任何匹配的站点信息")
#     print(f"找到的所有站点数量: {len(all_stations)}")
#     print(f"部分站点名称: {all_stations[:10]}")  # 只打印前10个站点名称

#     return results


# def send_line_message(message):
#     print("开始发送 Line 消息...")
#     if not LINE_CHANNEL_ACCESS_TOKEN or not LINE_USER_ID:
#         print("错误: LINE_CHANNEL_ACCESS_TOKEN 或 LINE_USER_ID 未设置")
#         return
    
#     url = 'https://api.line.me/v2/bot/message/push'
#     headers = {
#         'Content-Type': 'application/json',
#         'Authorization': f'Bearer {LINE_CHANNEL_ACCESS_TOKEN}'
#     }
#     data = {
#         'to': LINE_USER_ID,
#         'messages': [{'type': 'text', 'text': message}]
#     }
#     try:
#         response = requests.post(url, headers=headers, json=data)
#         response.raise_for_status()
#         print(f"Line 消息发送成功，响应状态: {response.status_code}")
#     except requests.RequestException as e:
#         print(f"发送 Line 消息时发生错误: {e}")
#         print(f"错误响应: {e.response.text if e.response else 'No response'}")

# def main():
#     print("YouBike 爬虫开始运行...")
#     results = scrape_youbike()
#     if results:
#         print("爬取成功，准备发送 Line 消息...")
#         message = "YouBike站點可借車輛數量:\n" + "\n".join(results)
#         send_line_message(message)
#     else:
#         print("爬取失败，未找到数据")
#         send_line_message("YouBike爬虫未找到目标站点数据，请检查脚本。")

# if __name__ == "__main__":
#     main()
