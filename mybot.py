import os, sys
from flask import Flask, request
from pymessenger import Bot
import pprint
import json
import os.path
import numpy as np
pp = pprint.PrettyPrinter(indent=4)


PAGE_ACCESS_TOKEN = 'EAAbHXRREfRsBAIRpFY5OZBYIZCpaMk7tB8TLmQfxGlbc2ZAZAaiok2bccTkJz7NEG0dHJBfnSa7KefD1p1q1qBBcG2efyKIHhXjCZBoSaYlEAVKmsqf91z9oZAl6KttPJeRj2HjuSkhUEKhbJYPyi2xhhSseUhJUk3JNsxMoDrfLKVAZCNVgh5T'

bot = Bot(PAGE_ACCESS_TOKEN)
app = Flask(__name__)

@app.route('/', methods=['GET'])
def verify():
    # Webhook verification
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == "hello":
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200
    return "Hello world", 200

@app.route('/', methods=['POST'])
def webhook():                  
    data = request.get_json()
    log(pp.pprint(data))
    if data['object'] == 'page':
        for entry in data['entry']:
            for messaging_event in entry['messaging']:
            # IDs
                sender_id = messaging_event['sender']['id']
                recipient_id = messaging_event['recipient']['id']

                if messaging_event.get('message'):
                # Extracting text message
                    if 'text' in messaging_event['message']:
                        messaging_text = messaging_event['message']['text']
                    else:
                        messaging_text = '沒打字喔'
                    if  'attachments' in messaging_event['message']:
                        message_image_url = messaging_event['message']['attachments'][0]['payload']
                        if os.path.isfile('food'+sender_id+'.txt') & os.path.isfile('place'+sender_id+'.txt') & os.path.isfile('check'+sender_id+'.txt'):
                            url = message_image_url
                            json.dump(url,open('image'+sender_id+'.txt','w'))
                            bot.send_text_message(sender_id, '圖片上傳成功 確認無誤想要發布的話 請打 傳送 ex 傳送')
                        else :
                            bot.send_text_message(sender_id, '圖片上傳失敗 因為要先給地點跟食物')

                # Echo
                    if messaging_text == '吃':
                        ID = np.load('id.npy')
                        if any(someone == sender_id for someone in ID):
                            bot.send_text_message(sender_id, '你不是註冊過了嗎？會提醒你啦別擔心')
                        else : 
                            ID_new = np.append(ID,sender_id)
                            np.save('id.npy',ID_new)
                            response = '以後有食物都會提醒你'
                            bot.send_text_message(sender_id, response)
                        print(np.load('id.npy'))
                    elif messaging_text == '不給了':
                        if os.path.isfile('food'+sender_id+'.txt'):
                            os.remove('food'+sender_id+'.txt')
                        if os.path.isfile('place'+sender_id+'.txt'):
                            os.remove('place'+sender_id+'.txt')
                        if os.path.isfile('image'+sender_id+'.txt'):
                            os.remove('image'+sender_id+'.txt')
                        if os.path.isfile('check'+sender_id+'.txt'):
                            os.remove('check'+sender_id+'.txt')    
                        response = '好喔，希望你以後再提供大家好吃的'
                        bot.send_text_message(sender_id, response)
                    elif messaging_text == '不吃':
                        ID = np.load('id.npy')
                        for index,everyone in enumerate(ID) :
                            if everyone == sender_id:
                                ID_new = np.delete(ID,index)
                        np.save('id.npy',ID_new)
                        print(np.load('id.npy'))
                        
                        response = '以後有食物都不跟你說'
                        bot.send_text_message(sender_id, response)
                    elif messaging_text == '給食物':
                        with open('check'+sender_id+'.txt','w') as outfile:
                            json.dump(messaging_text,outfile,indent = 4, ensure_ascii = False)
                        response = '請給我完整資訊 先告訴我食物名稱吧：ex：漢堡'
                        bot.send_text_message(sender_id, response)
                    elif os.path.isfile('check'+sender_id+'.txt') & (not os.path.isfile('food'+sender_id+'.txt')):
                        with open('food'+sender_id+'.txt','w') as outfile:
                            json.dump(messaging_text,outfile,indent = 4, ensure_ascii = False)
                        response = '成功，接下來請告訴我地點 ex 成大一活1f'
                        bot.send_text_message(sender_id, response)
                    elif os.path.isfile('check'+sender_id+'.txt') & os.path.isfile('food'+sender_id+'.txt') & (not os.path.isfile('place'+sender_id+'.txt')):
                        place = messaging_text
                        with open('place'+sender_id+'.txt','w') as outfile:
                            json.dump(messaging_text,outfile,indent = 4, ensure_ascii = False)
                        response = '成功，請拍一張食物的照片給我(請拍橫的比較好)'
                        bot.send_text_message(sender_id, response)
                       
                    elif messaging_text == '傳送': 
                        if os.path.isfile('food'+sender_id+'.txt') & os.path.isfile('place'+sender_id+'.txt') & os.path.isfile('image'+sender_id+'.txt'):
                            with open ('food'+sender_id+'.txt', "r") as myfile:
                                food=myfile.readlines()
                                print(type(food[0]))
                            with open ('place'+sender_id+'.txt', "r") as myfile:
                                place=myfile.readlines()
                                print(type(place[0]))
                            url_json = json.load(open('image'+sender_id+'.txt'))
                            url = url_json["url"]
                            print(type(url))
                            print(url)
                            
                            elements = [
                                {
                                    "title":'食物：'+food[0][1:-1],
                                    "image_url":url,
                                    "subtitle":'地點：'+place[0][1:-1],
                                }
                            ]
                            ID = np.load('id.npy')
                            for everyone in ID:
                                bot.send_generic_message(everyone,elements)
                            os.remove('food'+sender_id+'.txt')
                            os.remove('place'+sender_id+'.txt')
                            os.remove('image'+sender_id+'.txt')
                            os.remove('check'+sender_id+'.txt')    
                        else :
                            bot.send_text_message(sender_id, '你要給我食物跟地點才能傳送喔')
                            
                    elif os.path.isfile('image'+sender_id+'.txt') :
                        pass
                    else :
                        response = '如果希望有多的食物提醒你請打 “吃” ，如果你有多的食物請打 “給食物”' 
                        bot.send_text_message(sender_id, response)
                        food_mode = 0

    return "ok",200 
    
def log(message):
    sys.stdout.flush()



if __name__ == "__main__":
    app.run(debug = True, port = 3034)
