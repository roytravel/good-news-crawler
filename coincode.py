# -*- coding:utf-8 -*-
import os
import sys
import requests
import pymysql
from bs4 import BeautifulSoup
from datetime import datetime
from slack import Slack

class Tool(object):
    def __init__(self):
        self.conn = pymysql.connect(host='localhost', user='root', password=os.environ['MYSQL_PASSWORD'], db='good-news', charset='utf8mb4')
        self.cursor = self.conn.cursor()

    def insertMysql(self, title, time, url, category):
        query = "INSERT INTO coincode(title, post_time, url, upload_time, category) VALUES(%s, %s, %s, %s, %s)"
        self.cursor.execute(query, (title, time, url, datetime.today(), category))
        self.conn.commit()
        print ('[*] Success : {}'.format(title))

    def checkDuple(self, title, url):
        query = "SELECT * FROM coincode WHERE title = %s and url = %s"
        response = self.cursor.execute(query, (title, url))

        if response == 0:
            return False
        else:
            return True

def main():
    S = Slack()
    T = Tool()

    URL = ["https://coincode.kr/archives/category/news", "https://coincode.kr/archives/category/blockchain"]

    for idx in range(len(URL)):
        count = 0
        already = False
        response = requests.get(URL[idx])
        if response.status_code == 200:
            res = response.text
            soup = BeautifulSoup(res, 'html.parser')
            mainContent = soup.find('div', {'class':'td-ss-main-content'})

            for thumbNail in mainContent.findAll('div', {'class':'td-module-thumb'}):
                for content in thumbNail.findAll('a', href=True):
                    urlValue = content['href']
                    titleValue = content['title']

                    innerResponse = requests.get(urlValue)
                    if innerResponse.status_code == 200:
                        innerRes = innerResponse.text
                        innerSoup = BeautifulSoup(innerRes, 'html.parser')
                        timeValue = innerSoup.find('time', {'class':'entry-date updated td-module-date'})
                        timeValue = timeValue["datetime"].strip("+09:00").replace("T", " ")

                    dupFlag = T.checkDuple(titleValue, urlValue)
                    category = "news" if idx == 0 else "blockchain"

                    if dupFlag == False:
                        print (f"[*] {urlValue}")
                        print (f"[*] {titleValue}")
                        print (f"[*] {timeValue}")
                        print ('\n')

                        T.insertMysql(titleValue, timeValue, urlValue, category)
                        S.send(titleValue, timeValue, urlValue)

                    else:
                        count = count + 1
                        if count == 3:
                            already = True
                        print (f"[!] Content Duplicated : {titleValue}")

                if already:
                    break


if __name__ == "__main__":
    sys.exit(main())