from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, ImageMessage
import os
from youbike_scraper import scrape_youbike

app = Flask(__name__)

# 从环境变量获取 LINE Channel Secret 和 Channel Access Token
line_bot_api = LineBotApi(os.environ['LINE_CHANNEL_ACCESS_TOKEN'])
handler = WebhookHandler(os.environ['LINE_CHANNEL_SECRET'])

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    
    return 'OK'

@handler.add(MessageEvent, message=(TextMessage, ImageMessage))
def handle_message(event):
    if isinstance(event.message, TextMessage):
        if event.message.text.lower() == "更新youbike":
            results = scrape_youbike()
            if results:
                message = "YouBike站點可借車輛數量:\n" + "\n".join(results)
            else:
                message = "無法獲取YouBike數據，請稍後再試。"
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=message))
        else:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="請輸入 '更新youbike' 來獲取最新的YouBike資訊。")
            )
    
    elif isinstance(event.message, ImageMessage):
        try:
            message_content = line_bot_api.get_message_content(event.message.id)
            file_path = f"image_{event.message.id}.jpg"
            with open(file_path, "wb") as f:
                for chunk in message_content.iter_content():
                    f.write(chunk)
            
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="圖片已接收並保存。")
            )
            
            # 注意: Heroku的文件系統是臨時的,如果需要永久保存,請考慮使用雲存儲服務
            
        except LineBotApiError as e:
            print(f"Error handling image message: {e}")
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="處理圖片時發生錯誤,請稍後再試。")
            )

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
