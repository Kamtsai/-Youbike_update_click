import requests
import os
import json

LINE_NOTIFY_TOKEN = os.environ.get('LINE_CHANNEL_ACCESS_TOKEN')

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
    url = "https://tcgbusfs.blob.core.windows.net/dotapp/youbike/v2/youbike_immediate.json"
    try:
        response = requests.get(url)
        response.raise_for_status()
        print(f"API Response Status: {response.status_code}")
        data = response.json()
        print(f"Total stations received: {len(data)}")
        print(f"First station data: {json.dumps(data[0], ensure_ascii=False) if data else 'No data'}")

        results = []
        for station in data:
            if any(target in station.get('sna', '') for target in TARGET_STATIONS):
                available_bikes = station.get('sbi', 'N/A')
                results.append(f"{station['sna']}: {available_bikes}")
        
        print(f"Matched stations: {len(results)}")
        if not results:
            print("Target stations not found. Available stations:")
            for station in data[:10]:
                print(f"- {station.get('sna', 'Unknown')}")
        
        return "\n".join(results)
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"JSON parsing failed: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

def send_line_notify(message):
    if not LINE_NOTIFY_TOKEN:
        print("LINE_CHANNEL_ACCESS_TOKEN not set")
        return
    
    url = 'https://notify-api.line.me/api/notify'
    headers = {'Authorization': f'Bearer {LINE_NOTIFY_TOKEN}'}
    data = {'message': message}
    try:
        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()
        print(f"Line Notify Response: {response.status_code}")
    except requests.RequestException as e:
        print(f"Failed to send Line notification: {e}")

def main():
    print("Starting YouBike scraper...")
    result = scrape_youbike()
    if result:
        print("Scraping successful. Sending to Line...")
        send_line_notify(f"\nYouBike站點可借車輛數量:\n{result}")
    else:
        print("No data found for target stations.")
        send_line_notify("YouBike爬虫未找到目标站点数据,请检查脚本。")

if __name__ == "__main__":
    main()
