#!/usr/bin/env python
# -*- coding: utf-8 -*-
#summary:ニコニコ動画のコメント一覧を取得します。(oldV)
from bs4 import BeautifulSoup
import requests, datetime, json, os, sys, math, time
from getpass import getpass
import shutil

id = input("ID: ")
logname="log-"+datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")+"-"+id+".txt"
opmes="""
##################################
# Welcome to getComments Program #
#   Version: 1.0.0               #
#   Author:  Negima1072          #
##################################
"""

with open(logname, mode='w', encoding="utf-8") as f:
   f.write(opmes+"\n")
print(opmes)

def log(text, tp="MESSAGE"):
   now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
   with open(logname, mode='a', encoding="utf-8") as f:
      f.write(now+"["+tp+"]"+text+"\n")
   print(now+"["+tp+"]"+text)

log("Init this program")
log("Make log file => "+logname)

ses = requests.Session()
ses.headers = {"User-Agent":"getNicovideoComments.py/v0.0.1@Negima1072"}
loginurl = "https://secure.nicovideo.jp/secure/login?site=niconico"

log("Try to login on nicovideo.jp")

mail_regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
if os.path.exists(".NiconicoUserSessionTmp"):
    with open(".NiconicoUserSessionTmp", mode="r") as f:
        user_session = f.readline()
    session.cookies.set("user_session", user_session)
    res = session.get("https://www.nicovideo.jp").text

else:
    while True:
        email = input("Email: ")
        if not re.search(mail_regex, email):
            print("Invalid email. Please try again.")
        else:
            break

    passwd = getpass("Password: #")
    params={"mail": email, "password": passwd}
    res = ses.post(loginurl, params=params).text
    with open(".NiconicoUserSessionTmp", mode="w") as f:
        f.write(session.cookies.get("user_session"))

soup = BeautifulSoup(res, 'html.parser')
ch = soup.find_all("div", attrs={"class": "CommonHeader", "id": "CommonHeader"})[0].get("data-common-header")
d = json.loads(ch)
if str(d["initConfig"]["user"]["isLogin"]) == "True":
   log("Succeed to login by "+d["initConfig"]["user"]["nickname"])
   log("ID:"+str(d["initConfig"]["user"]["id"])+" Nickname:"+d["initConfig"]["user"]["nickname"]+" isPremium:"+str(d["initConfig"]["user"]["isPremium"]))
else:
   log("Failed to login. Program shutdown.", "ERROR")
   sys.exit()

chatsdir="./chats-"+id+"/"
if os.path.isdir(chatsdir):
   log("Check chats file => ./chats ...OK")
else:
   try:
      os.mkdir(chatsdir)
      log("Check chats file => ./chats ...OK")
   except:
      log("Check chats file => ./chats ...NG", "ERROR")
      sys.exit()

userid = str(d["initConfig"]["user"]["id"])
mvurl="https://www.nicovideo.jp/watch/"+id
log("Access to "+mvurl)
res = ses.get(mvurl).text
soup = BeautifulSoup(res, 'html.parser')
ch = soup.find_all("div", attrs={"id": "js-initial-watch-data"})[0].get("data-api-data")
d = json.loads(ch)
with open("js-initial-watch-data-"+id+".json", mode='w', encoding="utf-8") as f:
   f.write(ch)

log("smID:"+d["video"]["id"]+" title:"+d["video"]["title"])
userkey=d["context"]["userkey"]
dthread=d["thread"]["ids"]["default"]
contenthun=str(math.ceil(int(d["video"]["duration"])/60))
reqthread=[{"thread":{"language":0,"nicoru":3,"scores":1,"with_global":1,"version":20090904,"thread":str(dthread),"res_from":-1000}}]
msgurl="https://nmsg.nicovideo.jp/api.json"
res=ses.post(msgurl, json=reqthread).text
log("Get resentment chats 1000 => "+msgurl)
resjson=json.loads(res)
with open(chatsdir+id+"-recent.json", mode='w', encoding="utf-8") as f:
   f.write(res)
   log("Save recent comments file by json")

olderdate={"no":9999999999999999,"date":9999999999}
chats={}
for chat in resjson:
   if "chat" in chat.keys():
      if "nicoru" in chat["chat"].keys():
         if int(chat["chat"]["nicoru"]) > 9:
            chats[str(chat["chat"]["no"])]=chat["chat"]
            continue
      chats[str(chat["chat"]["no"])]=chat["chat"]
      if int(olderdate["no"]) > int(chat["chat"]["no"]):
         olderdate["no"] = int(chat["chat"]["no"])
         olderdate["date"] = int(chat["chat"]["date"])
log(str(len(chats))+" comments appended.")
log("Oldest comment is no-"+str(olderdate["no"]))

chanse = 0

while True:
   lastwhen=int(olderdate["date"])
   reqthread=[{"thread":{"language":0,"nicoru":3,"scores":1,"with_global":1,"version":20090904,"thread":str(dthread),"res_from":-1000,"when":lastwhen}}]
   res=ses.post(msgurl, json=reqthread).text
   log("Get old chats 1000 when "+str(olderdate["date"])+" => "+msgurl)
   resjson=json.loads(res)
   if len(resjson) <= 0:
      if chanse == 0:
         log("Response chats is null. Give one chanse.")
         chanse=1
      else:
         log("Response chats is null. Break while.")
         break
   else:
      chanse = 0
   with open(chatsdir+id+"-old"+str(olderdate["date"])+".json", mode='w', encoding="utf-8") as f:
      f.write(res)
      log("Save old comments file by json")
   for chat in resjson:
      if "chat" in chat.keys():
         if "nicoru" in chat["chat"].keys():
            if int(chat["chat"]["nicoru"]) > 9:
               chats[str(chat["chat"]["no"])]=chat["chat"]
               continue
         chats[str(chat["chat"]["no"])]=chat["chat"]
         if int(olderdate["no"]) > int(chat["chat"]["no"]):
            olderdate["no"] = int(chat["chat"]["no"])
            olderdate["date"] = int(chat["chat"]["date"])+1
   log(str(len(chats))+" comments appended.")
   log("Oldest comment is no-"+str(olderdate["no"]))
   if int(lastwhen) == int(olderdate["no"]):
      log("Response oldest chat is same to last response oldest char. Break while.")
      break
   if int(olderdate["no"]) <= 1:
      log("Response older chat is lower by first chat. Break while.")
      break;
   with open("comments-"+id+".json", mode='w', encoding="utf-8") as f:
      f.write(json.dumps(chats))
      log("Save all comments file by json","TMP")
   time.sleep(0.1)

log("Finished while program.")
with open("comments-"+id+".json", mode='w', encoding="utf-8") as f:
   f.write(json.dumps(chats))
   log("Save all comments file by json => commments.json")

log("Finished this program. Thank you.")