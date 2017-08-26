# -*- coding: utf-8 -*-
import scrapy
from yurika.items import YurikaItem
import random

class MalCrawlerSpider(scrapy.Spider):
	name = 'mal_crawler'
	allowed_domains = ['https://myanimelist.net']
	start_urls = ['https://myanimelist.net/']
	proxy_list = ['180.183.80.120:8081','78.85.32.217:53281','91.233.46.120:65309','188.27.85.65:53281']

	def parse(self, response):
		link = 'https://myanimelist.net/anime/'
		for i in range(1,10):
			request = scrapy.Request(url=link+str(i), callback=self.grab_data, dont_filter=True, meta={'id': i})
			request.meta['proxy'] = 'https://' + random.choice(MalCrawlerSpider.proxy_list)
			yield request

	def grab_data(self, response):
		item = YurikaItem()
		#TODO: add more properties
		item['_id'] = response.meta['id']
		item['title'] = response.css('.h1').xpath('./span/text()').extract()[0]
		yield item
