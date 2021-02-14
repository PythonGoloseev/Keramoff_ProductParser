import webbrowser

from _UNF import OS as UNF_OS
from _UNF import String as UNF_STR
from urllib.parse import urljoin

from Universal_scrapy_app.Universal_scrapy.page_parsers.single_product_page_parser import Single_product_page_parser
# from Universal_scrapy_app.Universal_scrapy.items import Product_list_item
from Universal_scrapy_app.Universal_scrapy.items import Catalog_item
from Universal_scrapy_app.Universal_scrapy.items import Product_from_list_page
from Universal_scrapy_app.Universal_scrapy.items import Product_scrapy_item
from Universal_scrapy_app.Universal_scrapy.items import Url_page
from Universal_scrapy_app.Universal_scrapy.items import Group_page_info
from Universal_scrapy_app.Universal_scrapy.items import Catalog_group

from _COMMON.spider_addition import Get_text_by_xpath

from _COMMON.spider_addition import Get_text_by_xpath

import _UNF.URLs as UNF_URLs

#---------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------
class Group_page_parser():
    url: str
    response = None
    # products_list = list()
    __spider = None
    need_to_print_Items = False
    other_pages_list = list()
    products_list = list()

    def async_group_upload(self, response):
        current_group = response.meta['current_group']
        its_pagination_follow = response.meta['its_pagination_follow']

        self.url = response.url
        self.response = response

        if response.url in self.__spider.uploaded_pages:
            print(f"Тревога, загрузил страницу, которая уже есть в списке загруженных. url={response.url}  пропускаю ее обработку")
            print(f"Программист должен был добавить в список эту ссылку uploaded_pages ее до вызова асинхронной загрузкию")
            return

        self.__spider.uploaded_pages.append(response.url)

        if its_pagination_follow == True:
            print(f"   ---- group pagination async uploaded {response.url}")
            self.__spider.uploaded_groups_paginations.append(response.url)
        else:
            self.__spider.uploaded_groups_dict[response.url] = response.url
            str_progress = f"{len(self.__spider.uploaded_groups_dict)} of {len(self.__spider.requested_groups_dict)}"
            print(f"   ---- new group async uploaded {str_progress}  {response.url}")



        group_page_info = self.get_info_from_response(response, current_group)

        groups_limit = self.__spider.add_settings.stop_after_number_of_groups


        if len(group_page_info.slave_group_pages_dict)>0:
            #UNF_STR.print_fuksi(f"Открываю подчиненные {len(group_page_info.slave_group_pages_dict)} групп")
            slave_groups_generator = self.open_each_slave_group(group_page_info, response, current_group)
            for each_value in slave_groups_generator:
                yield each_value
            #Не перебираем pagination
            #не открываем next page
            #не открываем товары....
        else:

            pagingation_generator = self.open_each_pagination(group_page_info, its_pagination_follow, response, current_group)
            for each_value in pagingation_generator:
                yield each_value

            next_page_generator = self.open_next_page(group_page_info, response, current_group)
            for each_value in next_page_generator:
                yield each_value


            products_generator = self.open_each_product(group_page_info, response, current_group)
            for each_value in products_generator:
                yield each_value

        self.__spider.save_progress_file()

    # -----------------------------------------------------------------------------------------------------------------
    # --open_each_slave_group-------------------------------------------------------------------------------------------
    # -----------------------------------------------------------------------------------------------------------------
    def open_each_slave_group(self, group_page_info, response, current_group):
        groups_limit = self.__spider.add_settings.stop_after_number_of_groups

        #Запустим переход на найденные  подчиненные группы
        for index, slave_group_url in enumerate(group_page_info.slave_group_pages_dict):

            # проверим не превышено ли ограничение на количество загружаемых групп
            if  groups_limit != None and groups_limit>0 and len(self.__spider.requested_groups_dict)>=groups_limit:
                UNF_STR.print_fuksi(f"      (!) прекратил запрос подчиненных групп, потому как достиг ограничения количества загружаемых групп {self.__spider.add_settings.stop_after_number_of_groups}")
                break

            full_slave_group_url = response.urljoin(slave_group_url)
            self.__spider.requested_groups_dict[full_slave_group_url] = full_slave_group_url
            self.__spider.debug_print(f"         - {index+1} перехожу на вложенную группу  {slave_group_url}")

            new_response = response.follow(slave_group_url,
                                           callback=self.async_group_upload)
            new_response.meta['current_group'] = current_group
            new_response.meta['spider'] = self
            new_response.meta['its_pagination_follow'] = False
            yield new_response

    # -----------------------------------------------------------------------------------------------------------------
    # --open_each_pagination-------------------------------------------------------------------------------------------
    # -----------------------------------------------------------------------------------------------------------------
    def open_each_pagination(self, group_page_info, its_pagination_follow, response, current_group):
        groups_limit = self.__spider.add_settings.stop_after_number_of_groups
        domain_url = UNF_URLs.get_base_domain(response.url)

        # запустим асинхрооное открытие других страниц pagination
        if not its_pagination_follow:
            # UNF_STR.print_fuksi(
            #     f"пробую перебрать остальные {len(group_page_info.pagination_other_pages_dict)} paginations")
            for other_page_url in group_page_info.pagination_other_pages_dict:
                other_page_full_url = urljoin(domain_url + "/", other_page_url)

                if other_page_full_url not in self.__spider.requested_groups_paginations:

                    # проверим не превышено ли ограничение на количество загружаемых групп
                    if groups_limit != None and groups_limit > 0 and len(self.__spider.requested_groups_dict)  == groups_limit:
                        UNF_STR.print_fuksi(
                            f"   (!) прекратил запрос остальных group pagination, потому как достиг ограничения количества загружаемых групп {groups_limit}")
                        break
                    # UNF_STR.print_fuksi(# f"запрашиваю Pagination  {other_page_full_url} paginations")

                    self.__spider.requested_groups_paginations.append(other_page_full_url)
                    self.__spider.debug_print(f"      асинхронно открою другую страницу pagination {other_page_full_url}")

                    new_response = response.follow(other_page_full_url, callback=self.async_group_upload)
                    new_response.meta['current_group'] = current_group
                    new_response.meta['spider'] = self
                    new_response.meta['its_pagination_follow'] = True
                    yield new_response

                else:
                    UNF_STR.print_fuksi(f"!!! пропускаю ужа ранее загруженную other_page{other_page_url}")

    # -----------------------------------------------------------------------------------------------------------------
    # ----open_next_page-----------------------------------------------------------------------------------------------
    # -----------------------------------------------------------------------------------------------------------------
    def open_next_page(self, group_page_info, response, current_group):
        groups_limit = self.__spider.add_settings.stop_after_number_of_groups

        #запросим страницу Далее
        if not UNF_STR.is_empty(group_page_info.pagination_next_page_url):

            #если достугнуто ограничение На количество загружаемых групп и это страница с группами (без товаров)
            # - смотреть страницы далее нет смысла
            if len(group_page_info.products_dict) == 0 and groups_limit != None and groups_limit > 0 and len(self.__spider.requested_groups_dict) >= groups_limit:
                # страницы даже не смотрим...
                pass
            else:
                self.__spider.requested_groups_paginations.append(group_page_info.pagination_next_page_url)
                self.__spider.debug_print(f"      асинхронно открою следующую страницу pagination {group_page_info.pagination_next_page_url}")

                new_response = response.follow(group_page_info.pagination_next_page_url, callback=self.async_group_upload)
                new_response.meta['current_group'] = current_group
                new_response.meta['spider'] = self
                new_response.meta['its_pagination_follow'] = True
                yield new_response

    # -----------------------------------------------------------------------------------------------------------------
    # ----open_each_product--------------------------------------------------------------------------------------------
    # -----------------------------------------------------------------------------------------------------------------
    def open_each_product(self, group_page_info, response, current_group):

        # запустим скачивание  каждого товара из списка (либо возврат только данных из списка)
        for index, product_url in enumerate(group_page_info.products_dict):
            each_product = group_page_info.products_dict[product_url]

            # проверим не превышено ли ограничение на количество загружаемых карточек товаров
            if self.__spider.add_settings.stop_after_number_of_products_on_page != None and self.__spider.add_settings.stop_after_number_of_products_on_page > 0 and index+1 > self.__spider.add_settings.stop_after_number_of_products_on_page:
                UNF_STR.print_red(f"   (!) ограничил количество запрошенных товаров из списка товаров группы до {self.__spider.add_settings.stop_after_number_of_products_on_page}  {current_group.url}")
                yield None
                break

            full_url = response.urljoin(each_product.url)
            self.__spider.requested_products_dict[full_url] = full_url

            if self.__spider.add_settings.Read_Only_List_Without_SingleProductPages:
                self.__spider.debug_print(f"   - {index+1} выгружаю short_product_card всего выгружено {len(self.__spider.requested_products_dict)} ")
                Product_item = Product_scrapy_item(each_product)

                self.__spider.uploaded_products_dict[each_product.url] = each_product.url

                yield Product_item
            else:
                # запустим парсинг страницы товара


                single_product_page_parser = Single_product_page_parser(self.__spider)
                new_response = response.follow(each_product.url,
                                               callback=single_product_page_parser.async_upload_and_parse)
                # new_response.meta['current_group'] = current_group
                new_response.meta['product_from_list'] = each_product
                yield new_response


    # -----------------------------------------------------------------------------------------------------------------
    # ----get_info_from_response--------------------------------------------------------------------------------------------
    # -----------------------------------------------------------------------------------------------------------------
    def get_info_from_response(self, response, current_group):

        #сохраним страницу если надо
        if self.__spider.add_settings.need_to_save_pages:
            # print(f"   - try to save product_list_file_name={product_list_file_name}")
            product_list_file_name = "product_list_page_" + UNF_URLs.convert_url_to_file_name(response.url) + ".html"
            UNF_OS.Save_text_to_file(product_list_file_name, self.__spider.add_settings.get_saved_pages_path(), response.text)

        group_page_info = Group_page_info(response.url)

        group_page_info.slave_group_pages_dict = self.get_catalogs_dict_from_group_page(response, current_group, spider=self.__spider)
        self.__spider.debug_print(
        f"      - получил {len(group_page_info.slave_group_pages_dict)} подчиненных групп с текущей страницы группы name={current_group.name} url={current_group.url} ")

        group_page_info.pagination_other_pages_dict = self.get_pagination_other_pages_dict_from_page(response, current_group)
        self.__spider.debug_print(f"      - получил {len(group_page_info.pagination_other_pages_dict)} pagination страниц с текущей страницы группы {current_group.name}")

        group_page_info.pagination_next_page_url = self.get_pagination_next_page_url(response, current_group)
        self.__spider.debug_print(f"      - получил next_page_url={group_page_info.pagination_next_page_url}")

        group_page_info.products_dict = self.get_products_list_from_page(response, current_group)
        self.__spider.debug_print(f"      - получил {len(group_page_info.products_dict)} товаров с текущей страницы группы {current_group.name}")

        return group_page_info



    # -----------------------------------------------------------------------------------------------------------------
    # ----get_pagination_other_pages_dict_from_page--------------------------------------------------------------------
    # -----------------------------------------------------------------------------------------------------------------
    def get_pagination_other_pages_dict_from_page(self, response, current_group):

        # получим список ссылок на другие страницы
        other_pages_dict = {}

        other_pages_xpath = self.__spider.add_settings.xpathes.group_page_pagination_other_pages_xpath

        if UNF_STR.is_empty(other_pages_xpath):
            return other_pages_dict

        pagination_url_list = response.xpath(other_pages_xpath).extract()

        # убирем повторы
        pagination_url_list = list(dict.fromkeys(pagination_url_list))

        domain_url = UNF_URLs.get_base_domain(response.url)

        for str_url in pagination_url_list:
            url_page = Url_page(str_url, "pagination", domain_url)

            # show_url = str_url
            # if show_url.startswith(current_group.url):
            #     show_url = show_url.partition(current_group.url)[2]
            #     print(f"       - pagination={show_url}")
            other_pages_dict[str_url] = url_page

        return other_pages_dict

    # -----------------------------------------------------------------------------------------------------------------
    # ----get_pagination_next_page_url---------------------------------------------------------------------------------
    # -----------------------------------------------------------------------------------------------------------------
    def get_pagination_next_page_url(self, response, current_group):

        # получим список ссылок на другие страницы

        next_page_path = self.__spider.add_settings.xpathes.group_page_pagination_next_page_xpath

        if UNF_STR.is_empty(next_page_path):
            return(None)

        next_page_url = response.xpath(next_page_path).extract_first()

        return next_page_url



    # -----------------------------------------------------------------------------------------------------------------
    # ----get_catalogs_dict_from_group_page----------------------------------------------------------------------------
    # -----------------------------------------------------------------------------------------------------------------
    def get_catalogs_dict_from_group_page(self, response, current_group, spider):

        # получим список ссылок на другие страницы

        xpathes = self.__spider.add_settings.xpathes

        res_groups_dict = {}


        # UNF_STR.print_red(f"group_page_slave_groups_xpath={xpathes.group_page_slave_groups_xpath}")
        # UNF_STR.print_fuksi(f"selectors={xpathes.group_page_slave_groups_xpath['selectors']}")

        group_selectors_xpath = xpathes.group_page_slave_groups_xpath['selectors']
        group_name_xpath = xpathes.group_page_slave_groups_xpath['name']
        group_url_xpath = xpathes.group_page_slave_groups_xpath['url']
        group_img_url_xpath = xpathes.group_page_slave_groups_xpath['img_url']
        group_img_logo_url_xpath = xpathes.group_page_slave_groups_xpath['img_logo_url']


        if UNF_STR.is_empty(group_selectors_xpath):
            #возвращаем пустой словарь, если путь поиска не задан
            return res_groups_dict

        if UNF_STR.is_empty(group_name_xpath):
            spider.RaiseErrorMessage(f"не заполнена настройка group_page_slave_groups_xpath.name")
            return res_groups_dict
        elif UNF_STR.is_empty(group_url_xpath):
            spider.RaiseErrorMessage(f"не заполнена настройка group_page_slave_groups_xpath.url")
            return res_groups_dict

        groups_selectors = response.xpath(group_selectors_xpath)

        domain_url = UNF_URLs.get_base_domain(response.url)

        for index, group_selector in enumerate(groups_selectors):
            group_name = group_selector.xpath(group_name_xpath).extract_first()
            group_url = group_selector.xpath(group_url_xpath).extract_first()

            group_img_url = Get_text_by_xpath(group_selector, group_img_url_xpath)
            group_img_url = self.__spider.remove_background_prefix(group_img_url)

            group_img_logo_url = Get_text_by_xpath(group_selector, group_img_logo_url_xpath)


            sub_group_selectors = None

            #UNF_STR.print_fuksi(f"   - нашел slave группу name={group_name}  url={group_url}   img_logo_url={group_img_logo_url}")

            group_number = index + 1
            catalog = Catalog_group(number=group_number, level = None, name=group_name, url=group_url,
                                    domain_url=domain_url, img_url=group_img_url, img_logo_url=group_img_logo_url, sub_group_selectors=sub_group_selectors )
            #, domain_url, img_url = None, img_logo_url = None

            #UNF_STR.print_fuksi(f"catalog.img_url={catalog.img_url}  group_img_url={group_img_url}")

            # show_url = str_url
            # if show_url.startswith(current_group.url):
            #     show_url = show_url.partition(current_group.url)[2]
            #     print(f"       - pagination={show_url}")
            res_groups_dict[group_url] = catalog

        return res_groups_dict


    # -----------------------------------------------------------------------------------------------------------------
    # ----get_products_list_from_page----------------------------------------------------------------------------------
    # -----------------------------------------------------------------------------------------------------------------
    def get_products_list_from_page(self, response, current_group):
        # product_url_list = response.xpath('//div[@class='card']/a[contains(@class,'img_block')]/img[contains(@class, "card-img")]/@src').extract()
        result_products_dict = {}

        domain_url = UNF_URLs.get_base_domain(response.url)

        group_page_product_xpath = self.__spider.add_settings.xpathes.group_page_product_xpath

        selectors_xpath = group_page_product_xpath['selectors']

        if UNF_STR.is_empty(selectors_xpath):
            self.__spider.RaiseErrorMessage("В настройка обнаружен пустой путь group_page_product_xpath['selectors'] ")
            return result_products_dict

        products_selectors = response.xpath(selectors_xpath)

        #UNF_STR.print_fuksi(f"selectors_xpath={selectors_xpath} нашел {len(products_selectors)} селекторов товаров списка")


        for index, each_product_selector in enumerate(products_selectors):

            # if self.__spider.add_settings.need_to_save_pages:
            #     # print(f"   - try to save product_list_file_name={product_list_file_name}")
            #     file_name = f"product_selector_{index+1}.html"
            #
            #     UNF_OS.Save_text_to_file(file_name, self.__spider.add_settings.get_saved_pages_path(),
            #                              each_product_selector.extract())

            name_part1 = Get_text_by_xpath(each_product_selector, group_page_product_xpath["name_part1"])
            name_part2 = Get_text_by_xpath(each_product_selector, group_page_product_xpath["name_part2"])
            name_part3 = Get_text_by_xpath(each_product_selector, group_page_product_xpath["name_part3"])

            name = (name_part1 + " " + name_part2 + " " + name_part3).strip()

            url = Get_text_by_xpath(each_product_selector, group_page_product_xpath["url"])
            img_url = Get_text_by_xpath(each_product_selector, group_page_product_xpath["img_url"])
            img_url = self.__spider.remove_background_prefix(img_url)
            price_str = Get_text_by_xpath(each_product_selector, group_page_product_xpath["price"])

            available_quantity = Get_text_by_xpath(each_product_selector, group_page_product_xpath["available_quantity"])
            reserv_quantity = Get_text_by_xpath(each_product_selector, group_page_product_xpath["reserv_quantity"])

            # file_name = "group_product_selector" + UNF_URLs.convert_url_to_file_name(response.url) + ".html"
            # path = UNF_OS.Save_text_to_file(file_name, self.__spider.add_settings.get_saved_pages_path(), each_product_selector.extract())
            # webbrowser.open(path, new=2)  ##new=2 Для новой вкладки

            #проверим заполнение name url
            if UNF_STR.is_empty(name):
                self.__spider.RaiseErrorMessage("Указанный шаблон group_page_product_xpath (name) товара дал пустое значение")
                continue
            elif UNF_STR.is_empty(url):
                self.__spider.RaiseErrorMessage("Указанный шаблон group_page_product_xpath (url) товара дал пустое значение")
                continue

            price_str = price_str.replace(chr(160), "")
            price_str = price_str.replace(" ", "")


            product_from_list_page = Product_from_list_page(name=name, url=url, domain_url=domain_url, img_url=img_url,
                                                            price = price_str, group = current_group,
                                                            list_page_full_url = response.url,
                                                            available_quantity=available_quantity,
                                                            reserv_quantity=reserv_quantity, number_on_page =index + 1)

            #загрузка картинки ЛОГОТИПА СПИСКА
            if self.__spider.add_settings.need_to_upload_images and product_from_list_page.img_url != None and product_from_list_page.img_url.strip() != "":
                full_img_url = urljoin(domain_url + "/", product_from_list_page.img_url)
                img_abs_path = self.__spider.get_abs_path(product_from_list_page.uploaded_img_rel_path)
                self.__spider.upload_img_if_not_exists(full_img_url, img_abs_path)

            self.__spider.debug_print(f"       - нашел продукт №{index+1} в списке {product_from_list_page}")
            result_products_dict[url] = product_from_list_page

        return  result_products_dict



    # -----------------------------------------------------------------------------------------------------------------
    # ----__init__----------------------------------------------------------------------------------
    # -----------------------------------------------------------------------------------------------------------------
    def __init__(self, spider):
        self.__spider = spider
        # self.saved_pages_catalog = self.__spider.settings.get('saved_pages_catalog')

