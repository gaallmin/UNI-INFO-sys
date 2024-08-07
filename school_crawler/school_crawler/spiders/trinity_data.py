from typing import Iterable
import scrapy
from scrapy.crawler import CrawlerProcess
import asyncio
from asyncio import SelectorEventLoop

if isinstance(asyncio.get_event_loop(), asyncio.ProactorEventLoop):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

class trinityscrapy(scrapy.Spider):
    name = "trinity"
    custom_settings = {
        'DUPEFILTER_CLASS': 'scrapy.dupefilters.BaseDupeFilter'
    }
    base_url = 'https://www.tcd.ie/scss/courses/postgraduate/computer-science/'
    programs =[
        'data-science',
        'intelligent-systems'
    ]

    def start_requests(self):
        for program in self.programs:
            url = f"{self.base_url}{program}/"
            yield scrapy.Request(url=url, callback=self.parse_program, meta={'program':program})

    def parse_program(self, response):
        program = response.meta['program']
        program_name = response.xpath('//*[@id="main"]/div[3]/div/div/div[1]/div[1]/div/p').get()

        introductions = response.xpath('//*[@id="main"]/div[3]/div/div/div[1]/div[1]/p/text()').getall()
        introduction = ' '.join([item.strip() for item in introductions])

        module_pg = response.xpath('//a[contains(@href, "teaching.scss.tcd.ie")]/@href').get()
        if module_pg:
            yield scrapy.Request(url=module_pg, callback=self.parse_modules, meta={
                'program_name':program_name,
                'introduction': introduction,
                'program' : program
            })
        
        else:
            yield {
                'School': 'Trinity',
                'program_name': program_name,
                'introduction': introduction,
                'modules': None
            }

    def parse_modules(self, response):
        program_name = response.meta['program_name']
        introduction = response.meta['introduction']
        program = response.meta['program']

        modules = []

        if program == 'intelligence-systems':
            modules = response.xpath('//*[@id="wpsp-899"]/article/div/header/h4/a').getall()
        elif program == 'data-science':
            modules = response.xpath('//*[@id="wpsp-871"]/article/div/header/h4/a').getall()
        
        module_list = ' '.join([item.strip() for item in modules])

        yield {
        'School': 'Trinity',
        'program_name': program_name,
        'introduction': introduction,
        'modules': module_list
        }

if __name__ == "__main__":
    process = CrawlerProcess()
    process.crawl(trinityscrapy)
    process.start()
