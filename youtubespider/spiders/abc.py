# -*- coding: utf-8 -*-
import json

import re
import stat

import scrapy
import time

from youtubespider.items import Youtubespiderv2Item
from youtubespider.langconv import Converter


class AbcSpider(scrapy.Spider):
    name = '美国广播公司'

    def __init__(self, keywords='ABCnews',video_time_long=1000, video_time_short=0, task_id=2,
                 startDate=int(time.time()) - 3600 * 48, endDate=int(time.time()), *args, **kwargs):
        super(AbcSpider, self).__init__(*args, **kwargs)
        self.keywords = keywords
        self.task_id = task_id
        self.video_time_long = video_time_long
        self.video_time_short = video_time_short
        self.upload_time_start_date = startDate
        self.upload_time_end_date = endDate

        self.page = 1
        self.allowed_domains = ['www.youtube.com']
        self.start_urls = ['https://www.youtube.com/user/' + self.keywords + '/videos?pbj=1']

    def parse(self, response):
        item = Youtubespiderv2Item()
        item['video_time_long'] = self.video_time_long
        item['video_time_short'] = self.video_time_short
        if self.page == 1:
            obj = json.loads(response.text)[1]['response']['contents']['twoColumnBrowseResultsRenderer']['tabs'][1][
                'tabRenderer'] \
                ['content']['sectionListRenderer']['contents'][0]['itemSectionRenderer']['contents'][0] \
                ['gridRenderer']
            items = obj['items']
            continuations = obj['continuations'][0]['nextContinuationData']
            ctoken = continuations['continuation']
            continuation = continuations['continuation']
            itct = continuations['clickTrackingParams']
            next_page = 'https://www.youtube.com/browse_ajax?' + 'ctoken=' + ctoken + '&continuation=' + continuation + '&itct=' + itct
            for video_list in items:
                videoId = video_list['gridVideoRenderer']['videoId']

                item['url'] = 'https://www.youtube.com/watch?v=' + videoId + '&pbj=1'  # 视频url
                item['site_name'] = 'youtube'
                item['keywords'] = self.keywords
                item['task_id'] = self.task_id

                yield scrapy.Request(url=item['url'], callback=self.parse_info, meta={'item': item})
            self.page += 1
        else:
            obj = json.loads(response.text)[1]['response']['continuationContents']['gridContinuation']
            items = obj['items']
            continuations = obj['continuations'][0]['nextContinuationData']
            ctoken = continuations['continuation']
            continuation = continuations['continuation']
            itct = continuations['clickTrackingParams']
            next_page = 'https://www.youtube.com/browse_ajax?' + 'ctoken=' + ctoken + '&continuation=' + continuation + '&itct=' + itct
            for video_list in items:
                videoId = video_list['gridVideoRenderer']['videoId']

                item['url'] = 'https://www.youtube.com/watch?v=' + videoId + '&pbj=1'  # 视频url
                item['site_name'] = 'youtube'
                item['keywords'] = self.keywords
                item['task_id'] = self.task_id

                yield scrapy.Request(url=item['url'], callback=self.parse_info, meta={'item': item})
            self.page += 1
        if self.page <= 3:
            yield scrapy.Request(url=next_page, callback=self.parse)

    def parse_info(self, response):
        # 获取传过来的参数
        item = response.meta['item']
        item['start_date'] = self.upload_time_start_date
        item['end_date'] = self.upload_time_end_date

        obj = json.loads(response.text)[3]['playerResponse']['videoDetails']
        item['url'] = 'https://www.youtube.com/watch?v=' + obj['videoId']

        item['title'] = self.translation(obj['title']).strip()  # 视频标题
        item['title'] = self.Traditional2Simplified(item['title'])

        item['video_time'] = int(obj['lengthSeconds'])  # 视频时长，以秒为单位

        item['tags'] = obj.get('keywords', '')  # 视频的标签
        list2 = ','.join(item['tags'])
        simplified_sentence = self.Traditional2Simplified(list2)
        tags = simplified_sentence.split(',')
        if tags == ['']:
            item['tags'] = []
        item['tags'] = tags

        item['info'] = obj.get('shortDescription', '')  # 视频内容介绍
        item['info'] = self.Traditional2Simplified(item['info'])

        item['video_category'] = \
        json.loads(response.text)[3]['response']['contents']['twoColumnWatchNextResults']['results']['results'] \
            ['contents'][1]['videoSecondaryInfoRenderer']['metadataRowContainer']['metadataRowContainerRenderer'] \
            ['rows'][0]['metadataRowRenderer']['contents'][0]['runs'][0]['text']  # 视频的分类

        item['upload_time'] = \
        json.loads(response.text)[3]['response']['contents']['twoColumnWatchNextResults']['results']['results'] \
            ['contents'][1]['videoSecondaryInfoRenderer']['dateText']['simpleText'][0:-1]  # 视频上传时间，精确到天
        item['upload_time'] = self.dts2ts(
            re.search(r"(\d{4}年\d{1,2}月\d{1,2}日)", item['upload_time']).group(0))  # 利用正则表达式将日期准确提取出来

        item['play_count'] = obj.get('viewCount', '')  # 视频的点击量

        yield item

    def translation(self, instring):
        """
        去掉数据中的空格换行等字符
        :param instring:
        :return:
        """
        move = dict.fromkeys((ord(c) for c in u"\xa0\n\t|│:：<>？?\\/*’‘“”\""))
        outstring = instring.translate(move)
        # outstring=Converter('zh-hans').convert(outstring)
        return outstring

    def Traditional2Simplified(self, s):
        """
        将sentence中的繁体字转为简体字
        :param sentence: 待转换的句子
        :return: 将句子中繁体字转换为简体字之后的句子
        """
        s = Converter('zh-hans').convert(s)
        return s

    def dts2ts(self, datestr):
        """
        datestring translate to timestamp
        :param datestr:
        :return:
        """
        timeArray = time.strptime(datestr, "%Y年%m月%d日")
        timeStamp = int(time.mktime(timeArray))
        return timeStamp

    def close(self, spider):
        # 当爬虫退出的时候 关闭chrome
        import datetime
        import os
        from scrapy.utils.project import get_project_settings

        dt = datetime.datetime.now().strftime("%Y-%m-%d")
        settings = get_project_settings()
        videos_save_dir = settings['VIDEOS_SAVE_DIR']
        path = os.getcwd()  # 获取当前路径
        count = 0
        sizes = 0
        for root, dirs, files in os.walk(path + "/" + videos_save_dir + "/" + self.keywords.replace(' ', '_') + "/" + dt):  # 遍历统计
            for each in files:
                size = os.path.getsize(os.path.join(root, each))  # 获取文件大小
                os.chmod(os.path.join(root, each), stat.S_IRWXO + stat.S_IRWXG + stat.S_IRWXU)
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
        with open(videos_save_dir + '/' + self.keywords.replace(' ', '_') + "/" + dt + "/" + "task_info.json",
                  'w', encoding='utf-8') as fq:
            fq.write(videojson)
        os.chmod(videos_save_dir + '/' + self.keywords.replace(' ', '_') + "/" + dt + "/" + "task_info.json",
                 stat.S_IRWXO + stat.S_IRWXG + stat.S_IRWXU)
        os.chmod(videos_save_dir + '/' + self.keywords.replace(' ', '_') + "/" + dt,
                 stat.S_IRWXO + stat.S_IRWXG + stat.S_IRWXU)
        os.chmod(videos_save_dir + '/' + self.keywords.replace(' ', '_'),
                 stat.S_IRWXO + stat.S_IRWXG + stat.S_IRWXU)
        os.chmod(videos_save_dir,
                 stat.S_IRWXO + stat.S_IRWXG + stat.S_IRWXU)
        print("spider closed")
