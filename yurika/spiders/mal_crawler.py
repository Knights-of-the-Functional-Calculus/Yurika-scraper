# -*- coding: utf-8 -*-
import scrapy
from yurika.items import YurikaItem

class MalCrawlerSpider(scrapy.Spider):
	name = 'mal_crawler'
	allowed_domains = ['https://myanimelist.net']
	start_urls = ['https://myanimelist.net/']

	def parse(self, response):
		link = 'https://myanimelist.net/anime/'
		for i in range(1,10):
			yield scrapy.Request(url=link+str(i), callback=self.grab_data, dont_filter=True, meta={'id': i})

	def grab_data(self, response):
		item = YurikaItem()
		#TODO: add more properties
		item['_id'] = response.meta['id']
		item['title'] = response.css('.h1').xpath('./span/text()').extract()[0]
		yield item
