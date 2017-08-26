# -*- coding: utf-8 -*-
import scrapy
from yurika.items import YurikaItem
from scrapy.spidermiddlewares.httperror import HttpError
import random
import logging

class MalCrawlerSpider(scrapy.Spider):
	name = 'mal_crawler'
	allowed_domains = ['https://myanimelist.net']
	start_urls = ['https://myanimelist.net/']
	with open('yurika/proxy_list.txt','r') as f:
		proxy_list = [l.strip() for l in f.readlines()]
	missed_urls = []

	def __init__(self, *args, **kwargs):
		logger = logging.getLogger('scrapy')
		logger.setLevel(logging.INFO)
		super().__init__(*args, **kwargs)

	def parse(self, response):
		link = 'https://myanimelist.net/anime/'
		for i in range(1,500):
			request = scrapy.Request(url=link+str(i), 
									callback=self.grab_data, 
									errback=self.handle_miss, 
									dont_filter=True, 
									meta={'id': i})
			request.meta['proxy'] = 'https://' + random.choice(MalCrawlerSpider.proxy_list)
			yield request

	def grab_data(self, response):
	
		item = YurikaItem()
		#TODO: add more properties
		item['_id'] = response.meta['id']
		item['title'] = response.css('.h1').xpath('./span/text()').extract()[0]
		yield item

	def handle_miss(self, failure):
		if failure.check(HttpError):
			if failure.value.response.status == 429:
				logger = logging.getLogger('scrapy')
				logger.info("Retrying entry..." + failure.value.response.url)
				yield scrapy.Request(url=failure.value.response.url,
									callback=self.grab_data, 
									errback=self.handle_miss, 
									dont_filter=True, 
									meta={'id': failure.value.response.meta['id']})

