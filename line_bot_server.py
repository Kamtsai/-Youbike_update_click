from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import os
import threading
from youbike_scraper import scrape_youbike, send_line_message

app = Flask(__name__)

line_bot_api = LineBotApi(os.environ['LINE_CHANNEL_ACCESS_TOKEN'])
handler = WebhookHandler(os.environ['LINE_CHANNEL_SECRET'])

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    if event.message.text.lower() == "更新youbike":
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="正在更新 YouBike 数据，请稍候...")
        )
        threading.Thread(target=update_youbike).start()

def update_youbike():
    results = scrape_youbike()
    if results:
        message = "YouBike站點可借車輛數量:\n" + "\n".join(results)
    else:
        message = "未找到 YouBike 站点数据"
    send_line_message(message)

if __name__ == "__main__":
    app.run()
