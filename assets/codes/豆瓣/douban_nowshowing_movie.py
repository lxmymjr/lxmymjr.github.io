# coding=utf-8
import requests # 导入请求库
import re # 导入正则表达式库
import json # 导入JSon库
from bs4 import BeautifulSoup # 导入HTML解析库
import bs4
# Python 2.7使用Requests发起https请求时会报一大堆Warning但并不影响使用，这句话使Warning不显示在Build Result中
import urllib3
urllib3.disable_warnings()
# 导入SQLite库
import sqlite3
import csv

def getHTMLText(url): # 获取网页的HTML源码
    try:
        # 设置响应等待时间为30秒
        r = requests.get(url, timeout=30)
        # 检查状态码是否为200，否则抛出异常。
        r.raise_for_status()
        # 返回请求的相应内容。
        return r.text
    except Exception as e:
        # 抛出异常则重试
        print(e)
        return getHTMLText(url)

def getnowshowing(url, city):
    text = getHTMLText(url + city)
    # 将获取到的资源转换为soup对象
    soup = BeautifulSoup(text)
    # 找到所有样式为lists的标签
    lists = soup.find(class_="lists")
    # 遍历其儿子节点
    for eachmoive in lists.children:
        if type(eachmoive) == bs4.element.Tag:
            # 找到所需字段
            name = eachmoive['data-title']
            rating = float(eachmoive['data-score'])
            votes = int(eachmoive['data-votecount'])
            if eachmoive['data-duration'].encode('utf-8') == '':
                duration = 0
            else:
                duration = int(str(eachmoive['data-duration'].encode('utf-8')).split('\\')[0].split('\'')[1])
            # 插入数据
            dbinsert(name, rating, votes, duration)

def dbtablecreate():
    # 执行一条SQL语句，创建NowShowingMoive表
    try:
        cursor.execute('CREATE TABLE NowShowingMoive (name TEXT PRIMARY KEY, rating REAL, votes INT, duration INT)')
        print('Table created successfully')
    except Exception as e:
        print(e)
    
def dbinsert(name, rating, votes, duration):
    # 执行一条SQL语句，插入一条记录
    try:
        cursor.execute('INSERT INTO NowShowingMoive (name, rating, votes, duration) VALUES (?, ?, ?, ?)', (name, rating, votes, duration))
        print('data insert successfully')
    except Exception as e:
        print('insert: ' + str(e))

def dbquery(name):
    # 以电影名称为关键词查询数据库
    try:
        cursor.execute('SELECT name, rating, votes, duration FROM NowShowingMoive WHERE name = ?', (name))
        for row in cursor:
            return row
    except Exception as e:
        print('query: ' + str(e))

# 连接到SQLite数据库
# 如果文件不存在，会自动在当前目录创建
doubandatabase = sqlite3.connect('豆瓣.db')
# 创建一个Cursor
cursor = doubandatabase.cursor()
# 如果数据库表已经存在，则删除
cursor.execute('DROP TABLE IF EXISTS NowShowingMoive')
# 创建一个数据库表
dbtablecreate()
nowshowing_url = 'https://movie.douban.com/cinema/nowplaying/'
city = 'wuhan'
nowshowing = getnowshowing(nowshowing_url, city)
# 关闭Cursor
cursor.close()
# 提交事务
doubandatabase.commit()
# 关闭Connection
doubandatabase.close()

conn = sqlite3.connect('豆瓣.db')
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
for i in cursor.fetchall():
    tablename = i[0]
    cursor.execute("SELECT * FROM '{}'".format(tablename))
    with open(tablename + '.csv', 'w', newline='', encoding='utf_8_sig') as csv_file: 
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow([j[0] for j in cursor.description])
        csv_writer.writerows(cursor)