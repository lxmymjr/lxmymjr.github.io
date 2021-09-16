# coding=utf-8
import os
from zhihu_oauth import ZhihuClient, ActType
import datetime
# 导入SQLite库
import sqlite3

def LoginZhihuClient(token_name):
    TOKEN_FILE = 'liuximing.pkl'
    client = ZhihuClient()
    if os.path.isfile(TOKEN_FILE):
        client.load_token(TOKEN_FILE)
    else:
        client.login_in_terminal()
        client.save_token(TOKEN_FILE)
    me = client.me()
    return me

def getdata(me):
    for act in me.activities:
        if act.type == ActType.VOTEUP_ANSWER:
            answer_id = act.target.id
            vote_time = datetime.datetime.fromtimestamp(act.created_time).strftime('%Y-%m-%d %H:%M:%S')
            answer_created_time = datetime.datetime.fromtimestamp(act.target.created_time).strftime('%Y-%m-%d %H:%M:%S')
            answer_updated_time = datetime.datetime.fromtimestamp(act.target.updated_time).strftime('%Y-%m-%d %H:%M:%S')
            thanks_count = act.target.thanks_count
            voteup_count = act.target.voteup_count
            answer_count = act.target.question.answer_count
            question_created_time = datetime.datetime.fromtimestamp(act.target.question.created_time).strftime('%Y-%m-%d %H:%M:%S')
            question_id = act.target.question.id
            title = act.target.question.title
            author = act.target.author.name
            topics = ''
            for i in act.target.question.topics:
                topics += i.name + ','
            topics = topics.strip(',')
            answerinsertorupdate(answer_id, vote_time, answer_created_time, answer_updated_time, thanks_count, voteup_count, answer_count, question_created_time, question_id, title, author, topics)
        elif act.type == ActType.VOTEUP_ARTICLE:
            article_id = act.target.id
            vote_time = datetime.datetime.fromtimestamp(act.created_time).strftime('%Y-%m-%d %H:%M:%S')
            created_time = datetime.datetime.fromtimestamp(act.target.created_time).strftime('%Y-%m-%d %H:%M:%S')
            updated_time = datetime.datetime.fromtimestamp(act.target.updated_time).strftime('%Y-%m-%d %H:%M:%S')
            voteup_count = act.target.voteup_count
            title = act.target.title
            author = act.target.author.name
            articleinsertorupdate(article_id, vote_time, created_time, updated_time, voteup_count, title, author)
        else:
            print act.type

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
doubandatabase = sqlite3.connect('liuximing_api.db')
# 创建一个Cursor
cursor = doubandatabase.cursor()
# 创建一个数据库表
dbtablecreate()
me = LoginZhihuClient('liuximing.pkl')
getdata(me)
# 关闭Cursor
cursor.close()
# 提交事务
doubandatabase.commit()
# 关闭Connection
doubandatabase.close()