# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import datetime

import pymysql
from scrapy.utils.project import get_project_settings

from youtubespider.videodownload import VdieoDownload


class Youtubespiderv2Pipeline(object):
    def process_item(self, item, spider):
        db = pymysql.connect("127.0.0.1", "root", "root", "test", charset='utf8')
        d = VdieoDownload(db=db)
        d.Automatic_download(time=item['limit_time'])
        # 关闭数据库连接
        db.close()
        return item

class MysqlPipeline(object):
    """存储到数据库中"""

    def __init__(self):
        settings = get_project_settings()
        self.host = settings["DB_HOST"]
        self.port = settings["DB_PORT"]
        self.user = settings["DB_USER"]
        self.pwd = settings["DB_PWD"]
        self.name = settings["DB_NAME"]
        self.charset = settings["DB_CHARSET"]

        self.connect()

    def connect(self):
        self.conn = pymysql.connect(host = self.host,
                                    port = self.port,
                                    user = self.user,
                                    password = self.pwd,
                                    db = self.name,
                                    charset = self.charset)
        self.cursor = self.conn.cursor()


    def colose_spider(self,spider):
        self.conn.close()
        self.cursor.close()
    def process_item(self,item,spider):

        # 查重处理
        self.cursor.execute(
                """select * from videoitems where url = %s""",
                item['url'])
        # 是否有重复数据
        repetition = self.cursor.fetchall()

        # 重复
        if repetition:
                print(repetition)
                print("此条重复抓取，没有存入数据库")
        else:
            dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            sql = 'insert into videoitems(title,keywords,spider_time,url,site_name,video_time,play_count,upload_time,info,video_category,tags,task_id)' \
                  ' values( "%s","%s","%s","%s", "%s" ,"%s","%s", "%s", "%s","%s","%s","%s")' \
                  %(item['title'],item['keywords'],dt,item['url'],item['site_name'],item['video_time'],item["play_count"],item['upload_time'],item['info'],
                    item['video_category'],item['tags'],item['task_id'],)
            #执行SQL语句
            self.cursor.execute(sql)
            self.conn.commit()


        return item
