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
	max_request = 500
	anime_link = 'https://myanimelist.net/anime/'


	def __init__(self, *args, **kwargs):
		logger = logging.getLogger('scrapy')
		logger.setLevel(logging.DEBUG)
		super().__init__(*args, **kwargs)

	def parse(self, response):
		for i in range(1,17):
			request = scrapy.Request(url=MalCrawlerSpider.anime_link+str(i), 
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
		if response.meta['id']+16 <= MalCrawlerSpider.max_request:
			request = scrapy.Request(url=MalCrawlerSpider.anime_link+str(response.meta['id']+16), 
									callback=self.grab_data, 
									errback=self.handle_miss, 
									dont_filter=True, 
									meta={'id': response.meta['id']+16})
			request.meta['proxy'] = 'https://' + random.choice(MalCrawlerSpider.proxy_list)
			yield request

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
			elif failure.value.response.status == 404:
				if failure.value.response.meta['id']+16 <= MalCrawlerSpider.max_request:
					request = scrapy.Request(url=MalCrawlerSpider.anime_link+str(failure.value.response.meta['id']+16), 
											callback=self.grab_data, 
											errback=self.handle_miss, 
											dont_filter=True, 
											meta={'id': failure.value.response.meta['id']+16})
					request.meta['proxy'] = 'https://' + random.choice(MalCrawlerSpider.proxy_list)
					yield request

