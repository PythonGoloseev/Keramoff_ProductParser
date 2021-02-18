
# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import sys

from scrapy.crawler import CrawlerProcess
from scrapy.utils.log import configure_logging

from Universal_scrapy_app.Universal_scrapy.spiders.Universal_Spider import Universal_Spider

sys.path.insert(0, "l:\\_Важное\\6 Работа\\Python\\PyCharm\\UNF_Project\\")
import UNF_SELENIUM
import UNF_STRING
import os


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.



# Press the green button in the gutter to run the script.
if False and __name__ == '__main__':
    #print_hi('PyCharm')

    # import logging
    #
    # logging.basicConfig(
    #     filename='log.txt',
    #     format='%(levelname)s: %(message)s',
    #     level=logging.WARNING
    #)
    #scrapy crawl Universal_spider --loglevel WARNING -a settings_file=settings_ledeme_ru.json
    #spider = Universal_Spider(settings_file="./Universal_scrapy_app/settings_ledeme_ru.json")
    # spider.logger.setLevel("WARNING")
    #spider.spider_opened()
    #runner = CrawlerRunner()
    # d = runner.crawl(spider)
    # d.addBoth(lambda _: reactor.stop())
    # reactor.run()  # the script will block here until the crawling is finished
    #configure_logging({'LOG_FORMAT': '%(levelname)s: %(message)s'})

    my_settings = {'LOG_LEVEL': 'WARNING'}
    configure_logging(my_settings)

    process = CrawlerProcess(my_settings)
    #process.crawl(Universal_Spider, settings_file="./Universal_scrapy_app/settings_centrsantehniki_com.json" )
    #process.crawl(Universal_Spider, settings_file="./Universal_scrapy_app/settings_fleksi_ru.json" )
    #process.crawl(Universal_Spider, settings_file="./Universal_scrapy_app/settings_hansgrohe_ru.json")
    #process.crawl(Universal_Spider, settings_file="./Universal_scrapy_app/settings_ledeme_ru.json")

    #Неудачная авторизация
    #process.crawl(Universal_Spider, settings_file="./Universal_scrapy_app/settings_SantehSmart_ru.json")

    #process.crawl(Universal_Spider, settings_file="./Universal_scrapy_app/settings_vogceramic_ru.json")
    #process.crawl(Universal_Spider, settings_file="./Universal_scrapy_app/settings_vogtrade_ru.json")

    process.crawl(Universal_Spider, settings_file="./Universal_scrapy_app/new_settings_santehnika_online_ru.json")
    # process.crawl(Universal_Spider, settings_file="./Universal_scrapy_app/new_settings_keramogranit_ru.json")
    # process.crawl(Universal_Spider, settings_file="./Universal_scrapy_app/new_settings_bestceramic_ru.json")
    # new_settings_keramogranit_ru
    # new_settings_bestceramic_ru



    process.start() # the script will block here until all crawling jobs are finished

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
