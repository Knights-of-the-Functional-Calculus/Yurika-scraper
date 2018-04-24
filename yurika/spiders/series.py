# -*- coding: utf-8 -*-
import scrapy
from yurika.items import SeriesItem
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError
from twisted.internet.error import TimeoutError
from twisted.internet.error import TCPTimedOutError
import random
import logging

class SeriesSpider(scrapy.Spider):
	name = "series"
	allowed_domains = ["anilist.co/anime"]
	start_urls = ['http://anilist.co/anime/']

	max_series = 500
	anime_link = 'https://anilist.co/anime/'
	requests = []

	def __init__(self, *args, **kwargs):
		logger = logging.getLogger('scrapy')
		logger.setLevel(logging.INFO)
		super().__init__(*args, **kwargs)
		self.generate_requests()

	def parse(self, response):
		for i in range(1,17):
			yield MalCrawlerSpider.requests.pop()

	def generate_requests(self):
		if not MalCrawlerSpider.requests:
			for i in range(1,MalCrawlerSpider.max_series):
				request = scrapy.Request(url=MalCrawlerSpider.anime_link+str(i), 
										callback=self.grab_data, 
										errback=self.handle_miss, 
										dont_filter=True, 
										meta={'id': i})
				request.meta['proxy'] = 'https://' + random.choice(MalCrawlerSpider.proxy_list)
				MalCrawlerSpider.requests.append(request)

	def grab_data(self, response):
		item = Series()
		#TODO: add more properties
		item['_id'] = response.meta['id']
		item['title'] = response.css('.h1').xpath('./span/text()').extract()[0]
		yield item
		if MalCrawlerSpider.requests:
			yield MalCrawlerSpider.requests.pop()

	def handle_miss(self, failure):
		logger = logging.getLogger('scrapy')
		if failure.check(HttpError):
			#logger.error(failure.value.response.status)
			if failure.value.response.status == 429:
				logger.info("Retrying entry..." + failure.value.response.url)
				request = scrapy.Request(url=failure.value.response.url,
									callback=self.grab_data, 
									errback=self.handle_miss, 
									dont_filter=True, 
									meta={'id': failure.value.response.meta['id']})
				request.meta['proxy'] = 'https://' + random.choice(MalCrawlerSpider.proxy_list)
				yield request
			elif failure.value.response.status == 404:
				pass
		elif failure.check(TCPTimedOutError,TimeoutError):
			logger.error("Check connectivity.")

	def spider_closed(self, spider):
		pass