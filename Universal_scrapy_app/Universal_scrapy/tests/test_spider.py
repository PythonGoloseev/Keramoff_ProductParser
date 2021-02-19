import urllib.request
from urllib.parse import urljoin

import pytest
from Universal_scrapy_app.Universal_scrapy.spiders.Universal_Spider import Universal_Spider
import os
from Universal_scrapy_app.Universal_scrapy.page_parsers.main_page_parser import Main_Page_Parser
from Universal_scrapy_app.Universal_scrapy.page_parsers.group_page_parser import Group_page_parser
from Universal_scrapy_app.Universal_scrapy.page_parsers.group_page_parser import Single_product_page_parser

from scrapy.selector import Selector
from scrapy.http import HtmlResponse
import UNF_STRING
import ssl
from Universal_scrapy_app.Universal_scrapy.items import *
import UNF_OS
import requests
import webbrowser

class Test_UniversalSpider():

    @pytest.fixture(scope="session", autouse=True)
    def spider(self):
        os.chdir('../../')
        settings_filename = "new_settings_santehnika_online_ru.json"
        res_spider = Universal_Spider(settings_filename)
        return res_spider


    # --------- инициализация -----------------------------------------------------------------------------
    def setup_module(self, module):
        # maxfail = 1
        print(f"\n!!!!!!!!!! СТАРТ ТЕСТОВ !!!!!!!!!!!!!!!")
        pass



    #----test 0--------------------------------------------------------------------------------------------------------
    @pytest.mark.skip
    @pytest.mark.parametrize("param1, param2", [(1, 2), (2, 3), (3, 4)])
    def test_0_param(self, param1, param2):
        print(f"   - runnung test_param param1 = {param1}   param2 = {param2}")
        assert True


    #----test 1 init --------------------------------------------------------------------------------------------------
    #!!! раскоментировать
    @pytest.mark.skip
    def test_1_init_spider(self, spider):
        print(f"\n  - test_spider_init   spider.name = {spider.name}")

        if not len(spider.start_urls)>0:
            spider.RaiseErrorMessage("пустой список start_urls")
            pytest.fail("пустой список start_urls")

        assert True
        # assert len(spider.start_urls)>0


    #-----test 2 MainPage upload --------------------------------------------------------------------------------------
    #!!!
    @pytest.mark.skip
    def test_2_MainPage_parsing(self, spider):
        if len(spider.error_messages) > 0:
            pytest.skip(f"на момент запуска теста уже найдены spider.error_messages")

        url = spider.start_urls[0]
        print(f"\n   - скачиваю страницу {url}")

        scrapy_response = self.get_scrapy_response(url, spider)

        main_page_parser = Main_Page_Parser(spider)
        main_page_parser.parse_info(scrapy_response, spider)
        catalogs_list = main_page_parser.catalogs

        #UNF_STR.print_fuksi(f"len={len(main_page_parser.catalogs)}")

        lower_catalogs_dict = spider.recursively_get_lower_catalogs_to_dict(main_page_parser.catalogs)

        print(f"   - на главной странице собрал {len(lower_catalogs_dict)} групп нижнего уровня")

        for key in lower_catalogs_dict:
            catalog = lower_catalogs_dict[key]
            print(f"      в т.ч. name={catalog.name} url={catalog.url}")
            if UNF_STR.is_empty(catalog.name):
                self.stop_and_fail_test(f"На корневой странице нашел групу с пустым именем {catalog.name}", spider)
            elif UNF_STR.is_empty(catalog.url):
                self.stop_and_fail_test(f"На корневой странице нашел групу с пустым URL", spider)


        if len(spider.error_messages) > 0:
            self.stop_and_fail_test(f"СТОП-ТЕСТ: В процессе исполнения накоплено  {len(spider.error_messages)} ошибок", spider)

        if len(catalogs_list)==0:
            self.stop_and_fail_test(f"СТОП-ТЕСТ: На корневой странице не найдено групп", spider)

        file_name = "Catalogs_object.json"
        spider.save_object_to_json_file(file_name, main_page_parser.catalogs)

        #откроем файл программой по умолчанию
        catalog_path = spider.add_settings.get_result_files_path()
        file_path = os.path.join(catalog_path, file_name)
        webbrowser.open(file_path, new=0) ##new=2 Для новой вкладки

        assert True



    #-----test 3 group page parsing --------------------------------------------------------------------------------------
    #!!!
    @pytest.mark.skip
    def test_3_group_page_parsing(self, spider):
        if len(spider.error_messages) > 0:
            pytest.skip(f"на момент запуска теста уже найдены spider.error_messages")

        testing_group_page_url = spider.add_settings.testing_group_page_url
        for index, url in enumerate(testing_group_page_url):
            print(f"\n   - скачиваю группу товаров {url}")

            scrapy_response = self.get_scrapy_response(url, spider)

            fake_group = Catalog_group(number =index + 1, level = 0, name =f"test_group_{index + 1}", url = url,
                                       domain_url=None, img_url=None, img_logo_url=None, sub_group_selectors=None)

            group_page_parser = Group_page_parser(spider)
            groupe_page_info = group_page_parser.get_info_from_response(scrapy_response, fake_group )

            file_name = fake_group.name + "_object.json"
            spider.save_object_to_json_file(file_name, groupe_page_info)

            # откроем файл программой по умолчанию
            file_path = os.path.join(spider.add_settings.get_result_files_path(), file_name)
            webbrowser.open(file_path, new=0)  ##new=2 Для новой вкладки

            if len(spider.error_messages) > 0:
                self.stop_and_fail_test(
                    f"СТОП-ТЕСТ: В процессе исполнения накоплено  {len(spider.error_messages)} ошибок", spider)
            elif len(groupe_page_info.slave_group_pages_dict)==0 and len(groupe_page_info.products_dict)==0:
                strError = f"СТОП-ТЕСТ: На тестируемой странице не нашел подчиненных групп или товаров {url}"
                UNF_STR.print_red(strError)
                pytest.fail(strError)
            elif len(groupe_page_info.pagination_other_pages_dict) == 0 and \
                    UNF_STR.is_empty(groupe_page_info.pagination_next_page_url) and \
                    len(groupe_page_info.products_dict)==0:
                UNF_STR.print_red(f"СТОП-ТЕСТ: На тестируемой странице не нашел страницы pagination/next_page или товары {url}")
                pytest.fail(f"СТОП-ТЕСТ: На тестируемой странице не нашел страницы pagination/next_page или товары {url}")

            UNF_STR.print_green(f"   Тестовая страница загружена корректно {url}")
            if len(groupe_page_info.slave_group_pages_dict)>0:
                UNF_STR.print_green(f"    - Найдено подчиненных групп {len(groupe_page_info.slave_group_pages_dict)}")
            else:
                UNF_STR.print_black(f"    - Найдено подчиненных групп {len(groupe_page_info.slave_group_pages_dict)}")

            if len(groupe_page_info.pagination_other_pages_dict)>0:
                UNF_STR.print_green(f"    - Найдено подчиненных paginations  {len(groupe_page_info.pagination_other_pages_dict)}")
            else:
                UNF_STR.print_black(
                    f"    - Найдено подчиненных paginations  {len(groupe_page_info.pagination_other_pages_dict)}")

            if not UNF_STR.is_empty(groupe_page_info.pagination_next_page_url):
                UNF_STR.print_green(f"    - сслыка на следующую страницу: {groupe_page_info.pagination_next_page_url}")
            else:
                UNF_STR.print_green(f"    - сслыка на следующую страницу: НЕТ")

            if len(groupe_page_info.products_dict)>0:
                UNF_STR.print_green(f"    - Найдено товаров  {len(groupe_page_info.products_dict)}")
            else:
                UNF_STR.print_fuksi(f"    - НЕ Найдено товаров")

        assert True

    #-----test 4 product page parsing --------------------------------------------------------------------------------------
    #@pytest.mark.skip
    def test_4_product_page_parsing(self, spider):
        if len(spider.error_messages) > 0:
            pytest.skip(f"на момент запуска теста уже найдены spider.error_messages")

        testing_product_page_url = spider.add_settings.testing_product_page_url
        for index, url in enumerate(testing_product_page_url):
            print(f"\n   - скачиваю страницу товара {url}")

            spec_postfix = spider.add_settings.xpathes.product_specification_info['postfix']
            UNF_STR.print_fuksi(f"   - spec_postfix={spec_postfix}")
            if UNF_STR.is_empty(spec_postfix):
                product_url_with_postfix = url
            else:
                product_url_with_postfix = urljoin(url, spec_postfix)

            scrapy_response = self.get_scrapy_response(product_url_with_postfix, spider)

            fake_group = Catalog_group(number=index + 1, level=0, name=f"test_group_{index + 1}", url=url,
                                       domain_url=None, img_url=None, img_logo_url=None, sub_group_selectors=None)

            fake_product_from_list = Product_from_list_page(name="fake_prod_from_list",
                                                    url=url, domain_url=None, img_url = None, price=0, group=fake_group,
                                                    list_page_full_url=None, available_quantity=None,
                                                    reserv_quantity=None, number_on_page=0)

            product_page_file_name = f"test_single_product_{index+1}.html"
            # print(f"   - try to save product_item_page={product_list_file_name}")
            UNF_OS.Save_text_to_file(product_page_file_name, spider.add_settings.get_saved_pages_path(),
                                     scrapy_response.text)

            product_scrapy_item = Product_scrapy_item(fake_product_from_list)
            single_prod_parser = Single_product_page_parser(spider)
            single_prod_parser.parse_info_and_fill_product(scrapy_response, product_scrapy_item, fake_product_from_list)

            file_name = f"test_single_product_object_{index + 1}.json"


            spider.save_object_to_json_file(file_name, product_scrapy_item)
            catalog_path = spider.add_settings.get_result_files_path()
            file_path = os.path.join(catalog_path, file_name)
            webbrowser.open(file_path, new=0)  ##new=2 Для новой вкладки


            xpathes = spider.add_settings.xpathes

            if len(spider.error_messages) > 0:
                self.stop_and_fail_test(
                    f"СТОП-ТЕСТ: В процессе исполнения накоплено  {len(spider.error_messages)} ошибок", spider)
            elif UNF_STR.is_empty(product_scrapy_item['name']):
                self.stop_and_fail_test(
                    f"СТОП-ТЕСТ: Прочитал пустое имя товара {url} по xpath={xpathes.product_info['name']}", spider)
            elif UNF_STR.is_empty(product_scrapy_item['artikul']):
                self.stop_and_fail_test(
                    f"СТОП-ТЕСТ: Прочитал пустое url товара {url} по xpath={xpathes.product_info['artikul']}", spider)

            # elif len(groupe_page_info.pagination_other_pages_dict) == 0 and \
            #         UNF_STR.is_empty(groupe_page_info.pagination_next_page_url) and \
            #         len(groupe_page_info.products_dict)==0:
            #     UNF_STR.print_red(f"СТОП-ТЕСТ: На тестируемой странице не нашел страницы pagination/next_page или товары {url}")
            #     pytest.fail(f"СТОП-ТЕСТ: На тестируемой странице не нашел страницы pagination/next_page или товары {url}")


            UNF_STR.print_green(f"   Тестовая страница товара корректно {url}")


        assert True


    # ----- method - stop_and_fail_test --------------------------------------------------------------------------
    #!!!
    @pytest.mark.skip
    def stop_and_fail_test(self, text, spider):
        spider.error_messages.append(text)
        print(f"{UNF_STR.decor_red()}"
              f"СТОП-ТЕСТ: {text}"
              f"{UNF_STR.decor_default()}")
        pytest.fail(text)




    def generator(self):
        for i in (1, 2, 3):
            yield i

    def response_gen(self, spider):
        url = "https://www.santehsmart.ru/catalog/product/141481.html"
        scrapy_response = self.get_scrapy_response(url, spider)
        new_response = scrapy_response.follow(url)

        import Universal_scrapy_app.Universal_scrapy.spiders.Universal_Spider as US
        us = US()
        f = us.parse(url)
        #new_response.meta['spider'] = spider
        #f = next(new_response)
        UNF_STR.print_fuksi(f"   - получил результат type={type(new_response)} new_response={new_response}")
        assert True


    def async_test_upload(self, response):
        UNF_STR.print_fuksi(f"асинхронно получил response.url={response.url}")
        yield 1





    def save_and_show_in_browser_pageText(self, pageText, name, spider):

        if not name:
            page_file_name = f"some_page.html"
        else:
            page_file_name = f"{name}.html"

        # print(f"   - try to save product_item_page={page_file_name}")
        # UNF_OS.Save_text_to_file(page_file_name, spider.add_settings.get_saved_pages_path(),
        #                          pageText)

        #product_page_file_path = os.path.join(spider.add_settings.get_saved_pages_path(), page_file_name)
        #webbrowser.open(product_page_file_path, new=0)  ##new=2 Для новой вкладки



    # ----- method - get_scrapy_response --------------------------------------------------------------------------
    def get_scrapy_response(self, url, spider: Universal_Spider):
        scrapy_response = spider.alternative_upload_page(url)
        if spider.add_settings.use_selenium:
            spider.close_selenium_driver()

        return(scrapy_response)


#----teardown_module --------------------------------------------------------------------------------------------------
    def teardown_module(self, module):
        # teardown_something()
        print(f"\n!!!!!!!!!! СТОП ТЕСТОВ !!!!!!!!!!!!!!!")
        pass



# assertEqual(a, b)	a == b
# assertTrue(x)	bool(x) is True
# assertFalse(x)	bool(x) is False
# assertIs(a, b)	a is b
# assertIsNone(x)	x is None
# assertIn(a, b)	a in b
# assertIsInstance(a, b)
