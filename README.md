# youtubespider
this is a spider of youtube

## 一、目录结构

```
youtubespider
        │  README.md          # 本文件
        │  requirements.txt	    # 项目依赖包文件
        │  scrapy.cfg        	# 爬虫配置文件
        │      
        ├─web
        │   │  __init__.py
        │   │  abc.py       # ABCnews模块爬爬取规则
        │   │  youtube.py   # 关键词采集爬取规则
        │    
        └─youtubespider
            │  __init__.py
            │   langconv.py     # 繁体字转换为简体
            │   item.py         # 所爬去的字段
            │   middlewares.py 	# 中间件，设置代理、请求头等
            │   pipelines.py    # 管道文件：将爬取的数据清洗并存入数据库
            │   setting.py		# 常用的一些设置
            │   translate.py	# 翻译：将非中文字段翻译成中文，利用的是百度翻译接口，需要账号
            │   videodownload.py # 视频下载，生成视频json文件，里面可以设置下载代理
            │   zh_wiki.py       #  繁体字转换为简体依赖
    
```

## 二、前期准备
　设置数据库、创建数据表等在setting.py文件中
##### 1　安装依赖包
    pip install -r requirements.txt
    回车
##### 2　设置数据库连接地址
```python
DB_HOST = "127.0.0.1"
DB_PORT = 3306
DB_USER = "root"
DB_PWD = "root"
DB_NAME = "spiderkeeper1"
DB_CHARSET = "utf8"

```
##### 3　设置视频文件的下载地址
```python
VIDEOS_SAVE_DIR = 'cetc_data_producer/videos'

```
##### 4　在相应的数据库中创建videoitems数据表
```mysql
     CREATE TABLE `videoitems` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` varchar(500) NOT NULL,
  `url` varchar(100) NOT NULL,
  `keywords` varchar(100) NOT NULL,
  `tags` varchar(1000) DEFAULT NULL,
  `video_category` varchar(50) DEFAULT NULL,
  `upload_time` varchar(50) DEFAULT NULL,
  `spider_time` varchar(50) DEFAULT NULL,
  `info` text,
  `site_name` varchar(20) DEFAULT NULL,
  `video_time` int(11) DEFAULT NULL,
  `isdownload` int(11) DEFAULT NULL,
  `play_count` varchar(20) DEFAULT NULL,
  `task_id` varchar(20) DEFAULT NULL,
  `lg` varchar(45) DEFAULT NULL,
  `title_cn` varchar(500) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_videoitems_url` (`url`)
) ENGINE=InnoDB AUTO_INCREMENT=329 DEFAULT CHARSET=utf8;
   ```
## 三、运行启动

##### 1 切换到youtubespider/spiders目录下
    在控制台输入 scrapy crawl 爬虫名称
    回车

##### 2 修改需爬去的关键字　　youtube.py
    只需修改youtube.py文件下__init__函数中的值
   ```python
    def __init__(self, keywords='你好', video_time_long="1000", video_time_short="0", task_id=2,
                 startDate=int(time.time()) - 3600 * 48 *7, endDate=int(time.time()), *args, **kwargs):
        pass
```
    其中keywords是所要爬取的关键字，video_time_long是爬取视频的最大时长（秒），video_time_short是爬取视频的最大时长（秒），
    startDate是爬取视频最早的日期， endDate是爬取视频最晚的日期

