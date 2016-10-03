#!/usr/bin/env python

from scrapy.spider import CrawlSpider
from scrapy.http import FormRequest
from scrapy.http.request import Request
from loginform import fill_login_form
from scrapy import log
import logging

class zauba(CrawlSpider):
    name = 'Zauba'
    start_urls = ['https://www.zauba.com/import-gold/p-1-hs-code.html']
    login_user = 'scrapybot1@gmail.com'
    login_pass = 'scrapybot1'

def parse(self, response):
    (args, url, method) = fill_login_form(response.url,
            response.body, self.login_user, self.login_pass)
    logging.warning('sdkjvbhvbhk')
    return FormRequest(url, method=method, formdata=args,
                       callback=self.getPageNumber)

def getPageNumber(self, response):
    logging.warning('**************')
    text = response.xpath('//div[@id="block-system-main"]/div[@class="content"]/div[@style="width:920px; margin-bottom:12px;"]/span/text()').extract_first()
    total_entries = int(text.split()[0].replace(',', ''))
    total_pages = int(math.ceil((total_entries*1.0)/30))
    logging.warning('***************    :   ' + total_pages)
    print('***************    :   ' + total_pages)
    for page in xrange(1, (total_pages + 1)):
        url = 'https://www.zauba.com/import-gold/p-' + page +'-hs-code.html'
        log.msg('url%d  :  %s' % (pages,url))
        yield scrapy.Request(url, callback=self.extract_entries)

def extract_entries(self, response):
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
