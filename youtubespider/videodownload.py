#!/usr/bin/python3
# coding:utf8

import pymysql
import datetime
import youtube_dl
import json
import time
# 打开数据库连dic = json.dumps(duck)接



class VdieoDownload(object):
    """download videos """

    def __init__(self,db):
        self.db=db
        self.url = ''
        self.title = ''
        self.cursor = self.db.cursor()
        self.videojson = {}
        self.play_count = ''
        self.keywords = ''
        self.info = ''
        self.upload_time =''
        self.video_time=''
    def translation(self,instring):
        '''去掉数据中的空格换行等字符'''
        move = dict.fromkeys((ord(c) for c in u"\xa0\n\t"))
        outstring = instring.translate(move)
        return outstring
    def _Query(self,time):
        # 使用cursor()方法获取操作游标

        # SQL 查询语句 每次取出一条
        sql = "select title,url,play_count,keywords,info,upload_time,spider_time,video_time,site_name,video_category,tags,task_id" \
              " from videoitems " \
              "where isdownload =0 and video_time <%d limit 0,1 " %time
        print(time)
        print(sql)
        try:
            self.cursor.execute(sql)
            # 获取所有记录列表
            results = self.cursor.fetchall()
            for row in results:
                    self.title = row[0]
                    self.url = row[1]
                    self.play_count= row[2]
                    self.keywords=self.keywords+row[3]
                    self.info = row[4]
                    self.upload_time = row[5]
                    self.spider_time =row[6]
                    self.video_time = row[7]
                    self.site_name = row[8]
                    self.video_category = row[9]
                    self.tags = row[10]
                    self.task_id = row[11]
                    print(row)
        except:
            print("Error: unable to fetch data")

    def UpdateStatus(self,num):
        # SQL 更新语句 更改isdownload的值
        sql = "UPDATE videoitems SET isdownload =%d WHERE url = '%s'" % (num,self.url)
        try:
            # 执行SQL语句
            self.cursor.execute(sql)
            # 提交到数据库执行
            self.db.commit()
        except:
            # 发生错误时回滚
            self.db.rollback()
    def Download(self):
        #下载视频
        self.dt = datetime.datetime.now().strftime("%Y-%m-%d")
        options = {}
        options['retries'] = 5
        # options['proxy'] = 'http://127.0.0.1:8118'
        options['outtmpl'] = self.keywords+"/"+self.dt+ "/"+self.title+'.%(ext)s'
        ydl = youtube_dl.YoutubeDL( options)

        with ydl:
            result = ydl.extract_info(
                url=self.url,
                download=True  # We can extract the info and download the video
            )
        if 'entries' in result:
            # Can be a playlist or a list of videos
            video = result['entries'][0]
        else:
            # Just a video
            video = result
        self.videojson["task_id"] = self.task_id
        self.videojson["title"] = self.title
        self.videojson["title_cn"]=''
        self.videojson["upload_time"] = self.upload_time
        self.videojson["spider_time"] = self.spider_time.strftime('%Y-%m-%d')
        self.videojson["url"] = self.url
        self.videojson["info"] = self.info
        self.videojson["info_cn"] =''
        self.videojson["site_name"] = self.site_name
        self.videojson["site_name_cn"] = self.site_name
        self.videojson["play_count"] = self.play_count
        self.videojson["section"] = self.video_category
        # list2 = ','.join(self.tags)
        # simplified_sentence = self.Traditional2Simplified(list2)
        # self.tags = simplified_sentence.split(',')
        if self.tags =="['']":
            self.videojson["keywords"] = []
        else:
            self.videojson["keywords"] = self.tags
        self.videojson["video_time"] = self.video_time
        # 生成关于视频的json文件
    def WriteJson(self):
        videojson = json.dumps(self.videojson,ensure_ascii=False)
        with open( self.keywords+"/"+self.dt+ "/"+self.videojson['title']+".json",'w',encoding='utf-8' ) as fq:
            fq.write(videojson)

    def AddVideoJson(self):
        # SQL 更新语句 更新视频的信息
        tags = json.dumps(self.videojson["tags"],ensure_ascii=False)
        info = json.dumps(self.videojson["info"], ensure_ascii=False)
        sql = "UPDATE videoitems SET upload_time = '%s',info='%s' ,play_count='%s',tags='%s'\
              WHERE url = '%s'"% \
              (self.videojson["upload_time"],info,self.videojson["play_count"],tags ,self.url)
        try:
            # 执行SQL语句
            self.cursor.execute(sql)
            # 提交到数据库执行
            self.db.commit()
        except EOFError as e:
            # 发生错误时回滚
            print(e)
            self.db.rollback()
    def Automatic_download(self,time):
        import threading
        l = threading.Lock()
        l.acquire()
        self._Query(time)
        self.UpdateStatus(num=1)
        if self.url !='':
            try:
                self.Download()
                self.WriteJson()
                # self.AddVideoJson()

                self.UpdateStatus(num=2)
            except Exception as e:
                print(e)
                print('下载失败')
                self.UpdateStatus(num=3)

        l.release()

    def Traditional2Simplified(sentence):
        '''
        将sentence中的繁体字转为简体字
        :param sentence: 待转换的句子
        :return: 将句子中繁体字转换为简体字之后的句子
        '''
        print(sentence)
        sentence = Converter('zh-hans').convert(sentence)
        return sentence


if __name__ == '__main__':
    db = pymysql.connect("localhost", "root", "root", "test",charset='utf8')
    d = VdieoDownload(db=db)
    d.Automatic_download()
    # 关闭数据库连接
    db.close()