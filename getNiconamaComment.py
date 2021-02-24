#!/usr/bin/env python
# -*- coding: utf-8 -*-
#summary:Get Nicolive comments.
import re
from getpass import getpass
import requests
import sys
import os
import websocket
from bs4 import BeautifulSoup
import json
import datetime
import time
import shutil
try:
    import thread
except ImportError:
    import _thread as thread

if not os.path.exists(".tmp"):
    os.mkdir(".tmp")

mail_regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'

session = requests.session()
session.headers = {"User-Agent":"getNiconamaComment.py/v0.0.1@Negima1072"}

if os.path.exists(".NiconicoUserSessionTmp"):
    with open(".NiconicoUserSessionTmp", mode="r") as f:
        user_session = f.readline()
    session.cookies.set("user_session", user_session)
    res = session.get("https://www.nicovideo.jp")

else:
    while True:
        email = input("Email: ")
        if not re.search(mail_regex, email):
            print("Invalid email. Please try again.")
        else:
            break

    passwd = getpass("Password: #")

    login_param = {
        "mail_tel": email,
        "password": passwd
    }

    res = session.post("https://account.nicovideo.jp/api/v1/login", params=login_param, headers={"Content-Type":"x-www-form-urlencoded"})
    with open(".NiconicoUserSessionTmp", mode="w") as f:
        f.write(session.cookies.get("user_session"))

if res.headers.get("x-niconico-authflag") == "0":
    print("Login failed...")
    sys.exit(1)
else:
    user_id = str(res.headers.get("x-niconico-id"))
    print("Login success! : "+user_id)

lvid = input("LiveID(lv~~): ")

try:
    res = session.get("https://live2.nicovideo.jp/watch/"+lvid)
    soup = BeautifulSoup(res.text, "html.parser")
    jd = soup.find("script", id="embedded-data").get("data-props")
    jres = json.loads(jd)
except:
    print("Get movie data failed..")
    sys.exit(1)

ws = None
msgws = None
chats = []
last_res = 0
num = 0
whenn = jres["program"]["openTime"]
endt = jres["program"]["endTime"]
tmp = 1

def msgws_on_open(ws):
    def run(*args):
        req = [{"ping":{"content":"rs:0"}},{"ping":{"content":"ps:0"}},{"thread":{"thread":ws.cookie[7:-1],"version":"20061206","when":whenn,"user_id":user_id,"res_from":-200,"with_global":1,"scores":1,"nicoru":0,"waybackkey":""}},{"ping":{"content":"pf:0"}},{"ping":{"content":"rf:0"}}]
        ws.send(json.dumps(req))
        #print("↑"+str(req))
    thread.start_new_thread(run, ())

def msgws_on_mess(ws, msg):
    global last_res
    global whenn
    global num
    global chats
    global tmp
    res = json.loads(msg)
    #print("↓"+str(res))
    if "chat" in res:
        chats.append(res)
        if len(chats) >= 1000:
            with open(".tmp/comments-"+str(tmp), mode="w", encoding="utf-8") as f:
                f.write(json.dumps(chats))
            chats.clear()
            tmp+=1
    elif "thread" in res:
        if whenn > endt+200:
            mws_on_close(ws)
        else:
            try:
                last_res = int(res["thread"]["last_res"])
            except:
                pass
    elif "ping" in res:
        if res["ping"]["content"][0:2] == "rf":
            if num == 0: whenn+=20
            else: whenn+=10
            num+=1
            req = [{"ping":{"content":"rs:"+str(num)}},{"ping":{"content":"ps:"+str(num*5)}},{"thread":{"thread":ws.cookie[7:-1],"version":"20061206","when":whenn,"user_id":user_id,"res_from":last_res+1,"with_global":1,"scores":1,"nicoru":0,"waybackkey":""}},{"ping":{"content":"pf:"+str(num*5)}},{"ping":{"content":"rf:"+str(num)}}]
            ws.send(json.dumps(req))
            #print("↑"+str(req))

def msgws_on_close(msgws):
    global ws
    ws.close()

def mws_on_open(ws):
    def run(*args):
        req = {"type":"startWatching","data":{"stream":{"quality":"super_high","protocol":"hls","latency":"low","chasePlay":False},"room":{"protocol":"webSocket","commentable":True},"reconnect":False}}
        ws.send(json.dumps(req))
    thread.start_new_thread(run, ())

def mws_on_mess(ws, msg):
    global msgws
    res = json.loads(msg)
    if res["type"] == "ping":
        req = {"type": "pong"}
        ws.send(json.dumps(req))
        req = {"type": "keepSeat"}
        ws.send(json.dumps(req))
    elif res["type"] == "room":
        msgws = websocket.WebSocketApp(res["data"]["messageServer"]["uri"], on_open=msgws_on_open, on_message=msgws_on_mess, cookie="thread="+res["data"]["threadId"]+";")
        msgws.run_forever()

def mws_on_close(ws):
    global chats
    global tmp
    global lvid
    global last_res
    cs = []
    if tmp >= 2:
        for i in range(tmp - 1):
            with open(".tmp/comments-"+str(i+1), mode="r", encoding="utf-8") as f:
                cs += json.loads(f.read())
    cs += chats
    print(str(len(cs)) + " comments / "+str(last_res))
    shutil.rmtree(".tmp")
    with open("comments"+lvid+".json", mode="w", encoding="utf-8") as f:
        f.write(json.dumps(cs))
    print("Finished.")
    sys.exit(0)

websocket.enableTrace(True)
ws = websocket.WebSocketApp(
    jres["site"]["relive"]["webSocketUrl"]+"&frontend_id="+str(jres["site"]["frontendId"]),
    on_open=mws_on_open,
    on_message=mws_on_mess
)
ws.run_forever()
