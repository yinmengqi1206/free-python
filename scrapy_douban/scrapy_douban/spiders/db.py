import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy_douban.items import ScrapyDbtop250Item

class DbSpider(CrawlSpider):
    name = 'db'
    allowed_domains = ['movie.douban.com']
    start_urls = ['https://movie.douban.com/top250?start=0&filter=']
    rules = (
        Rule(LinkExtractor(allow=r'\?start=\d+&filter='), callback='parse_item',
             follow=True),
    )
    def parse_item(self, response):
        videos_a = response.xpath('//div[@class="hd"]/a/@href')
        for v_a in videos_a:
            url = v_a.extract()
            # 对链接发起访问
            yield scrapy.Request(url=str(url), callback=self.parse_second)
    # 去除空格与\n
    def dislodge_blank(self, src):
        price = [sy.strip() for sy in src if sy.strip() != '']
        return price
    def parse_second(self, response):
        # 排名
        ord = response.xpath('//div[@id="content"]/div[@class="top250"]/span[1]/text()').extract()[0]
        # # 电影名称
        name = response.xpath('//div[@id="content"]/h1/span')[0].xpath('./text()').extract()[0]
        if len(name) == 0:
            name = '无电影名'
        # 导演
        director = response.xpath('//div[@id="info"]/span')[0].xpath('./span[@class="attrs"]/a/text()').extract()[0]
        if len(director) == 0:
            director = '无导演'
        # 编剧
        try:
            response.xpath('//div[@id="info"]/span')[1].xpath('./span[@class="attrs"]/a/text()').extract()[0]
        except Exception:
            scriptwriters = '无编剧信息'
        else:
            scriptwriters = \
            response.xpath('//div[@id="info"]/span')[1].xpath('./span[@class="attrs"]/a/text()').extract()[0]
        # 主演
        star = '/'.join(response.xpath('//span[@class="actor"]//a/text()').extract())
        if len(star) == 0:
            star = '无主演'
        # 类型
        type = '/'.join(response.xpath('//div[@id="info"]/span[@property="v:genre"]/text()').extract())
        # 地区
        region = response.xpath('//span[contains(./text(), "制片国家/地区:")]/following::text()[1]').extract()[0]
        if len(region) == 0:
            region = '无地区'
        # 语言
        language = response.xpath('//span[contains(./text(), "语言:")]/following::text()[1]').extract()[0]
        if len(language) == 0:
            language = '无语言'
        # 上映时间
        releaseDate = self.dislodge_blank(
            src=response.xpath('//div[@id="info"]//span[@property="v:initialReleaseDate"]/@content').extract())[0]
        # 片上
        length = self.dislodge_blank(
            src=response.xpath('//div[@id="info"]//span[@property="v:runtime"]/@content').extract())[0] + "分钟"
        # 简介
        synopsis = ''.join(response.xpath('//div[@id="link-report"]/span/text()').extract()).replace(u'\u3000',
                                                                                                     u'').replace('\n',
                                                                                                                  '').replace(
            '\r', '').replace(" ", "").replace('"', "'")
        # 图片地址
        img = response.xpath('//div[@id="mainpic"]/a/img/@src').extract()[0]
        data = ScrapyDbtop250Item(ord=ord, name=name, director=director, scriptwriters=scriptwriters, star=star,
                                    type=type, region=region, language=language, releaseDate=releaseDate, length=length,
                                    synopsis=synopsis, img=img)
        yield data