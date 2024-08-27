import requests
import os
from bs4 import BeautifulSoup

# 从环境变量获取Line Notify token
LINE_NOTIFY_TOKEN = os.environ['LINE_CHANNEL_ACCESS_TOKEN']

# 目标站点列表
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
    url = "https://tcgbusfs.blob.core.windows.net/dotapp/youbike/v2/youbike_immediate.json"
    response = requests.get(url)
    data = response.json()

    results = []
    for station in data:
        if station['sna'] in TARGET_STATIONS:
            available_bikes = station['sbi']
            results.append(f"{station['sna']}: {available_bikes}")
    
    return "\n".join(results)

def send_line_notify(message):
    url = 'https://notify-api.line.me/api/notify'
    headers = {'Authorization': f'Bearer {LINE_NOTIFY_TOKEN}'}
    data = {'message': message}
    response = requests.post(url, headers=headers, data=data)
    print(f"Line Notify Response: {response.status_code}")

def main():
    print("Starting YouBike scraper...")
    result = scrape_youbike()
    if result:
        print("Scraping successful. Sending to Line...")
        send_line_notify(f"\nYouBike站點可借車輛數量:\n{result}")
    else:
        print("No data found for target stations.")

if __name__ == "__main__":
    main()
