# -*- coding: utf-8 -*-
import json

import re
import scrapy
import time

from youtubespider.items import Youtubespiderv2Item
from youtubespider.langconv import Converter


class YoutubeSpider(scrapy.Spider):
    name = 'youtube'
    def __init__(self,keywords = '金正恩',limit=800,taskId = 2,startDate=int(time.time())-3600*48,endDate=int(time.time()),*args,**kwargs):
        super(YoutubeSpider, self).__init__(*args, **kwargs)
        self.keywords = keywords
        self.task_id = taskId
        self.limit_time =int(limit)
        self.start_date = startDate
        self.end_date = endDate
        self.allowed_domains = ['www.youtube.com']
        self.url1 = 'http://www.youtube.com/results?sp=EgIIBA%253D%253D&search_query='+self.keywords+'&pbj=1&page='
        self.page = 1
        self.start_urls = [self.url1+'1']
    def parse(self, response):
        '''抽取相关的采集数据'''

        item = Youtubespiderv2Item()
        item['limit_time']=self.limit_time
        obj = json.loads(response.text)[1]['response']['contents']['twoColumnSearchResultsRenderer']['primaryContents']
        videoRenderers = obj['sectionListRenderer']['contents'][0]['itemSectionRenderer']['contents']
        print(len(videoRenderers))
        # exit()
        for videoRenderer in videoRenderers:         #视频列表
            video = videoRenderer.get('videoRenderer',False)
            if video:
                videoId = video.get('videoId','')   #视频id
                item['url'] = 'https://www.youtube.com/watch?v=' + videoId +'&pbj=1' #视频url
                print(item['url'] )
                item['site_name'] = 'youtube'
                item['keywords'] = self.keywords
                item['task_id'] =self.task_id

                yield scrapy.Request(url=item['url'], callback=self.parse_info, meta={'item': item})
        self.page += 1

        if self.page <= 10:
            print("开始爬去第%d页" % self.page)
            url = self.url1 + str(self.page)
            time.sleep(5)
            # 再次发送请求

            yield scrapy.Request(url=url, callback=self.parse)

    def parse_info(self, response):
        # 获取传过来的参数
        item = response.meta['item']
        item['start_date'] = self.start_date
        item['end_date'] = self.end_date
        obj = json.loads(response.text)[3]['playerResponse']['videoDetails']
        item['url'] = 'https://www.youtube.com/watch?v='+obj['videoId']

        item['title'] = self.translation(obj['title']).strip()  #视频标题
        item['title'] = self.Traditional2Simplified(item['title'])

        item['video_time'] =int(obj['lengthSeconds'] )      #视频时长，以秒为单位


        item['tags'] = obj.get('keywords','')          #视频的标签
        list2 = ','.join(item['tags'])
        simplified_sentence = self.Traditional2Simplified(list2)
        tags = simplified_sentence.split(',')
        print(tags)
        if tags==['']:
            item['tags'] = []
        item['tags'] = tags


        item['info'] = obj.get('shortDescription','') #视频内容介绍
        item['info'] = self.Traditional2Simplified(item['info'])


        item['video_category'] = json.loads(response.text)[3]['response']['contents']['twoColumnWatchNextResults']['results']['results']\
                                        ['contents'][1]['videoSecondaryInfoRenderer']['metadataRowContainer']['metadataRowContainerRenderer']\
                                        ['rows'][0]['metadataRowRenderer']['contents'][0]['runs'][0]['text']  #视频的分类

        item['upload_time'] = json.loads(response.text)[3]['response']['contents']['twoColumnWatchNextResults']['results']['results']\
                                        ['contents'][1]['videoSecondaryInfoRenderer']['dateText']['simpleText'][0:-1]  #视频上传时间，精确到天
        item['upload_time'] =  self.dts2ts(re.search(r"(\d{4}年\d{1,2}月\d{1,2}日)",item['upload_time']).group(0)) #利用正则表达式将日期准确提取出来
        item['play_count'] = obj.get('viewCount','')           #视频的点击量

        yield item


    def translation(self,instring):
        '''去掉数据中的空格换行等字符'''
        move = dict.fromkeys((ord(c) for c in u"\xa0\n\t|│:：<>？?\\/*’‘“”\""))
        outstring = instring.translate(move)
        # outstring=Converter('zh-hans').convert(outstring)
        return outstring


    def Traditional2Simplified(self,s):
        '''
        将sentence中的繁体字转为简体字
        :param sentence: 待转换的句子
        :return: 将句子中繁体字转换为简体字之后的句子
        '''
        s = Converter('zh-hans').convert(s)
        return s

    def dts2ts(self,datestr):
        '''datestring translate to timestamp'''

        timeArray = time.strptime(datestr, "%Y年%m月%d日")
        timeStamp = int(time.mktime(timeArray))
        return timeStamp

    def close(self, spider):
         # 当爬虫退出的时候 关闭chrome
         import datetime
         import os
         dt = datetime.datetime.now().strftime("%Y-%m-%d")

         path = os.getcwd()  # 获取当前路径
         count = 0
         sizes = 0
         for root, dirs, files in os.walk(path + "/" + self.keywords + "/" + dt):  # 遍历统计
             for each in files:
                 size = os.path.getsize(os.path.join(root, each))  # 获取文件大小
                 sizes += size
                 count += 1  # 统计文件夹下文件个数
         count = count // 2
         sizes = sizes / 1024.0 / 1024.0
         sizes = round(sizes, 2)
         videojson = {}
         videojson['title'] = self.keywords
         videojson['time'] = dt
         videojson['keywords'] = self.keywords
         videojson['file_number'] = count
         videojson['file_size'] = str(sizes) + 'M'
         dt = datetime.datetime.now().strftime("%Y-%m-%d")
         videojson = json.dumps(videojson, ensure_ascii=False)
         with open(self.keywords + "/" + dt + "/" + "task_info.json", 'w', encoding='utf-8') as fq:
             fq.write(videojson)
         print("spider closed")



