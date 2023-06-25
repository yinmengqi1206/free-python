# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class ScrapyDoubanPipeline:
    def process_item(self, item, spider):
        return item

class ScrapyDbtop25002Pipeline:
    # 加上这两个方法是为了避免文件重复的打开
    # 在爬虫文件开始的之前就执行的方法
    def open_spider(self, spider):
        self.fd = open('book.json', 'w', encoding='utf-8')
    # 将item就是yield后面的book对象
    def process_item(self, item, spider):
        self.fd.write(str(item))
        return item
    # 在爬虫文件执行完成后执行的方法
    def close_spider(self, spider):
        self.fd.close()
# 加载settings文件
from scrapy.utils.project import get_project_settings
import pymysql
class MysqlPipelines:
    # 开启链接
    def open_spider(self, spider):
        settings = get_project_settings()
        self.host = settings['DB_HOST']
        self.user = settings['DB_USER']
        self.port = settings['DB_PORT']
        self.passwrod = settings['DB_PASSWROD']
        self.name = settings['DB_NAME']
        self.charset = settings['DB_CHARSET']
        self.connect()
    def connect(self):
        self.conn = pymysql.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.passwrod,
            db=self.name,
            charset=self.charset
        )
        self.cursor = self.conn.cursor()
    # 执行sql语句
    def process_item(self, item, spider):
        # sql语句
        sql = 'insert into dbtop250(ord,name,director,scriptwriters,star,type,region,language,releaseDate,length,synopsis,img) ' \
              'values ("{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","{}");'.format(
            item["ord"], item["name"], item["director"], item["scriptwriters"], item["star"], item["type"],
            item["region"], item["language"], item["releaseDate"], item["length"], item["synopsis"], item["img"])
        print(sql)
        # 执行sql语句
        self.cursor.execute(sql)
        # 提交
        self.conn.commit()
    # 关闭连接
    def close_spider(self, spider):
        self.cursor.close()
        self.conn.close()
import os
import csv
# 导出csv
class ExcelPipelines:
    def __init__(self):
        # csv文件的位置,无需事先创建
        store_file = os.path.dirname(__file__) + '/spiders/csdn.csv'
        # 打开(创建)文件
        self.file = open(store_file, 'w')
        # csv写法
        self.writer = csv.writer(self.file, dialect="excel")
        self.writer.writerow(
            ["排名", "电影名称", "导演", "编剧", "主演", "类型", "地区", "语言", "上映时间", "片长", "简介",
             "图片地址"])
    def process_item(self, item, spider):
        self.writer = csv.writer(self.file, dialect="excel")
        line = [item['ord'].encode('utf8', 'ignore'), item['name'].encode('utf8', 'ignore'),
                item['director'].encode('utf8', 'ignore'), item['scriptwriters'].encode('utf8', 'ignore'),
                item['star'].encode('utf8', 'ignore'), item['type'].encode('utf8', 'ignore'),
                item['region'].encode('utf8', 'ignore'),
                item['language'].encode('utf8', 'ignore'),
                item['releaseDate'].encode('utf8', 'ignore'), item['length'].encode('utf8', 'ignore'),
                item['synopsis'].encode('utf8', 'ignore'), item['img'].encode('utf8', 'ignore')]
        self.writer.writerow(line)
        return item
    def spider_closed(self, spider):
        self.file.close()