# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class Youtubespiderv2Item(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    title = scrapy.Field()
    title_cn = scrapy.Field()
    keywords = scrapy.Field()
    tags = scrapy.Field()
    upload_time = scrapy.Field()
    url = scrapy.Field()
    info = scrapy.Field()
    site_name = scrapy.Field()
    video_time = scrapy.Field()
    play_count = scrapy.Field()
    video_category = scrapy.Field()
    video_time_long = scrapy.Field()
    video_time_short = scrapy.Field()
    task_id = scrapy.Field()
    start_date = scrapy.Field()
    end_date = scrapy.Field()
    language = scrapy.Field()
