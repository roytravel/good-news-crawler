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

    def insertMysql(self, url, title, time):
        query = "INSERT INTO coinness(title, post_time, url, upload_time) VALUES(%s, %s, %s, %s)"
        self.cursor.execute(query, (title, time, url, datetime.today()))
        self.conn.commit()
        print ('[*] Success : {}'.format(title))

    def checkDuple(self, title, url):
        query = "SELECT * FROM coinness WHERE title = %s and url = %s"
        response = self.cursor.execute(query, (title, url))

        if response == 0:
            return False
        else:
            return True
  
def main():
    S = Slack()
    T = Tool()
    URL = "https://kr.coinness.com"

    response = requests.get(URL)
    if response.status_code == 200:
        res = response.text
        soup = BeautifulSoup(res, 'html.parser')
        newsContainer = soup.findAll('ul', {'class':'newscontainer'})

        for idx in range(len(newsContainer)):
            for li in newsContainer[idx].findAll('li'):
                # get post link 
                for link in li.findAll("a", href=True):
                    if "javascript" not in link['href']:
                        fullURL = URL  + link['href']
                        # print ("[*] {}".format(fullURL))

                # get post title
                for title in li.findAll("h3"):
                    if "공유하기" not in title.text:
                        titleValue = title.text.replace('\n','').replace("                                       ","").replace('                      ','').replace("                  ","")
                        titleValue = titleValue[6:]
                        # print ("[*] {}".format(titleValue))

                # get post time
                for time in li.findAll("span", {"class":"newstime"}):
                    time = time.text.strip('\n').strip(' ')
                    timeValue = (datetime.today().strftime("%Y.%m.%d ") + time)
                    # print ("[*] {}".format(timeValue))

                flag = T.checkDuple(titleValue, fullURL)

                if flag == False:
                    T.insertMysql(fullURL, titleValue, timeValue)
                    S.send(fullURL, titleValue, timeValue)

                else:
                    print ("[!] Content Duplicated : {}".format(titleValue))


if __name__ == "__main__":
    sys.exit(main())