from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, ImageMessage
import os
import tempfile
import logging
from youbike_scraper import scrape_youbike

app = Flask(__name__)

# 设置日志
logging.basicConfig(level=logging.INFO)

# 从环境变量获取 LINE Channel Secret 和 Channel Access Token
line_bot_api = LineBotApi(os.environ['LINE_CHANNEL_ACCESS_TOKEN'])
handler = WebhookHandler(os.environ['LINE_CHANNEL_SECRET'])

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    logging.info("Request body: " + body)
    
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        logging.error("Invalid signature")
        abort(400)
    except Exception as e:
        logging.error(f"Unexpected error in callback: {e}")
        abort(500)
    
    return 'OK'

@handler.add(MessageEvent, message=(TextMessage, ImageMessage))
def handle_message(event):
    try:
        if isinstance(event.message, TextMessage):
            handle_text_message(event)
        elif isinstance(event.message, ImageMessage):
            handle_image_message(event)
    except Exception as e:
        logging.error(f"Error in handle_message: {e}")
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="處理消息時發生錯誤,請稍後再試。")
        )

def handle_text_message(event):
    if event.message.text.lower() == "1":
        try:
            results = scrape_youbike()
            if results:
                message = "YouBike站點可借車輛數量:\n" + "\n".join(results)
            else:
                message = "無法獲取YouBike數據，請稍後再試。"
        except Exception as e:
            logging.error(f"Error in scrape_youbike: {e}")
            message = "獲取YouBike數據時發生錯誤，請稍後再試。"
        
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=message))
    else:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="請輸入 '更新youbike' 來獲取最新的YouBike資訊。")
        )

def handle_image_message(event):
    try:
        message_content = line_bot_api.get_message_content(event.message.id)
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tf:
            for chunk in message_content.iter_content():
                tf.write(chunk)
            tempfile_path = tf.name
        
        # 这里可以添加处理图片的代码
        # 例如: process_image(tempfile_path)
        
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="圖片已接收並處理。")
        )
        
        # 处理完后删除临时文件
        os.unlink(tempfile_path)
        
    except LineBotApiError as e:
        logging.error(f"LineBotApiError in handle_image_message: {e}")
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="處理圖片時發生錯誤,請稍後再試。")
        )
    except Exception as e:
        logging.error(f"Unexpected error in handle_image_message: {e}")
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="處理圖片時發生未知錯誤,請稍後再試。")
        )

@app.errorhandler(Exception)
def handle_exception(e):
    logging.error(f"Unhandled exception: {e}")
    return "Internal Server Error", 500

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
