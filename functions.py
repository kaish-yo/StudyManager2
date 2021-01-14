def time_presentaiton(seconds):
    hour = seconds // 3600
    minute = (seconds % 3600)//60
    
    return "{}時間{}分".format(hour,minute)

# def send_message(replying_message):
#      #返信メッセージを送信する
#     line_bot_api.reply_message(
#             event.reply_token,
#             TextSendMessage(text=replying_message))

