import json
from urllib.parse import urljoin
#подключим внение каталоги с модулями
import os
from sys import path as sys_path #im naming it as pylib so that we won't get confused between os.path and sys.path
sys_path += [os.path.abspath('../')] # подключаем каталог выше запущенного корневого скрипта scrapy на уровень
from _UNF import String as UNF_STR
import scrapy
from scrapy import signals
from _COMMON.spider_addition import Spider_addition
from _COMMON.spider_addition import Crawling_Page
from _UNF import OS as UNF_OS
from Universal_scrapy_app.Universal_scrapy.page_parsers.main_page_parser import Main_Page_Parser
from Universal_scrapy_app.Universal_scrapy.items import Catalog_item
from Universal_scrapy_app.Universal_scrapy.page_parsers.group_page_parser import Group_page_parser
import _UNF.URLs as UNF_URLs
import datetime
from scrapy.http import Request

from scrapy.http import FormRequest
from scrapy.utils.response import open_in_browser
from scrapy.utils.log import configure_logging

class Universal_Spider(scrapy.Spider, Spider_addition):
    name = 'Universal_spider'
    # allowed_domains = ['http://santehcentr.com']
    start_urls = ['http://site_from_settins.com/']
    output_catalog = "./_outputs"

    #разрешим возвращать страницы со статусом 404
    #handle_httpstatus_list = [404, ]

    # DOWNLOAD_HANDLERS = {
    #     'https': 'my.custom.downloader.handler.https.HttpsDownloaderIgnoreCNError',
    # }
    # DOWNLOAD_HANDLERS_BASE = {
    #     'file': 'scrapy.core.downloader.handlers.file.FileDownloadHandler',
    #     'http': 'scrapy.core.downloader.handlers.http.HttpDownloadHandler',
    #     'https': 'scrapy.core.downloader.handlers.http.HttpsDownloaderIgnoreCNError',
    #     's3': 'scrapy.core.downloader.handlers.s3.S3DownloadHandler',
    # }

    custom_settings = {
        'ROBOTSTXT_OBEY': False,
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:79.0) Gecko/20100101 Firefox/78.0',
        'FEEDS':{
            #'file:e:///Temp/_Spider/%(name)s_new_output.xml':
            'file:%(output_catalog)s/%(name)s_xml_data.xml':
                {
                'format': 'xml',
                # 'fields': ['name', 'price'],
                'encoding': 'utf8',
                'indent': 8,
                },
            # './_outputs/results/%(name)s_output.json':
            'file:%(output_catalog)s/%(name)s_json_data.json':                {
                'format': 'json',
                'encoding': 'utf8',
                'store_empty': False,
                # 'fields': None,
                'indent': 4,
                },
            }
        }


    # def login(self, response):
    #
    #     my_login_url = self.add_settings.login_url
    #     my_login = self.add_settings.login
    #     my_password = self.add_settings.password
    #
    #     UNF_STR.print_fuksi(f"   выполняю попытку авторизации my_login_url={my_login_url} login={my_login}   password={my_password}")
    #
    #     my_form_data = {'user': my_login, 'password': my_password,
    #                                         "authenticity_token": response.xpath(
    #                                             "//meta[@name='csrf-token']/@content").extract_first()}
    #
    #     result = scrapy.FormRequest(url=my_login_url, encoding="ascii",
    #                               headers={"X-Requested-With": "XMLHttpRequest"},
    #                               formdata=my_form_data,
    #                               callback=self.parse, dont_filter=True)
    #
    #     return  result

    # def start_requests(self):
    #
    #     if UNF_STR.is_empty(self.add_settings.login_url):
    #         UNF_STR.print_yellow("Авторизация на сайте не применяется")
    #     else:
    #         UNF_STR.print_fuksi("   выполняю попытку авторизации")
    #         pass
    #
    #
    #     result = FormRequest(
    #             self.add_settings.login_url,
    #             formdata={"Username": self.add_settings.login, "Password": self.add_settings.password}
    #         )
    #
    #     UNF_STR.print_fuksi(f"result type={type(result)}")
    #     return result

    #--------------------------------------------------------------------------------------------------------------------------
    #--------------------------------------------------------------------------------------------------------------------------
    #--------------------------------------------------------------------------------------------------------------------------
    def parse(self, response):
        self.uploaded_pages.append(Crawling_Page(response.url, "Main_page"))
        print(f"   - Начинаю сканирование ресурса: {response.url}")

        if self.add_settings.login_required and not self.success_autorization(response):
            self.RaiseErrorMessage("Не удачная попытка авторизации")
            return(None)

        self.debug_print(f"   - Скачал корневую страницу парсинга url={response.url}")

        if self.add_settings.need_to_save_pages:
             UNF_OS.Save_text_to_file("main_page_" + self.name + ".html", self.add_settings.get_saved_pages_path(), response.text)

        main_page_parser = Main_Page_Parser(self)
        main_page_parser.parse_info(response, self)
        self.catalogs_list = main_page_parser.catalogs
        self.debug_print(f"   (!) На главной странице перечень групп из {len(main_page_parser.catalogs)} элементов верхнего уровня")

        # lower_catalogs_array = self.recursively_get_lower_catalogs_to_array(main_page_parser.catalogs)

        lower_catalogs_dict = self.recursively_get_lower_catalogs_to_dict(main_page_parser.catalogs)

        if self.add_settings.need_to_save_pages:
            self.save_object_to_json_file("lower_catalogs_dict.json", lower_catalogs_dict)


        #self.debug_
        print(f"   - всего найдено  {len(lower_catalogs_dict)} уникальных ссыллок на группы нижнего уровня")

        #выгрузим иерархию в файл
        # catalog_item = self.export_catalog_to_output_files(catalogs_list)
        # yield catalog_item

        groups_limit = self.add_settings.stop_after_number_of_groups
        #запустим асинхронную загрузку групп

        for index, each_group_url in enumerate(lower_catalogs_dict):
            group_number = len(self.requested_groups_dict) + 1

            # проверим не превышено ли ограничение на количество загружаемых групп
            if  groups_limit != None and groups_limit > 0 and len(self.requested_groups_dict)>=groups_limit:
                UNF_STR.print_fuksi(f"   (!) Прекратил запрос остальных групп, потому как достиг ограничения количества загружаемых групп {groups_limit}")
                break

            domain_url = UNF_URLs.get_base_domain(response.url)
            products_page_fullurl = urljoin(domain_url + "/", each_group_url)
            cur_catalog = lower_catalogs_dict[each_group_url]



            if not UNF_STR.is_empty(self.add_settings.filter_groups_only_url) and \
                    cur_catalog.url != self.add_settings.filter_groups_only_url and products_page_fullurl != self.add_settings.filter_groups_only_url:
                    self.debug_print(f"      - пропускаю {products_page_fullurl} потому как она не совпала с фильтром {self.add_settings.filter_groups_only_url}")
                    self.cancelled_pages.append(products_page_fullurl)
                    continue

            #print(f"отправляю команду на открытие {index+1} группы нижнего уровня {cur_catalog.name}  url={cur_catalog.url}")

            self.debug_print(f"      - запускаю асинхронное чтение {group_number} страницы {cur_catalog.name}  url={products_page_fullurl}")

            self.requested_groups_dict[products_page_fullurl] = products_page_fullurl

            group_page_parser = Group_page_parser(self)
            new_response = response.follow(products_page_fullurl, callback=group_page_parser.async_group_upload)
            new_response.meta['current_group'] = cur_catalog
            new_response.meta['spider'] = self
            new_response.meta['its_pagination_follow'] = False
            yield new_response


    # --------------------------------------------------------------------------------------------------------------------------
    def recursively_get_lower_catalogs_to_dict(self, catalogs):

        result_dict = {}

        for catalog in catalogs:
            if len(catalog.slave_catalogs) == 0:
                result_dict[catalog.url] = catalog
                #print(f"********** добавил группу name = {catalog.name} url={catalog.url}")
            else:
                #print(f"********** провалился на уровень ниже из {catalog.name} url={catalog.url}")
                slave_dict = self.recursively_get_lower_catalogs_to_dict(catalog.slave_catalogs)

                for key in slave_dict:
                    result_dict[key] = slave_dict[key]


        return result_dict



    #--------------------------------------------------------------------------------------------------------------------------
    #--------------------------------------------------------------------------------------------------------------------------
    #--------------------------------------------------------------------------------------------------------------------------
    def spider_opened(self, spider):
        print(f"--------------------spider {self.name} opened-----------------------------")
        self.start_time = datetime.datetime.now()
        self.delete_summary_file()

    #--------------------------------------------------------------------------------------------------------------------------
    #--------------------------------------------------------------------------------------------------------------------------
    #--------------------------------------------------------------------------------------------------------------------------
    def spider_closed(self, spider):
        self.finish_time = datetime.datetime.now()
        self.duration = int((self.finish_time -self.start_time).total_seconds()/60)

        #сохраняю структуру групп в отдельный json
        self.debug_print(f"   - сохраняю итоговую структурe в каталог output")
        self.save_object_to_json_file("Group_Structure.json", self.catalogs_list)
        self.save_object_to_json_file(self.get_summary_file_name(), self.get_sprider_summary())


        print(f"-----------------------------CLOSED-----------------------------------------")
        UNF_STR.print_blue(f"ИТОГО: ПОТРАЧЕНО {self.duration} МИНУТ")

        self.show_cancelled_pages()
        self.show_uploaded_groups()
        self.show_uploaded_groups_paginations()
        self.show_uploaded_products()
        self.show_uploaded_images()
        self.show_errors()

        # result_message = f"В ИТОГЕ ЗАГРУЗИЛ {len(spider.uploaded_pages)} СТРАНИЦ ПРОПУСТИЛ {len(spider.cancelled_pages)} СТРАНИЦ И НАШЕЛ  {len(spider.uploaded_products)} товаров"
        # print(result_message)
        #
        # spider.logger.info('Spider closed: %s', spider.name)
        # spider.logger.info('result_message: %s', result_message)

    def show_cancelled_pages(self):
        if len(self.cancelled_pages)>0:
            UNF_STR.print_fuksi(f"ИТОГО (ВНИМАНИЕ!!!): ПРОПУЩЕНО {len(self.cancelled_pages)} ГРУПП ИЗ-ЗА ФИЛЬТА filter_groups_only_url={self.add_settings.filter_groups_only_url}")

    def show_errors(self):
        if len(self.error_messages)>0:

            UNF_STR.print_red(f"ЗАФИКСИРОВАНО {len(self.error_messages)} ОШИБОК")
            for index, each_error_message in enumerate(self.error_messages):
                if index>5:
                    print(f"  -и другие ... ")
                    break
                UNF_STR.print_red(f"  - в том числе ошибка: {each_error_message.text}")
        else:
            UNF_STR.print_green(f"ИТОГО: ОШИБОК НЕ ЗАФИКСИРОВАНО")

    def show_uploaded_groups(self):
        if len(self.requested_groups_dict)>len(self.uploaded_groups_dict):
            deviation = len(self.requested_groups_dict) - len(self.uploaded_groups_dict)
            UNF_STR.print_fuksi(f"ИТОГО: Загружены лишь {len(self.uploaded_groups_dict)} из {len(self.requested_groups_dict)} ПОТЕРЯНО ({deviation} шт) БЫЛИ ПРОПУЩЕНЫ :")
            number = 0
            for each_requested_group in enumerate(self.requested_groups_dict):
                if each_requested_group not in self.uploaded_groups_dict:
                    number += 1
                    if number >=5:
                        print(f"  -и другие ... ")
                        break
                    print(f"  - в том числе не загружена {number} группа  {each_requested_group}" )
        elif len(self.requested_groups_dict)<len(self.uploaded_groups_dict):
            deviation = len(self.requested_groups_dict) - len(self.uploaded_groups_dict)
            UNF_STR.print_red(f"ИТОГО: НОНСЕНС ЗАГРУЖЕНО {len(self.uploaded_groups_dict)} (НА {deviation} ГРУПП БОЛЬШЕ) ИЗ {len(self.uploaded_groups_dict)} ЗАПРОШЕНЫХ ")
        else:
            UNF_STR.print_green(f"ИТОГО: ЗАГРУЖЕНЫ ВСЕ {len(self.requested_groups_dict)} ГРУППЫ ТОВАРОВ")

    def show_uploaded_groups_paginations(self):
        if len(self.requested_groups_paginations)>len(self.uploaded_groups_paginations):
            deviation = len(self.requested_groups_paginations) - len(self.uploaded_groups_paginations)
            UNF_STR.print_fuksi(f"ИТОГО: ЗАГРУЖЕНО ЛИШЬ {len(self.uploaded_groups_paginations)} PAGINATION PAGES ИЗ {len(self.requested_groups_paginations)} ПОТЕРЯНО {deviation} шт) :")
            number = 0
            for each_requested_group_pagination in enumerate(self.requested_groups_paginations):
                if each_requested_group_pagination not in self.uploaded_groups_dict:
                    number += 1
                    if number>=5:
                        print(f"  -и другие ... ")
                        break
                    print(f"  - в том числе не загружена {number} group pagination   {each_requested_group_pagination}")
        elif len(self.requested_groups_paginations)<len(self.uploaded_groups_paginations):
            deviation = len(self.requested_groups_paginations) - len(self.uploaded_groups_paginations)
            UNF_STR.print_red(f"ИТОГО: НОНСЕНС ЗАГРУЖЕНО НА {deviation} GROUP PAGINATION БОЛЬШЕ ЧЕМ ЗАПРОШЕНО")
            UNF_STR.print_red(f"ИТОГО: НОНСЕНС ЗАГРУЖЕНО {len(self.uploaded_groups_paginations)} PAGINATIONS PAGE (НА {deviation}  БОЛЬШЕ) ИЗ {len(self.uploaded_groups_paginations)} ЗАПРОШЕНЫХ ")
        else:
            UNF_STR.print_green(f"ИТОГО: ЗАГРУЖЕНЫ ВСЕ {len(self.requested_groups_paginations)} GROUP PAGINATION ")

    def show_uploaded_products(self):
        if len(self.requested_products_dict)>len(self.uploaded_products_dict):
            deviation = len(self.requested_products_dict) - len(self.uploaded_products_dict)
            UNF_STR.print_fuksi(f"ИТОГО: ИЗ ТОВАРОВ ЗАГРУЖЕНО ЛИШЬ {len(self.uploaded_products_dict)} ИЗ {len(self.requested_products_dict)} ПОТЕРЯНО {deviation} шт")
            number = 0
            for each_requested_product in self.requested_products_dict:
                if each_requested_product not in self.uploaded_products_dict:
                    number += 1
                    if number >= 5:
                        print(f"  - и другие ... ")
                        break
                    print(f"  - в том числе не загружен товар {number}  " + each_requested_product)
        elif len(self.requested_products_dict)<len(self.uploaded_products_dict):
            deviation = len(self.requested_products_dict) - len(self.uploaded_products_dict)
            UNF_STR.print_fuksi(f"ИТОГО: ИЗ ТОВАРОВ ЗАГРУЖЕНО ЧРЕЗМЕРНО МНОГО {len(self.uploaded_products_dict)} ИЗ {len(self.requested_products_dict)} ЛИШНИХ {deviation} шт")
        else:
            UNF_STR.print_green(f"ИТОГО: ЗАГРУЖЕНЫ ВСЕ {len(self.requested_products_dict)} ТОВАРОВ")

    def show_uploaded_images(self):
        # покажем сколько загружено новых картинок
        if self.add_settings.need_to_upload_images:
            UNF_STR.print_green(f"ИТОГО: ЗАГРУЖЕНО {len(self.uploaded_images)} НОВЫХ КАРТИНОК")
        else:
            UNF_STR.print_fuksi(f"ИТОГО: ЗАГРУЗКА КАРТИНОК ОТКЛЮЧЕНА")

        if self.add_settings.stop_after_number_of_groups != None and self.add_settings.stop_after_number_of_groups >0:
            UNF_STR.print_fuksi(f"(!!!) установлено ограничение количества загружаемых групп {self.add_settings.stop_after_number_of_groups}")

        if self.add_settings.stop_after_number_of_products_on_page != None and self.add_settings.stop_after_number_of_products_on_page >0:
            UNF_STR.print_fuksi(f"(!!!) )установлено ограничение количества загружаемых товаров {self.add_settings.stop_after_number_of_products_on_page}")

        if len(self.failed_upload_urls_dict)>0:
            UNF_STR.print_fuksi(f"ИТОГО: не удалось неудачная загрузка у {len(self.failed_upload_urls_dict)} страниц ")

    def show_uploaded_products(self):
        if len(self.requested_products_dict)>len(self.uploaded_products_dict):
            deviation = len(self.requested_products_dict) - len(self.uploaded_products_dict)
            UNF_STR.print_fuksi(f"ИТОГО: ИЗ ТОВАРОВ ЗАГРУЖЕНО ЛИШЬ {len(self.uploaded_products_dict)} ИЗ {len(self.requested_products_dict)} ПОТЕРЯНО {deviation} шт")
            number = 0
            for each_requested_product in self.requested_products_dict:
                if each_requested_product not in self.uploaded_products_dict:
                    number += 1
                    if number >= 5:
                        print(f"  - и другие ... ")
                        break
                    print(f"  - в том числе не загружен товар {number}  " + each_requested_product)
        elif len(self.requested_products_dict)<len(self.uploaded_products_dict):
            deviation = len(self.requested_products_dict) - len(self.uploaded_products_dict)
            UNF_STR.print_fuksi(f"ИТОГО: ИЗ ТОВАРОВ ЗАГРУЖЕНО ЧРЕЗМЕРНО МНОГО {len(self.uploaded_products_dict)} ИЗ {len(self.requested_products_dict)} ЛИШНИХ {deviation} шт")
        else:
            UNF_STR.print_green(f"ИТОГО: ЗАГРУЖЕНЫ ВСЕ {len(self.requested_products_dict)} ТОВАРОВ")



    def __init__(self, settings_file=None):
        # super().__init__()
        # self.settings.set('ROBOTSTXT_OBEY', False)
        self.init_addition(settings_file)

        self.output_catalog = self.add_settings.get_result_files_path()
        # print(f"result_catalog={self.output_catalog}")

        super(Universal_Spider, self).__init__()


        # if self.settings['ROBOTSTXT_OBEY'] != False:
        #     self.Show_Error("Необходимо параметр ROBOTSTXT_OBEY указать как False, что бы избежать ограничения для роботов")



    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(Universal_Spider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider
