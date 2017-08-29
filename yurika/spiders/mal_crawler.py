# -*- coding: utf-8 -*-
import scrapy
from yurika.items import YurikaItem
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError
from twisted.internet.error import TimeoutError
from twisted.internet.error import TCPTimedOutError
from scrapy.xlib.pydispatch import dispatcher
from scrapy import signals
from scrapy import Selector
import random
import logging

class MalCrawlerSpider(scrapy.Spider):
	name = 'mal_crawler'
	allowed_domains = ['https://myanimelist.net']
	start_urls = ['https://myanimelist.net/']
	with open('yurika/proxy_list.txt','r') as f:
		proxy_list = [l.strip() for l in f.readlines()]
	check_proxies = []
	max_series = 36000
	anime_link = 'https://myanimelist.net/anime/'
	requests = []


	def __init__(self, *args, **kwargs):
		logger = logging.getLogger('scrapy')
		logger.setLevel(logging.INFO)
		super().__init__(*args, **kwargs)
		dispatcher.connect(self.spider_closed, signals.spider_closed)
		self.generate_requests()

	def parse(self, response):
		for i in range(1,33):
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
		item = YurikaItem()
		#TODO: add more properties
		item['_id'] = response.meta['id']
		item['title'] = response.css('.h1').xpath('./span/text()').extract_first()
		i = 0
		objects = response.css('.js-scrollfix-bottom').css('.spaceit').extract()
		for o in objects:
			if "Episodes:" in o:
				break
			i+=1

		num_episodes = Selector(text=objects[i]).css('.spaceit') \
								.xpath('./text()').extract()[1].strip()
		item['num_episodes'] = int(num_episodes) if num_episodes.isdigit() else -1
		
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
				if MalCrawlerSpider.requests:
					yield MalCrawlerSpider.requests.pop()
			elif failure.value.response.status in [400, 405, 407, 500]:
			# 	if failure.request.meta['proxy'] in MalCrawlerSpider.proxy_list:
			# 		MalCrawlerSpider.proxy_list.remove(failure.request.meta['proxy'])
				logger.error(str(failure.value.response.status) + ": Check connectivity and that proxy " 
							+ failure.request.meta['proxy']
							+ " is up and not blocked. Failed to connect to: "
							+ failure.value.response.url)
			# 	MalCrawlerSpider.check_proxies.append(failure.request.meta['proxy'] + '\n')
			# 	request = scrapy.Request(url=failure.value.response.url,
			# 						callback=self.grab_data, 
			# 						errback=self.handle_miss, 
			# 						dont_filter=True, 
			# 						meta={'id': failure.value.response.meta['id']})
			# 	request.meta['proxy'] = 'https://' + random.choice(MalCrawlerSpider.proxy_list)
			# 	yield request
		elif failure.check(TCPTimedOutError,TimeoutError):
			if failure.request.meta['proxy'] in MalCrawlerSpider.proxy_list:
				MalCrawlerSpider.proxy_list.remove(failure.request.meta['proxy'])
			logger.error("TIME: Check connectivity and that proxy " 
						+ failure.request.meta['proxy']
						+ " is up and not blocked. Failed to connect to: "
						+ failure.value.response.url)
			MalCrawlerSpider.check_proxies.append(failure.request.meta['proxy'] + '\n')


	def spider_closed(self, spider):
		pass
		# with open('yurika/proxy_list.txt','w') as f:
		# 	for p in MalCrawlerSpider.proxy_list:
		# 		if not p in MalCrawlerSpider.check_proxies:
		# 			f.write(p)

