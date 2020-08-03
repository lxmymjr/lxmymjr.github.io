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
import datetime
import time

def getHTMLText(url): # 获取网页的HTML源码
    try:
        kv = {'user-agent':'Mozilla/5.0', 'authorization':'Bearer secret!'}
        # 设置响应等待时间为30秒
        r = requests.get(url, headers=kv, timeout=30)
        # 检查状态码是否为200，否则抛出异常。
        r.raise_for_status()
        time.sleep(5)
        # 返回请求的相应内容。
        return r.text
    except Exception as e:
        # 抛出异常则重试
        print e
        return getHTMLText(url)

def getdata(json_activities):
    for i in range(len(json_activities['data'])):
        verb = json_activities['data'][i]['verb']
        if verb == 'ANSWER_VOTE_UP':
            answer_id = json_activities['data'][i]['target']['id']
            vote_time = datetime.datetime.fromtimestamp(json_activities['data'][i]['created_time']).strftime('%Y-%m-%d %H:%M:%S')
            answer_created_time = datetime.datetime.fromtimestamp(json_activities['data'][i]['target']['created_time']).strftime('%Y-%m-%d %H:%M:%S')
            answer_updated_time = datetime.datetime.fromtimestamp(json_activities['data'][i]['target']['updated_time']).strftime('%Y-%m-%d %H:%M:%S')
            thanks_count = json_activities['data'][i]['target']['thanks_count']
            voteup_count = json_activities['data'][i]['target']['voteup_count']
            answer_count = json_activities['data'][i]['target']['question']['answer_count']
            topic_ids = json_activities['data'][i]['target']['question']['bound_topic_ids']
            question_created_time = datetime.datetime.fromtimestamp(json_activities['data'][i]['target']['question']['created']).strftime('%Y-%m-%d %H:%M:%S')
            question_id = json_activities['data'][i]['target']['question']['id']
            title = json_activities['data'][i]['target']['question']['title']
            author = json_activities['data'][i]['target']['author']['name']
            question = getHTMLText('https://www.zhihu.com/question/' + str(question_id))
            try:
                topics = BeautifulSoup(question).find(itemprop="keywords")['content']
            except:
                topics = ''
            answerinsertorupdate(answer_id, vote_time, answer_created_time, answer_updated_time, thanks_count, voteup_count, answer_count, question_created_time, question_id, title, author, topics)
        elif verb == 'MEMBER_VOTEUP_ARTICLE':
            article_id = json_activities['data'][i]['target']['id']
            vote_time = datetime.datetime.fromtimestamp(json_activities['data'][i]['created_time']).strftime('%Y-%m-%d %H:%M:%S')
            created_time = datetime.datetime.fromtimestamp(json_activities['data'][i]['target']['created']).strftime('%Y-%m-%d %H:%M:%S')
            updated_time = datetime.datetime.fromtimestamp(json_activities['data'][i]['target']['updated']).strftime('%Y-%m-%d %H:%M:%S')
            voteup_count = json_activities['data'][i]['target']['voteup_count']
            title = json_activities['data'][i]['target']['title']
            author = json_activities['data'][i]['target']['author']['name']
            articleinsertorupdate(article_id, vote_time, created_time, updated_time, voteup_count, title, author)
        else:
            print verb

def answerinsertorupdate(answer_id, vote_time, answer_created_time, answer_updated_time, thanks_count, voteup_count, answer_count, question_created_time, question_id, title, author, topics):
    # 执行一条SQL语句，插入一条记录
    try:
        cursor.execute('INSERT INTO Answer (answer_id, vote_time, answer_created_time, answer_updated_time, thanks_count, voteup_count, answer_count, question_created_time, question_id, title, author, topics) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (answer_id, vote_time, answer_created_time, answer_updated_time, thanks_count, voteup_count, answer_count, question_created_time, question_id, title, author, topics))
        print 'data insert successfully'
    except:
        # 如果该数据已经存在，则插入异常，改用更新数据
        try:
            cursor.execute('UPDATE Answer SET vote_time = ?, answer_created_time = ?, answer_updated_time = ?, thanks_count = ?, voteup_count = ?, answer_count = ?, question_created_time = ?, question_id = ?, title = ?, author = ?, topics = ? WHERE answer_id = ?', (vote_time, answer_created_time, answer_updated_time, thanks_count, voteup_count, answer_count, question_created_time, question_id, title, author, topics, answer_id))
            print 'data update successfully'
        except Exception as e:
            print 'update: ' + str(e)

def articleinsertorupdate(article_id, vote_time, created_time, updated_time, voteup_count, title, author):
    # 执行一条SQL语句，插入一条记录
    try:
        cursor.execute('INSERT INTO Article (article_id, vote_time, created_time, updated_time, voteup_count, title, author) VALUES (?, ?, ?, ?, ?, ?, ?)', (article_id, vote_time, created_time, updated_time, voteup_count, title, author))
        print 'data insert successfully'
    except:
        # 如果该数据已经存在，则插入异常，改用更新数据
        try:
            cursor.execute('UPDATE Article SET vote_time = ?, created_time = ?, updated_time = ?, voteup_count = ?, title = ?, author = ? WHERE article_id = ?', (vote_time, created_time, updated_time, voteup_count, title, author, article_id))
            print 'data update successfully'
        except Exception as e:
            print 'update: ' + str(e)

def dbtablecreate():
    # 执行一条SQL语句，创建Answer表和Article表
    try:
        cursor.execute('create table Answer (answer_id INT primary key, vote_time TEXT, answer_created_time TEXT, answer_updated_time TEXT, thanks_count INT, voteup_count INT, answer_count INT, question_created_time TEXT, question_id INT, title TEXT, author TEXT, topics TEXT)')
        cursor.execute('create table Article (article_id INT primary key, vote_time TEXT, created_time TEXT, updated_time TEXT, voteup_count INT, title TEXT, author TEXT)')
        print "Table created successfully"
    except Exception as e:
        print e

# 连接到SQLite数据库
# 如果文件不存在，会自动在当前目录创建
doubandatabase = sqlite3.connect('liuximing.db')
# 创建一个Cursor
cursor = doubandatabase.cursor()
# 创建一个数据库表
dbtablecreate()
homepageurl = 'https://www.zhihu.com/people/liu-xi-ming-5/activities'
homepage = getHTMLText(homepageurl)
after_id = re.search(u'after_id=(\d+)', homepage).group(1)
activities = getHTMLText('http://www.zhihu.com/api/v4/members/liu-xi-ming-5/activities?limit=20&after_id=' + after_id + '&desktop=True')
while True:
    json_activities = json.loads(activities)
    getdata(json_activities)
    if json_activities['paging']['is_end']:
        break
    url = json_activities['paging']['next']
    activities = getHTMLText(url)
# 关闭Cursor
cursor.close()
# 提交事务
doubandatabase.commit()
# 关闭Connection
doubandatabase.close()