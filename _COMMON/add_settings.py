import os
import configparser
import json
from pprint import pprint
import datetime
import scrapy

from _UNF import String as UNF_STR

class Xpathes():
    structure_selector_xpath = ""
    root_structure_groups_xpath = ""
    root_structure_info = {"name": "",
                           "url": "",
                           "sub_group_selectors": "",
                           }

    recursively_structure_blocks_xpath = ""

    recursively_structure_info = {"name": "",
                                  "url": "",
                                  "sub_group_selectors": "",
                                  }

    group_page_slave_groups_xpath = {
        "selectors": "",
        "name": "",
        "url": "",
    }
    group_page_pagination_other_pages_xpath = ""
    group_page_pagination_next_page_xpath = ""

    group_page_product_xpath = {"selectors": "",
                                "name": "",
                                "url": "",
                                "img_url": "",
                                "price": "",
                                }

    product_info = {
                    "selectors": "",
                    "name": "",
                    "img_url": "",
                    "currency": "",
                    "price": "",
                    "kod": "",
                    "brend": "",
                    "collection": "",
                    "artikul": "",
                    }

    # таблица характеристик продукта
    product_specification_info = {
                            "name":  "",
                            "value": "",
                            "Separate_by_simbol": "",
                            "value_subselector": "",
                            }




