# -*- coding: utf-8 -*-
import json
import requests
import time
import urllib
from datetime import *
import sys
import tempfile
from random import randint
import random, string, time
import json, requests, pprint
import logging
from watson_developer_cloud import ConversationV1
from subprocess import Popen, PIPE
import urllib.request
import time
from pydub import AudioSegment
from os import path
import os
import speech_recognition as sr


TOKEN = "682400460:AAENfCuT6Gqehg3dcFsLwazdAJuE8bdD4T4"
URL = "https://api.telegram.org/bot{}/".format(TOKEN)
FILE_URL = "https://api.telegram.org/file/bot{}/".format(TOKEN)

TOKEN_WHATSAPP = "9hv9a22w6mlookkj"
URL_WHATSAPP = "https://eu3.chat-api.com/instance24731/"

def hasNumbers(inputString):
    return any(char.isdigit() for char in inputString)

def get_url(url):
    response = requests.get(url)
    content = response.content.decode("utf8")
    return content

def get_json_from_url(url):
    content = get_url(url)
    js = json.loads(content)
    return js

def get_updates(offset=None):
    url = URL + "getUpdates"
    if offset:
        url += "?offset={}".format(offset)
    print(url)
    js = get_json_from_url(url)
    return js

def get_updates_whatsapp(offset=None):
    url = URL_WHATSAPP + "messages?token={}".format(TOKEN_WHATSAPP)
    if offset:
        url += "&lastMessageNumber={}".format(offset)
    print(url)
    js = get_json_from_url(url)
    return js

def get_file(the_file_id=None):
    url = URL + "getFile"
    if the_file_id:
        url += "?file_id={}".format(the_file_id)
    js = get_json_from_url(url)
    print(js)
    return get_file_url(js['result']['file_path'])

def get_file_url(file_path):
    url = FILE_URL
    if file_path:
        url += file_path
    return url

def get_last_update_id(updates):
    update_ids = []
    for update in updates["result"]:
        update_ids.append(int(update["update_id"]))
    return max(update_ids)


def echo_all(updates):
    for update in updates["result"]:
        text = update["message"]["text"]
        chat = update["message"]["chat"]["id"]
        send_message(text, chat)

def processar_audio(audio_file):
    API_AI_KEY = ""
    AudioSegment.from_ogg(audio_file).export(audio_file+".flac", format="flac")
    xAUDIO_FILE = path.join(path.dirname(path.realpath(__file__)), audio_file+".flac")
    r = sr.Recognizer()
    with sr.AudioFile(xAUDIO_FILE) as source:
        audio = r.record(source)
    audio_message = ''
    try:
        audio_message = r.recognize_wit(audio, key=API_AI_KEY)
    except sr.UnknownValueError:
        print("*FALHA* API could not understand audio")
    except sr.RequestError as e:
        print("*FALHA* Could not reach stt service; {0}".format(e))

    print("AUDIO="+audio_file)
    print("audio_message = ")

    print((u' '+audio_message).encode('utf-8').strip())

    os.remove(audio_file)
    os.remove(audio_file+".flac")

    return audio_message

def pre_processar(updates):
    print("updates");
    print(updates);
    for update in updates["result"]:
        text = '';
        try:
            if(len(update["message"]["text"])>0):
                text = update["message"]["text"]
        except KeyError:
            pass
        try:
            if(len(update["message"]["voice"])>0):
                file_name = "voice/"+time.strftime("%Y%m%d-%H%M%S")+".ogg"
                urllib.request.urlretrieve(get_file(update["message"]["voice"]["file_id"]), (file_name))
                text = processar_audio(file_name)
        except KeyError:
            pass
        chat = update["message"]["chat"]["id"]
        processar(chat, text, "telegram")

def pre_processar_whastapp(updates):
    for update in updates["messages"]:
        text = '';
        if not(update["fromMe"]):
            try:
                if(update["type"]=='ptt'):
                    print("processar audio")
                    file_name = "voice/"+time.strftime("%Y%m%d-%H%M%S")+".ogg"
                    urllib.request.urlretrieve(update["body"], file_name)
                    text = processar_audio(file_name)
                if(update["type"]=='chat'):
                    print("type chat")
                    print((u' '+update["body"]).encode('utf-8').strip())
                    text = update["body"]
            except KeyError:
                pass
            chat = update["chatId"]
            processar(chat, text, "whastapp")        


def get_last_chat_id_and_text(updates):
    num_updates = len(updates["result"])
    last_update = num_updates - 1
    text = updates["result"][last_update]["message"]["text"]
    chat_id = updates["result"][last_update]["message"]["chat"]["id"]
    return (text, chat_id)


def send_message(text, chat_id):
    text = urllib.parse.quote_plus(text)
    url = URL + "sendMessage?parse_mode=markdown&text={}&chat_id={}".format(text, chat_id)
    print(url)
    get_url(url)

def send_message_whastapp(text, chat_id):
    print("SEND MSG WHATSAPP")
    text = urllib.parse.quote_plus(text)
    url = URL_WHATSAPP + "sendMessage?token={}&body={}&chatId={}".format(TOKEN_WHATSAPP, text, chat_id)
    print(url)
    get_url(url)

def send_message_whastapp_i(text, abcnome, chat_id):
    print("SEND MSG WHATSAPP")
    text = urllib.parse.quote_plus(text)
    url = URL_WHATSAPP + "sendFile?token={}&body={}&filename={}&chatId={}".format(TOKEN_WHATSAPP, text, abcnome, chat_id)
    print(url)
    get_url(url)

def processar(chat, message, platform):

    conversation = ConversationV1(
        username="apikey",
        password="80VUnIsigtKZIrg1QkwkUTu_8JuQRhvke_4FZFC41T5x",
        url='https://gateway-wdc.watsonplatform.net/assistant/api',
    version='2018-07-10')



    workspace_id = '0742b813-a704-4d1e-a38e-9f72517b1469'

    message = (u' '+message).encode('utf-8').strip()

    response = conversation.message(workspace_id=workspace_id, message_input={'text': message.decode()})
    

    abcd = response['output']['generic'][0]['source']
    abcnome = response['output']['generic'][0]['source']

    if(len(response['output']['text'])>0):
        for valx in response['output']['text']:
            retorno = valx
            if(platform=='whastapp'):
                print("send_message_whastapp")
                send_message_whastapp(retorno, chat)
            else:
                print("send_message")
                send_message(retorno, chat)
    else:
        print('OIIIIII', abcd)
        send_message_whastapp_i(abcd, abcnome, chat)

def main():
    last_update_id = None
    last_update_id_whastapp = 0
    file = open("last_update_id_whastapp", "r") 
    read = file.read() 
    if(read):
        if(int(read)>0):
            last_update_id_whastapp = int(read)
    while True:
        try:
            updates = get_updates(last_update_id)
            if len(updates["result"]) > 0:
                last_update_id = get_last_update_id(updates) + 1
                # echo_all(updates)
                pre_processar(updates)
            time.sleep(0.5)
        
            updates = get_updates_whatsapp((2438, last_update_id_whastapp)[last_update_id_whastapp>0]) #
            if len(updates["messages"]) > 0:
                last_update_id_whastapp = updates["lastMessageNumber"]
                file = open("last_update_id_whastapp","w") 
                file.write(str(last_update_id_whastapp))
                file.close() 
                pre_processar_whastapp(updates)
            time.sleep(1)
        except:
            pass


if __name__ == '__main__':
    main()
