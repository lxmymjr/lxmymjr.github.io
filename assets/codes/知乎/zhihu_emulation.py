# coding=utf-8
import json # 导入JSon库
from bs4 import BeautifulSoup # 导入HTML解析库
from selenium import webdriver
# 导入SQLite库
import sqlite3
import time
import matplotlib.pyplot as plt # plt 用于显示图片
import matplotlib.image as mpimg # mpimg 用于读取图片

def login(login_url, homepage_url):
    browser = webdriver.PhantomJS()
    browser.implicitly_wait(5) # seconds
    browser.get(login_url)
    qrcodeurl = browser.find_element_by_class_name('qrcode-signin-img').get_attribute('src')
    plt.imshow(mpimg.imread(qrcodeurl)) # 显示图片
    plt.axis('off') # 不显示坐标轴
    plt.show()
    time.sleep(5) # seconds
    browser.get(homepage_url)
    if '该用户设置了隐私保护' in browser.page_source.encode('utf-8'):
        print '登录失败'
    else:
        browser.execute_script("setInterval(function(){document.body.scrollTop = document.body.scrollHeight;},50);")
        time.sleep(55555) # seconds
        try:
            getdata(browser.page_source)
        except Exception as e:
            print 'getdata: ' + str(e)
    browser.quit()

def getdata(string):
    for i in BeautifulSoup(string).find_all(class_="List-item"):
        item = i.contents[1]
        if 'AnswerItem' in item['class']:
            zop = json.loads(item['data-zop'])
            info = json.loads(item['data-za-module-info'])
            answer_id = zop['itemId']
            answer_created_time = item.find(itemprop="dateCreated")['content'].replace('T',' ').replace('.000Z', '')
            answer_updated_time = item.find(itemprop="dateModified")['content'].replace('T',' ').replace('.000Z', '')
            voteup_count = info['card']['content']['upvote_num']
            question_id = info['card']['content']['parent_token']
            title = zop['title']
            author = zop['authorName']
            answerinsertorupdate(answer_id, answer_created_time, answer_updated_time, voteup_count, question_id, title, author)
        elif 'ArticleItem' in item['class']:
            zop = json.loads(item['data-zop'])
            info = json.loads(item['data-za-module-info'])
            article_id = zop['itemId']
            created_time = item.find(itemprop="datePublished")['content'].replace('T',' ').replace('.000Z', '')
            updated_time = item.find(itemprop="dateModified")['content'].replace('T',' ').replace('.000Z', '')
            voteup_count = info['card']['content']['upvote_num']
            title = zop['title']
            author = zop['authorName']
            articleinsertorupdate(article_id, created_time, updated_time, voteup_count, title, author)

def answerinsertorupdate(answer_id, answer_created_time, answer_updated_time, voteup_count, question_id, title, author):
    # 执行一条SQL语句，插入一条记录
    try:
        cursor.execute('INSERT INTO Answer (answer_id, answer_created_time, answer_updated_time, voteup_count, question_id, title, author) VALUES (?, ?, ?, ?, ?, ?, ?)', (answer_id, answer_created_time, answer_updated_time, voteup_count, question_id, title, author))
        print 'data insert successfully'
    except Exception as e:
        print 'insert: ' + str(e)
        # 如果该数据已经存在，则插入异常，改用更新数据
        try:
            cursor.execute('UPDATE Answer SET answer_created_time = ?, answer_updated_time = ?, voteup_count = ?, question_id = ?, title = ?, author = ? WHERE answer_id = ?', (answer_id, answer_created_time, answer_updated_time, voteup_count, question_id, title, author))
            print 'data update successfully'
        except Exception as e:
            print 'update: ' + str(e)

def articleinsertorupdate(article_id, created_time, updated_time, voteup_count, title, author):
    # 执行一条SQL语句，插入一条记录
    try:
        cursor.execute('INSERT INTO Article (article_id, created_time, updated_time, voteup_count, title, author) VALUES (?, ?, ?, ?, ?, ?)', (article_id, created_time, updated_time, voteup_count, title, author))
        print 'data insert successfully'
    except Exception as e:
        print 'insert: ' + str(e)
        # 如果该数据已经存在，则插入异常，改用更新数据
        try:
            cursor.execute('UPDATE Article SET created_time = ?, updated_time = ?, voteup_count = ?, title = ?, author = ? WHERE article_id = ?', (created_time, updated_time, voteup_count, title, author, article_id))
            print 'data update successfully'
        except Exception as e:
            print 'update: ' + str(e)

def dbtablecreate():
    # 执行一条SQL语句，创建Answer表和Article表
    try:
        cursor.execute('create table Answer (answer_id INT primary key, answer_created_time TEXT, answer_updated_time TEXT, voteup_count INT, question_id INT, title TEXT, author TEXT)')
        cursor.execute('create table Article (article_id INT primary key, created_time TEXT, updated_time TEXT, voteup_count INT, title TEXT, author TEXT)')
        print "Table created successfully"
    except Exception as e:
        print e

# 连接到SQLite数据库
# 如果文件不存在，会自动在当前目录创建
doubandatabase = sqlite3.connect('liuximing_emulation.db')
# 创建一个Cursor
cursor = doubandatabase.cursor()
# 创建一个数据库表
dbtablecreate()
login('https://www.zhihu.com/#signin', 'https://www.zhihu.com/people/liu-xi-ming-5/activities')
# 关闭Cursor
cursor.close()
# 提交事务
doubandatabase.commit()
# 关闭Connection
doubandatabase.close()