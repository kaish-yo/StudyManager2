#Postgres用
import os

#ライブラリをインストール
from flask import Flask, request, abort
from time import time
import datetime
#他ファイルからインポート
from db import db
from models.time_records import TimeModel
from models.studytime_record import StudytimeModel
from functions import time_presentaiton

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

#Direct the location of the database
##Herokuの場合は第一引数、ローカルの場合は第二引数を参照するように設定
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL','sqlite:///data.db')
#Disable track recording in SQLAlchemy so as to work faster
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

'''
下記はローカル用
'''
# @app.before_first_request
# def create_tables():
#     db.create_all()
'''
Herokuにdeployする際はコメントアウト
'''

line_bot_api = LineBotApi('bCxcsrJMtZoSBkcEUKxo2meIVxL6TvfvTBPU4YU78XMOv+2DD2PoLRo7m/LBDl1OVY2Zl8U32I8rYwye1lDoj9FCTAOoppjAzLw8QFs19iqhMBftbD5zcHJwVgAv/tTZPaZSlkwbswnoZbqz2frqCgdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('2eb98ca7615b9ac2d883570595da7cab')

@app.route("/")
def test():
    return 'OK'

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
    userId = event.source.user_id

    if response == "勉強開始":
        start_end_flag = 0
        new_record = TimeModel(userId=userId, date=date, recordedtime=recordedtime, start_end_flag=start_end_flag)
        new_record.save_to_database()
        replying_message = "記録を開始しました!一緒に勉強を楽しんでいこう!"
        
    elif response =="勉強終了":
        start_end_flag = 1
        #スタート時間のレコードをGET
        last_record = TimeModel.get_last_data(userId)

        if last_record.start_end_flag == 0:
            studytime = recordedtime - last_record.recordedtime
            studytime_in_str = time_presentaiton(studytime)

            #データベースに保存する
            new_record = TimeModel(userId=userId, date=date, recordedtime=recordedtime, start_end_flag=start_end_flag)
            new_record.save_to_database()

            #合計時間用DBに保存する
            new_total = StudytimeModel(userId=userId, date=date, year=date.year,
                                       month=date.month, 
                                       eachtime=studytime)
            new_total.save_to_database_total()

            # if studytime >=28800:
            #     replying_message = "殿、ご苦労様でした！\n前回開始から勉強時間は{}...!!\n殿は生けるレジェンドですな!!!".format(studytime_in_str)
            # elif studytime >= 18000:
            #     replying_message = "長時間お疲れ様でした！\n前回開始から勉強時間は、なんと{}！\nお前は…本当に…すごいやつだッ…!!!".format(studytime_in_str)
            #else:
            replying_message = "お疲れ様！\n前回開始から{}勉強しました！".format(studytime_in_str)

        else:
            replying_message = "Error:勉強開始時間が記録されていません。"
            # line_bot_api.reply_message(
            #      event.reply_token,
            #      TextSendMessage(text=replying_message))
        
    elif response=="今日は終了":
        #今日の勉強時間を合計を返信する
        totaltime = StudytimeModel.sum_of_daily_total(userId=userId, date=date)
        totaltime_in_str = time_presentaiton(totaltime)
        
        if totaltime >=28800:
            replying_message = "陛下、本日もご苦労様でした！本日の御勉強時間は、\n{}...!!\n陛下は生けるレジェンドですな!!!".format(totaltime_in_str)
        elif totaltime >= 18000:
            replying_message = "長時間お疲れ様でした！今日の勉強時間は、\nなんと{}！\nお前は…本当に…すごいやつだッ…!!!".format(totaltime_in_str)
        else:
            replying_message ="今日の勉強時間は、\n{}です！お疲れ様でした！".format(totaltime_in_str)

    elif "月合計を教えて" in response:
        month = response.split('月')
        month = month[0]
        totaltime = StudytimeModel.sum_of_monthly_total(userId=userId, month=month)
        totaltime_in_str = time_presentaiton(totaltime)
        replying_message = "{}月の勉強時間は、合計で\n{}です！".format(month, totaltime_in_str)    

    elif response == "俺のすべてを教えて":
        totaltime = StudytimeModel.sum_of_entire(userId=userId)
        totaltime_in_str = time_presentaiton(totaltime)
        replying_message = "よかろう。汝のすべてを教えてやる。\nおぬしの総勉強時間は{}だ！".format(totaltime_in_str)    

    #返信メッセージを送信する
    line_bot_api.reply_message(event.reply_token,
                               TextSendMessage(text=replying_message))

if __name__ == "__main__":  

    if app.config['DEBUG']:
        #データベースを作成するための
        @app.before_first_request
        def create_tables():
            db.create_all()
    
    app.debug = False
    app.run()
