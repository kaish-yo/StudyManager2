#Postgres用
import os

#ライブラリをインストール
from flask import Flask, request, abort
from time import time
import datetime
#他ファイルからインポート
from db import db
from models.time_records import TimeModel

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)

app = Flask(__name__)
db.init_app(app)
@app.before_first_request
    def create_tables():
        db.create_all()



#Direct the location of the database
##Herokuの場合は第一引数、ローカルの場合は第二引数を参照するように設定
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL','sqlite:///data.db')
#Disable track recording in SQLAlchemy so as to work faster
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False



line_bot_api = LineBotApi('bCxcsrJMtZoSBkcEUKxo2meIVxL6TvfvTBPU4YU78XMOv+2DD2PoLRo7m/LBDl1OVY2Zl8U32I8rYwye1lDoj9FCTAOoppjAzLw8QFs19iqhMBftbD5zcHJwVgAv/tTZPaZSlkwbswnoZbqz2frqCgdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('2eb98ca7615b9ac2d883570595da7cab')

@app.route("/")
def test():
    return "OK"

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'

#ここで送信メッセージをハンドリングする
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    # line_bot_api.reply_message(
    #     event.reply_token,
    #     TextSendMessage(text="あなたは{}と言いました".format(event.message.text))
    response = event.message.text

    #データベースに保存するための変数（共通）
    date = datetime.date.today()
    recordedtime = int(time())

    if response == "勉強開始":
        start_end_flag = 0
        new_record = TimeModel(date=date, recordedtime=recordedtime, start_end_flag=start_end_flag)
        new_record.save_to_database()
        replying_message = "記録を開始しました!一緒に勉強を楽しんでいこう!"
    elif response =="勉強終了":
        start_end_flag = 1
        #スタート時間のレコードをGET
        last_record = TimeModel.get_last_data()

        if last_record.start_end_flag == 0:
            studytime = recordedtime - last_record.recordedtime
            studytime_in_str = datetime.timedelta(seconds=(studytime))

            if studytime >=28800:
                replying_message = "殿、ご苦労様でした！\n前回開始から勉強時間は{}...!!\n殿は生けるレジェンドですな!!!".format(studytime_in_str)
            elif studytime >= 18000:
                replying_message = "長時間お疲れ様でした！\n前回開始から勉強時間は、なんと{}！\nお前は…本当に…すごいやつだッ…!!!".format(studytime_in_str)
            else:
                replying_message = "お疲れ様！\n前回開始から{}勉強しました！".format(studytime_in_str)

        else:
            replying_message = "Error:勉強開始時間が記録されていません。"
            line_bot_api.reply_message(
                 event.reply_token,
                 TextSendMessage(text=replying_message))
    #返信メッセージを送信する
    line_bot_api.reply_message(
         event.reply_token,
         TextSendMessage(text=replying_message))


    #データベースに保存する
    new_record = TimeModel(date, recordedtime, start_end_flag)
    new_record.save_to_database()


if __name__ == '__main__':
    app.run()
