# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ScrapyDoubanItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class ScrapyDbtop250Item(scrapy.Item):
    # 定义以下变量
    # define the fields for your item here like:
    # name = scrapy.Field()
    # 排名
    ord = scrapy.Field()
    # 电影名称
    name = scrapy.Field()
    # 导演
    director = scrapy.Field()
    # 编剧
    scriptwriters = scrapy.Field()
    # 主演
    star = scrapy.Field()
    # 类型
    type = scrapy.Field()
    # 地区
    region = scrapy.Field()
    # 语言
    language = scrapy.Field()
    # 上映时间
    releaseDate = scrapy.Field()
    # 片长
    length = scrapy.Field()
    # 简介
    synopsis = scrapy.Field()
    # 图片地址
    img = scrapy.Field()