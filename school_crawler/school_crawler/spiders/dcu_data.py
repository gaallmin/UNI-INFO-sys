import scrapy
from scrapy.crawler import CrawlerProcess
import asyncio

if isinstance(asyncio.get_event_loop(), asyncio.ProactorEventLoop):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

class ucdscrapy(scrapy.Spider):
    name = "dcu"
   
    def start_requests(self):
        url = 'https://www.dcu.ie/courses/postgraduate/school-computing/msc-computing-major-options'
        yield scrapy.Request(url=url, callback=self.response_parser)
    
    def response_parser(self, response):
        courses = {}
        current_course_name = None
        current_description = []

        self.logger.info("Parsing the response")
        for i in range(5, 42):
            course_name_xpath = f'//*[@id="collapse-prospectus-about"]//p[{i}]/strong/text()'
            desc_xpath = f'//*[@id="collapse-prospectus-about"]//p[{i}]/text()[2]'

            course_name = response.xpath(course_name_xpath).get()
            course_desc = response.xpath(desc_xpath).get()

            if course_name:  
                if current_course_name:
                    yield {
                        'Course Name': current_course_name,
                        'Description': " ".join(current_description).strip()
                    }
                current_course_name = course_name.strip()
                current_description = []  

            if course_desc and current_course_name: 
                current_description.append(course_desc.strip())

        if current_course_name:
            yield {
                'Course Name': current_course_name,
                'Description': " ".join(current_description).strip()
            }

if __name__ == "__main__":
    process = CrawlerProcess()
    process.crawl(ucdscrapy)
    process.start()
