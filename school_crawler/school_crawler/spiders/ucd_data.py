from typing import Iterable
import scrapy
import asyncio
from asyncio import SelectorEventLoop

if isinstance(asyncio.get_event_loop(), asyncio.ProactorEventLoop):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


class SchoolSpider(scrapy.Spider):
    name="school_crawler"
    # start_urls = [
    #     "https://hub.ucd.ie/usis/!W_HU_MENU.P_PUBLISH?p_tag=PROG&MAJR=T306#nav-T306", # ucd data comp
    #     "https://hub.ucd.ie/usis/!W_HU_MENU.P_PUBLISH?p_tag=PROG&MAJR=T195", #ucd comsci
    #     "https://hub.ucd.ie/usis/!W_HU_MENU.P_PUBLISH?p_tag=PROG&MAJR=B746" #ucd financial datasci
    # ]
    base_url = 'https://hub.ucd.ie/usis/!W_HU_MENU.P_PUBLISH?p_tag=PROG&MAJR='
    programs = {
        'T306': '//*[@id="nav-T306-tab"]/text()',
        'T195': '//*[@id="nav-T195-tab"]/text()',
        'B746': '//*[@id="nav-B746-tab"]/text()',
        'T150': '//*[@id="nav-T150-tab"]/text()',
        'W564': '//*[@id="nav-W564-tab"]/text()'
    }

    def start_requests(self):
        for program, xpath in self.programs.items():
            url = f"{self.base_url}{program}"
            yield scrapy.Request(url=url, callback=self.parse_program, meta={'program': program, 'xpath': xpath})
    
    def parse_program(self,response):
        program = response.meta['program']
        xpath = response.meta['xpath']
        program_name = response.xpath(xpath).get()
        if program_name:
            program_name = program_name.strip()
        
        introduction_p1 = response.xpath('//*[@id="h639628"]/div/div/div/div[2]/div/p[1]/text()[1]').get()
        introduction_p2 = response.xpath('//*[@id="h639628"]/div/div/div/div[2]/div/p[1]/text()[2]').get()
        introduction_p3 = response.xpath('//*[@id="h639628"]/div/div/div/div[2]/div/p[1]/text()[3]').get()

        introduction = ''
        if introduction_p1:
            introduction += introduction_p1.strip()
        if introduction_p2:
            introduction += introduction_p2.strip()
        if introduction_p3:
            introduction += introduction_p3.strip()
        
        highlights = response.xpath('//*[@id="h639628"]/div/div/div/div[2]/div/ul[1]/li/text()').getall()
        highlight = ' '.join([item.strip() for item in highlights])

        what_learns = response.xpath('//*[@id="collapseCB425-081"]/div/ul/li/text()').getall()
        what_learn = ' '.join([item.strip() for item in what_learns])
        
        modules = response.xpath('//*[starts-with(@id, "CB425-210")]/td[2]/a/text()').getall()
        module = ' '.join([item.strip() for item in modules])

        
        
        yield{
            'School':'UCD',
            'program_name': program_name,
            'introduction': introduction.strip(),
            'highlight' : highlight,
            'module' : module,
            'transcripts_required': 'A copy of all relevant transcripts from previous degrees/courses taken',
            'references_required': '2 academic references on headed university paper. If not possible, 1 academic and 1 professional reference',
            'english_certification_required': 'A copy of English language certification (if applicable)',
            'additional_documents': 'Additional supporting documentation such as personal statements or curriculum vitae can be included'
    
        }