class Add_spider_settings():
    start_url_list: list
    comment: str
    version: str

    login_required: bool
    login_url: str
    login_formdata: dict

    result_catalog: str
    result_files_subdir: str
    saved_pages_subdir: str
    saved_images_subdir: str
    need_to_save_pages: bool
    show_debug_messages: bool
    filter_groups_only_url: str
    Read_Only_List_Without_SingleProductPages: bool
    stop_after_number_of_products_on_page: int
    stop_after_number_of_groups: int
    need_to_upload_images: bool

    testing_group_page_url: str
    testing_product_page_url: str

    verify_ssl = False

    xpathes= Xpathes()

    def get_cache_files_path(self):
        res_path = self.result_catalog + "\\_img_Cache"
        return (res_path)


    def get_result_files_path(self):
        res_path = self.result_catalog + "\\_outputs"
        return (res_path)

    def get_saved_pages_path(self):
        res_path = self.result_catalog + "\\" + self.saved_pages_subdir
        return (res_path)

    def get_saved_images_path(self):
        res_path = self.result_catalog + "\\" + self.saved_images_subdir
        return(res_path)


    def set_default_settings(self):
        self.start_url_list = ["https://www.vogtrade.ru",]

        self.testing_group_page_url = [
            "https://www.vogtrade.ru/plitka/",
            "https://www.vogtrade.ru/plitka/ipanema/"
        ]

        self.testing_product_page_url = [
            "https://www.vogtrade.ru/plitka/ipanema/38ace7e2-5d8b-46ed-898c-084f2aaf7c1a-1906-0005/",
            ]

        self.comment = "vogtrade_2020-08-23"
        self.version = "1.0.0"

        self.result_catalog = "l:\\\\_Важное\\6 Работа\\Python\\Grabbed_data\\vogceramic_ru" #f"{os.getcwd()}\\_outputs"
        self.result_files_subdir = f"results"
        self.saved_pages_subdir = f"pages"
        self.saved_images_subdir = f"images"
        self.need_to_save_pages = True
        self.show_debug_messages = True
        self.filter_groups_only_url = ""
        self.Read_Only_List_Without_SingleProductPages = False
        self.stop_after_number_of_products_on_page = 1
        self.stop_after_number_of_groups = 1
        self.need_to_upload_images = True

        self.xpathes = Xpathes()
        self.xpathes.structure_selector_xpath = "(//div[contains (@class,'top-nav')]//ul[@class='main-menu__list'])[1]"
        self.xpathes.root_structure_groups_xpath = ".//li[contains(@class, 'main-menu__item')]/a[(contains(@href, 'plitka')) or (contains(@href, 'oboi'))]"
        self.xpathes.root_structure_info = {
                               "name": "text()[1]",
                               "url": "@href[1]",
                               "sub_group_selectors": "",
                               "img_url": "",
                               }
        self.xpathes.recursively_structure_blocks_xpath = "div[@class='dropdown-menu']/ul/li"
        self.xpathes.recursively_structure_info = {
                                "name": "",
                               "url": "",
                               "sub_group_selectors": ""
                                      }

        self.xpathes.group_page_slave_groups_xpath =  {
            "selectors": "//div[@class='tile__item']",
            "name": ".//a[@class='tile__title fz_xl']/text()",
            "url": ".//a[@class='tile__title fz_xl']/@href",
            "img_url": "",
            "img_logo_url": ".//img[@class='tile__img']/@src",

            }

        self.xpathes.group_page_pagination_other_pages_xpath = ''
        self.xpathes.group_page_pagination_next_page_xpath = "//div[contains (@class,'pagenvaigation-show-more')]/a/@href"

        self.xpathes.group_page_product_xpath = {'selectors': "//div[@class='tab-content']//div[contains(@class, 'tab-pane fade show active')]//div[@class='tile__container']",
                                                 "name_part1": "",
                                                 "name_part2": "",
                                                 "name_part3": "",
                                                 "url": ".//div[@class='tile__desc']/a/@href",
                                                 "img_url": ".//div[@class='tile__img-wrap']/img/@src",
                                                 "price": "",
                                                 }
        self.xpathes.product_info = {
                        "selectors": "//div[contains(@class, \"container\")][contains(@class, \"b-ware\")]",
                        "name_part1": "",
                        "name_part2": "",
                        "name_part3": "",
                        "img_url": "//a[@class='ware-slider-for__cell gallery'][1]/@href",
                        "currency": "//span[@class='card__price-cell']/span[@class='price-rub']/text()",
                        "price": "//span[@class='card__price-cell']/text()",
                        "kod": "//div[text()='\u041a\u043e\u0434 \u0442\u043e\u0432\u0430\u0440\u0430:']/span/text()",
                        "brend": "//div[text()='\u0411\u0440\u0435\u043d\u0434:']/span/a/text()",
                        "collection": "",
                        "artikul": "//div[text()='\u0410\u0440\u0442\u0438\u043a\u0443\u043b:']/span/text()"
                        }

        #таблица характеристик продукта
        self.xpathes.product_specification_info = {
                                           "selector": "//table[@class='table ware-table']/tbody",
                                           "name": './/tr/td[1]/text()',
                                            "value": './/tr/td[2]/text()'
                                           }




    def __init__(self):
        self.set_default_settings()

    # Read_settings_from_ini
    def load_settings(self, path):
        with open(path, 'rb') as config_file:
            result_settings = json.load(config_file, object_hook=decode_json_dict_to_class)

        return result_settings

    def save_current_settings(self, path):
       #print(f"   - сохраняю текущие настройки в файл {path}")

       with open(path, "w", encoding="utf-8") as config_file:
            json.dump(self, config_file, indent=4, cls=CustomEncoder, ensure_ascii=False)




def decode_json_dict_to_class(json_dict):
    if '__Add_spider_settings__' in json_dict:
        object = Add_spider_settings()
        object.__dict__.update(json_dict['__Add_spider_settings__'])
        return object

    elif '__Xpathes__' in json_dict:
        object = Xpathes()
        object.__dict__.update(json_dict['__Xpathes__'])
        return object

    elif '__datetime__' in json_dict:
        object = datetime.strptime(json_dict['__datetime__'], '%Y-%m-%dT%H:%M:%S')
        return object

    else:
        return json_dict

class CustomEncoder(json.JSONEncoder):
    def default(self, class_object):

        # if isinstance(class_object, datetime):
        if isinstance(class_object, scrapy.Selector):
            return {'__scrapy_selector__': "some selectors"}
        elif isinstance(class_object, datetime.datetime):
            return {'__datetime__': class_object.replace(microsecond=0).isoformat()}
        else:
            return {'__{}__'.format(class_object.__class__.__name__): class_object.__dict__}
