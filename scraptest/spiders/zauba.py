#!/usr/bin/env python

import scrapy
from scrapy.spiders import CrawlSpider
from scrapy.http import FormRequest
from scrapy.http.request import Request
from loginform import fill_login_form
import logging
import math

logger = logging.getLogger('Zauba')

class zauba(CrawlSpider):
    name = 'Zauba'
    login_url = 'https://www.zauba.com/user'
    login_user = 'scrapybot1@gmail.com'
    login_password = 'scrapybot1'
    logger.info('zauba')
    start_urls = ['https://www.zauba.com/import-gold/p-1-hs-code.html']

    def start_requests(self):
        logger.info('start_request')
        # let's start by sending a first request to login page
        yield scrapy.Request(self.login_url, callback = self.parse_login)

    def parse_login(self, response):
        logger.warning('parse_login')
        # got the login page, let's fill the login form...
        data, url, method = fill_login_form(response.url, response.body,
                                            self.login_user, self.login_password)

        # ... and send a request with our login data
        return FormRequest(url, formdata=dict(data),
                           method=method, callback=self.start_crawl)

    def start_crawl(self, response):
        logger.warning('start_crawl')
        # OK, we're in, let's start crawling the protected pages
        for url in self.start_urls:
            yield scrapy.Request(url, callback=self.parse)

    def parse(self, response):
        logger.info('parse')
        text = response.xpath('//div[@id="block-system-main"]/div[@class="content"]/div[@style="width:920px; margin-bottom:12px;"]/span/text()').extract_first()
        total_entries = int(text.split()[0].replace(',', ''))
        total_pages = int(math.ceil((total_entries*1.0)/30))
        logger.warning('***************    :   %d' % total_pages)
        print('***************    :   %d' % total_pages)
        for page in xrange(1, (total_pages + 1)):
            url = 'https://www.zauba.com/import-gold/p-' + str(page) +'-hs-code.html'
            logger.debug('url%d  :  %s' % (page,url))
            yield scrapy.Request(url, callback=self.extract_entries)


    def extract_entries(self, response):
        logger.warning('extract_entries')
        row_trs = response.xpath('//div[@id="block-system-main"]/div[@class="content"]/div/table/tr')
        for row_tr in row_trs[1:]:
            row_content = row_tr.xpath('.//td/text()').extract()
            if (row_content.__len__() == 9):
                print row_content
                yield {
                    'date' : row_content[0].replace(' ', ''),
                    'hs_code' : int(row_content[1]),
                    'description' : row_content[2],
                    'origin_country' : row_content[3],
                    'port_of_discharge' : row_content[4],
                    'unit' : row_content[5],
                    'quantity' : int(row_content[6].replace(',', '')),
                    'value_inr' : int(row_content[7].replace(',', '')),
                    'per_unit_inr' : int(row_content[8].replace(',', '')),
                }
