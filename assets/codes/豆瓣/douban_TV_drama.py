# coding=utf-8
import requests # 导入请求库
import re # 导入正则表达式库
import json # 导入JSon库
from bs4 import BeautifulSoup # 导入HTML解析库
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

def getTVdramalist(url, Numofpage):
    # 电视剧豆瓣地址列表
    TVdramalist = []
    # Numofpage为爬取页面数
    for i in range(int(Numofpage)):
        # 获取第i页网页的资源，20为每页的电视剧记录数
        text = getHTMLText(url+str(i*20))
        # 由于此url返回json对象，所以将获取到的资源转换为json格式
        json_text = json.loads(text)
        # 获取json中的url字段，存入TVdramalist列表
        for j in range(20):
            dic = json_text['subjects'][j]
            TVdramalist.append(dic['url'])
    return TVdramalist

def getTVdramainfo(url, writer):
    text = getHTMLText(url)
    # 将获取到的资源转换为soup对象
    soup = BeautifulSoup(text, features='html.parser')
    # 找到所需字段
    name = soup.find(property='v:itemreviewed').string
    rating = float(soup.find(property='v:average').string)
    votes = int(soup.find(property='v:votes').string)
    episode = int(re.search(u'集数:</span> (\d+)<br/>', text).group(1))
    duration = int(re.search(u'单集片长:</span> (\d+)分钟<br/>', text).group(1))
    #插入或者更新数据
    dbinsertorupdate(name, rating, votes, episode, duration)

def dbtablecreate():
    # 执行一条SQL语句，创建ChineseTVdrama表
    try:
        cursor.execute('CREATE TABLE ChineseTVdrama (name TEXT PRIMARY KEY, rating REAL, votes INT, episode INT, duration INT)')
        print('Table created successfully')
    except Exception as e:
        print(e)

def dbinsertorupdate(name, rating, votes, episode, duration):
    # 执行一条SQL语句，插入一条记录
    try:
        cursor.execute('INSERT INTO ChineseTVdrama (name, rating, votes, episode, duration) VALUES (?, ?, ?, ?, ?)', (name, rating, votes, episode, duration))
        print('data insert successfully')
    except:
        # 如果该数据已经存在，则插入异常，改用更新数据
        try:
            cursor.execute('UPDATE ChineseTVdrama SET rating = ?, votes = ?, episode = ?, duration = ? WHERE name = ?', (rating, votes, episode, duration, name))
            print('data update successfully')
        except Exception as e:
            print('update: ' + str(e))

def dbquery(name):
    # 以电视剧名称为关键词查询数据库
    try:
        cursor.execute('SELECT name, rating, votes, episode, duration FROM ChineseTVdrama WHERE name = ?', (name))
        for row in cursor:
            return row
    except Exception as e:
        print('query: ' + str(e))

moivelist_url = 'https://movie.douban.com/j/search_subjects?type=tv&tag=国产剧&sort=time&page_limit=20&page_start='
Numofpage = 5
# 获取最新5*20条电视剧的详情页链接
moivelist = getTVdramalist(moivelist_url, Numofpage)
# 连接到SQLite数据库
# 如果文件不存在，会自动在当前目录创建
doubandatabase = sqlite3.connect('豆瓣.db')
# 创建一个Cursor
cursor = doubandatabase.cursor()
# 创建一个数据库表
dbtablecreate()
# 从每个电视剧的详情页中获取所需字段存入数据库
for i in moivelist:
    try:
        getTVdramainfo(i, cursor)
    except Exception as e:
        print(e)
        continue
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