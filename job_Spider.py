import sys
import re
import requests
import lxml.html
import mysql.connector
from lxml import etree
from chardet import detect
from bs4 import BeautifulSoup

baseURL = ""
paramsURL = ".html?lang=c&postchannel=0000&workyear=99&cotype=99&degreefrom=99&jobterm=99&companysize=99&ord_field=0&dibiaoid=0&line=&welfare="
headers = {
    "Referer": "",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36"
}
dbConfig = {
    'host': 'localhost',
    'user': 'root',
    'password': '962921921',
    'port': 3306,
    'database': 'py_database',
    'charset': 'utf8mb4'
}

pageIndex = 1


class MysqlDB:

    def __init__(self, dbConfig):
        try:
            self.db = mysql.connector.connect(**dbConfig)
            self.cursor = self.db.cursor()
            self.cursor.execute("SELECT VERSION()")
            data = self.cursor.fetchone()
            print("数据库版本: %s " % data)
        except mysql.connector.Error as e:
            print('connect fails!{}'.format(e))

    def close(self):
        if self.cursor != None:
            self.cursor.close()
        if self.db != None:
            self.db.close()
        print("数据库关闭...")

    def __items(self, sqlCommand, params=None):
        count = 0
        try:
            count = self.cursor.execute(sqlCommand, params)
            self.db.commit()
        except Exception as e:
            print(e)
        return count

    def Insert(self, sqlCommand, params=None):
        return self.__items(sqlCommand, params)

    def Delete(self, sqlCommand, params=None):
        return self.__items(sqlCommand, params)

    def Update(self, sqlCommand, params=None):
        return self.__items(sqlCommand, params)

    def SelectSingle(self, sqlCommand, params=None):
        dataOne = None
        try:
            count = self.cursor.execute(sqlCommand, params)
            if count != 0:
                dataOne = self.cursor.fetchone()
        except Exception as ex:
            print(ex)
        return dataOne

    def Select(self, sqlCommand, params=None):
        dataall = None
        try:
            count = self.cursor.execute(sqlCommand, params)
            if count != 0:
                dataall = self.cursor.fetchall()
        except Exception as ex:
            print(ex)
        return dataall


def getUrl(pageIndex):
    return baseURL+str(pageIndex)+paramsURL


def findjobs(baseURL, pageIndex, encoding, db):
    rep = requests.get(url=baseURL, headers=headers)
    rep.encoding = encoding
    html = rep.content
    tree = etree.HTML(html)
    sumCount = re.findall(
        r"\d+\.?\d*", tree.xpath('//*[@id="resultList"]/div/div/div/div/span[1]')[0].text)[0]
    for job in tree.xpath('//*[@id="resultList"]/div'):
        jobinfo = job.xpath('.//span/a')
        joburl = job.xpath(".//span/a/@href")
        address = job.xpath('.//span[@class="t3"]')
        money = job.xpath('.//span[@class="t4"]')
        time = job.xpath('.//span[@class="t5"]')
        if jobinfo != []:
            if money[0].text is None:
                money="暂无薪资"
            else:
                money=money[0].text.strip()
            db.Insert("INSERT INTO job_spider (title,money,company,address,time,url)VALUES(%s, %s, %s, %s, %s,%s )",(jobinfo[0].text.strip(),money,jobinfo[1].text.strip(),address[0].text.strip(),time[0].text.strip(),str(joburl[0])))
            #print(jobinfo[0].text.strip(),money,jobinfo[1].text.strip(),address[0].text.strip(),time[0].text.strip(),str(joburl[0]))
            # pass
    pageIndex += 1
    if pageIndex > int(sumCount):
        return
    return findjobs(getUrl(pageIndex), pageIndex, encoding, db)


def main():
    db = MysqlDB(dbConfig)
    findjobs(getUrl(pageIndex), pageIndex, 'gbk', db)
    db.close()


if __name__ == "__main__":
    main()
