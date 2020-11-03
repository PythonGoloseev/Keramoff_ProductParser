from urllib.parse import urljoin
import urllib3

from Universal_scrapy_app.Universal_scrapy.items import Catalog_group

import os
from sys import path as sys_path #im naming it as pylib so that we won't get confused between os.path and sys.path
sys_path += [os.path.abspath('../')] # подключаем каталог выше запущенного корневого скрипта scrapy на уровень

import _UNF.URLs as UNF_URLs

from _UNF import OS as UNF_OS

import _UNF.String as UNF_STR
from _COMMON.spider_addition import Get_text_by_xpath



class Main_Page_Parser():
    url: str
    response = None
    catalogs = list()
    domain_url = str


    def parse_info(self, response, spider ):
        self.url = response.url;
        self.response = response
        self.catalogs.clear()
        self.domain_url = UNF_URLs.get_base_domain(response.url)


        xpathes = spider.add_settings.xpathes

        xpath = xpathes.structure_selector_xpath

        structure_block_Selectors = response.xpath(xpath)

        if len(structure_block_Selectors) == 0:
            spider.RaiseErrorMessage(f"На главной странице не нашел блок групп по шаблону={xpathes.structure_selector_xpath}    страница {response.url}")
            return
        elif len(structure_block_Selectors) >1:
            spider.RaiseErrorMessage(f"На главной странице нашел не один {len(structure_block_Selectors)} блоков групп по шаблону={xpathes.structure_selector_xpath}    страница {response.url}")
            return

        first_struct_selector = structure_block_Selectors[0]

        #spider.debug_print(f"   - нашел блок с группами товаров")

        # print(f"нашел блок групп в количестве {len(structure_block_Selectors)}")
        if spider.add_settings.need_to_save_pages:
            UNF_OS.Save_text_to_file("root_structure_block.html", spider.add_settings.get_saved_pages_path(), first_struct_selector.extract())

        # print(spider.xpathes.root_bloks_3part_structure_xpath)
        root_structure_groups_list = first_struct_selector.xpath(xpathes.root_structure_groups_xpath)
        print(f"   - нашел {len(root_structure_groups_list)} корневых групп")

        if len(root_structure_groups_list) == 0:
            return

        sub_group_selectors_xpath = xpathes.root_structure_info["sub_group_selectors"]

        #парсим корневые группы
        level = 0
        for index, each_root_block in enumerate(root_structure_groups_list):

            # if spider.add_settings.need_to_save_pages:
            #     UNF_OS.Save_text_to_file(f"root_structure_block_{index}.html", spider.add_settings.get_saved_pages_path(),
            #                              each_root_block.extract())

            group_name = Get_text_by_xpath(each_root_block, xpathes.root_structure_info["name"])
            group_url = Get_text_by_xpath(each_root_block, xpathes.root_structure_info["url"])
            group_img_url = Get_text_by_xpath(each_root_block, xpathes.root_structure_info["img_url"])

            spider.debug_print(f"      - обнаружил корневую группу {group_name} url={group_url}")

            group_logo_url = None
            if UNF_STR.is_empty(sub_group_selectors_xpath):
                group_sub_group_selectors = None
            else:
                group_sub_group_selectors = each_root_block.xpath(sub_group_selectors_xpath)
                #UNF_STR.print_fuksi(f"в корневой группе {group_name} результат поиска вложенных подгрупп длинной {len(group_sub_group_selectors)}")

            # print(f"********** Нашел корневую группу Name = {group_name} url = {group_url}")

            catalog = Catalog_group(number=index + 1, level=level, name=group_name, url= group_url,
                                    domain_url=self.domain_url, img_url=group_img_url, img_logo_url= group_logo_url,
                                    sub_group_selectors=group_sub_group_selectors)



            if group_sub_group_selectors:
                self.recursively_parse_sub_group_selectors_and_append_slave_groups(catalog, spider, level)
                #UNF_STR.print_fuksi(f"!!!!! у корневой группы {catalog.name} + нашел {len(catalog.slave_catalogs)} подчиненных подкаталогов")

            self.catalogs.append(catalog)

        if spider.add_settings.need_to_save_pages:
            spider.save_object_to_json_file("main_page_parser_catalogs_list.json", self.catalogs)

        return


    def recursively_parse_sub_group_selectors_and_append_slave_groups(self, parent_catalog, spider, level):
        level += 1
        # print(level)
        parent_catalog.slave_catalogs = list()

        # print(f"{parent_catalog.sub_group_selectors.extract()}")

        # UNF_OS.Save_text_to_file(parent_catalog.name + ".html", spider.add_settings.get_saved_pages_path(),
        #                          parent_catalog.sub_group_selectors.extract_first())

        xpathes = spider.add_settings.xpathes

        tab = "   "*level
        if len(parent_catalog.sub_group_selectors) == 0:
            # UNF_STR.print_black(
            #     f"   {tab} -у родителя {parent_catalog.name}   нет вложеных подгрупп {level} уровня")
            return
        else:
            # UNF_STR.print_fuksi(
            #     f"   {tab} - у родителя {parent_catalog.name} вложено {len(parent_catalog.sub_group_selectors)} подгрупп {level} уровня")
            pass

        for index, each_recursively_block in enumerate(parent_catalog.sub_group_selectors):

            group_name = Get_text_by_xpath(each_recursively_block, xpathes.recursively_structure_info["name"])
            group_url = Get_text_by_xpath(each_recursively_block, xpathes.recursively_structure_info["url"])
            group_img_url = None
            group_img_logo_url = None

            if not UNF_STR.is_empty(xpathes.recursively_structure_info["sub_group_selectors"]):
                sub_group_selectors = each_recursively_block.xpath(xpathes.recursively_structure_info["sub_group_selectors"])
            else:
                sub_group_selectors = None

            # page_name = parent_catalog.name + "_sub_group_" + str(index+1)  + "_" + group_name + ".html"
            # UNF_OS.Save_text_to_file(page_name, spider.add_settings.get_saved_pages_path(),
            #                           each_recursively_block.extract())
            # UNF_STR.print_fuksi(f"  - {page_name} name={group_name}  url={group_url}  xpath={xpathes.recursively_structure_info['name']} has {len(sub_group_selectors)} downlevel groups")

            catalog = Catalog_group(number=index + 1, level=level, name=group_name, url=group_url,
                                    domain_url=self.domain_url, img_url=group_img_url, img_logo_url=group_img_logo_url,
                                    sub_group_selectors=sub_group_selectors)

            parent_catalog.slave_catalogs.append(catalog)
            spider.debug_print(f"      {tab} - подгруппа({level}ур-{(index+1)}) {catalog} ")
            self.recursively_parse_sub_group_selectors_and_append_slave_groups(catalog, spider, level)

        return #recursively_parse_sub_group_selectors_and_append_slave_groups



    def __init__(self, spider):
        pass



