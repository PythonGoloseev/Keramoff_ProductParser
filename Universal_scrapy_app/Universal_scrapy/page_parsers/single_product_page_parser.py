from urllib.parse import urljoin

from Universal_scrapy_app.Universal_scrapy.items import  Product_scrapy_item
from _UNF import OS as UNF_OS
from Universal_scrapy_app.Universal_scrapy.items import Url_page
from Universal_scrapy_app.Universal_scrapy.items import Specification
import _UNF.URLs as UNF_URLs
import _UNF.String as UNF_STR

from Universal_scrapy_app.Universal_scrapy.items import get_rel_path_to_img_from_url
from _COMMON.spider_addition import Get_text_by_xpath

#import progressbar

#from progress.bar import IncrementalBar



class Single_product_page_parser():
    # url: str
    # response = None
    # products_list = list()
    __spider = None
    # other_pages_list = list()
    # products_list = list()

    def async_upload_and_parse(self, response):
        if response.url in self.__spider.uploaded_pages:
            print(f"Тревога, загрузил страницу, которая уже есть в списке загруженных. url={response.url}  пропускаю ее обработку")
            print(f"Программист должен был добавить в список эту ссылку uploaded_pages ее до вызова асинхронной загрузкию")
            return


        self.__spider.uploaded_pages.append(response.url)
        self.__spider.uploaded_products_dict[response.url] = response.url




        str_product_progress = f"{len(self.__spider.uploaded_products_dict)} of {len(self.__spider.requested_products_dict)}"
        str_group_progress = f"{len(self.__spider.uploaded_groups_dict)}/{len(self.__spider.requested_groups_dict)}"
        # self.__spider.debug_print(f"   ---- product page async uploaded {str_progress} page url={response.url}")
        print(f"   ---- product page async uploaded {str_product_progress}  (crawl {str_group_progress} groups) url={response.url}")

        # if not self.__spider.show_debug_messages:
            # progress_bar = progressbar.ProgressBar(maxval=len(self.__spider.requested_products_dict))
            # progress_bar.start()
            # progress_bar.update(len(self.__spider.uploaded_products_dict))


        # progress_bar.finish()

        product_from_list = response.meta['product_from_list']

        # if self.__spider.add_settings.need_to_save_pages:
        #     product_list_file_name = "single_product_" + UNF_URLs.convert_url_to_file_name(product_from_list.url) + ".html"
        #     # print(f"   - try to save product_item_page={product_list_file_name}")
        #     UNF_OS.Save_text_to_file(product_list_file_name, self.__spider.add_settings.get_saved_pages_path(), response.text)

        product_scrapy_item = Product_scrapy_item(product_from_list)


        self.parse_info_and_fill_product(response, product_scrapy_item, product_from_list)

        yield product_scrapy_item

    def parse_info_and_fill_product(self, response, product_scrapy_item, product_from_list):
        # self.__spider.debug_print(f"      - пробую парсить товар {response.url}")

        xpathes = self.__spider.add_settings.xpathes

        product_info_Selector = response.xpath(xpathes.product_info['selectors'])
        # print(product_info_Selector.extract_first())



        product_scrapy_item['type_Card'] = "full_info_from_product_card"

        name_part1 = Get_text_by_xpath(product_info_Selector, xpathes.product_info["name_part1"])
        name_part2 = Get_text_by_xpath(product_info_Selector, xpathes.product_info["name_part2"])
        name_part3 = Get_text_by_xpath(product_info_Selector, xpathes.product_info["name_part3"])
        self.__spider.debug_print(f"         - распарсил name_part1{name_part1}  name_part2={name_part2} name_part3={name_part3}")

        name = (name_part1 + " " + name_part2 + " " + name_part3).strip()
        product_scrapy_item["name"] = name

        for key in xpathes.product_info:
            if key == "selectors": continue
            if key == "name_part1": continue
            if key == "name_part2": continue
            if key == "name_part3": continue

            xpath = xpathes.product_info[key]
            if UNF_STR.is_empty(xpath): continue

            # print(f" dict key={key}, xpath={xpath}")
            value = Get_text_by_xpath(product_info_Selector, xpath)
            self.__spider.debug_print(f"         - распарсил {key}={value}")
            product_scrapy_item[key] = value

            # if key == "img_url":
            #     UNF_STR.print_fuksi(f"{key}={value} xpath={xpath}")
            #     UNF_OS.Save_text_to_file("single_product_selector.html", self.__spider.add_settings.get_saved_pages_path(),
            #                              product_info_Selector.extract_first())

        product_scrapy_item["full_url"] = response.url

        specification_selectors = response.xpath(xpathes.product_specification_info['selector'])
        self.__spider.debug_print(f"         - нашел {len(specification_selectors)} селекторов спецификаций")

        specifications_list = self.get_specifications_list(specification_selectors, xpathes, response.url)

        specification_dicts_list = list()
        self.__spider.debug_print(f"         - получил таблицу доп. свойств из {len(specifications_list)} элементов")
        for specification_object in specifications_list:
            self.__spider.debug_print(f"         - доп свойство {specification_object.name} = {specification_object.value}" )
            specification_dicts_list.append(specification_object.to_dict())



        #загрузка картинки товара
        product_scrapy_item['uploaded_img_rel_path'] = get_rel_path_to_img_from_url("single_product_img_", product_scrapy_item['img_url'], product_from_list.group)

        if self.__spider.add_settings.need_to_upload_images and product_scrapy_item['img_url'] != None and product_scrapy_item['img_url'].strip() != "":
            domain_url = UNF_URLs.get_base_domain(response.url)
            full_img_url = urljoin(domain_url + "/", product_scrapy_item['img_url'])
            img_abs_path = self.__spider.get_abs_path(product_scrapy_item['uploaded_img_rel_path'])
            self.__spider.upload_img_if_not_exists(full_img_url, img_abs_path)


        product_scrapy_item['specification_dicts_list'] = specification_dicts_list

        #объект дозаполнен выходим из процедуры
        return


    def get_specifications_list(self, specification_Selectors, xpathes, response_url):

        res_specifications_list = list()

        for specif_selector in specification_Selectors:
            specifications_name_list = specif_selector.xpath(xpathes.product_specification_info['name']).extract()

            Separate_by_simbol = xpathes.product_specification_info['Separate_by_simbol']
            if not UNF_STR.is_empty(Separate_by_simbol):
                value_xpath = xpathes.product_specification_info['name']
            else:
                value_xpath = xpathes.product_specification_info['value']

            value_subselector = xpathes.product_specification_info['value_subselector']
            if not UNF_STR.is_empty(value_subselector):
                row_specifications_value_list = specif_selector.xpath(value_xpath)
                specifications_value_list = []
                for each_row_value in row_specifications_value_list:
                    act_value = each_row_value.xpath(value_subselector).extract()
                    specifications_value_list.append(act_value)

            else:
                specifications_value_list = specif_selector.xpath(value_xpath).extract()




            # file_name = "specif_secector_" + str(num)
            # print(f"file_name={file_name}")
            # UNF_OS.Save_text_to_file(file_name, self.saved_pages_catalog, specif_selector.extract())


            # print(type(specif_selector))
            # print(f"{specif_selector.extract()}")
            # print("--------------------")
            # print(names_xpath)

            if len(specifications_name_list) != len(specifications_value_list):
                self.__spider.RaiseErrorMessage(f"не совпали длины список name/value в таблице спецификаций. Длина {len(specifications_name_list)} против {len(specifications_value_list)}", response_url)
                #print("ОШБИКА не совпали длины список name/value в таблице спецификаций " + response_url)
            else:
                # print(f"      - в очередном блоке нашел {len(specifications_name_list)} name/value характеристики")
                pass


            row_specifications = zip(specifications_name_list, specifications_value_list)


            for specification in row_specifications:
                if not UNF_STR.is_empty(Separate_by_simbol):
                    specif_name_and_value = specification[0]

                    specif_name = specif_name_and_value.partition(Separate_by_simbol)[0]
                    specif_value = specif_name_and_value.partition(Separate_by_simbol)[2]

                    #убирать спец символы после дележа на partition потому как этот дележ может быть по спец символу "："
                    specif_name = UNF_STR.remove_spec_chars(specif_name)
                    specif_value = UNF_STR.remove_spec_chars(specif_value)




                    if UNF_STR.is_empty(specif_name) or UNF_STR.is_empty(specif_value):
                        #UNF_STR.print_yellow(f"пропускаю неполную спецификацию name={specif_name}  value={specif_value} из строки {UNF_STR.remove_spec_chars(specif_name_and_value)}")
                        continue
                    else:
                        #UNF_STR.print_green(f" - допускаю спецификация name={specif_name}  value={specif_value}")
                        pass



                else:
                    specif_name = UNF_STR.remove_spec_chars(specification[0])
                    specif_value = UNF_STR.remove_spec_chars(specification[1])




                specification_object = Specification(specif_name, specif_value)
                res_specifications_list.append(specification_object)


        return res_specifications_list










    def __init__(self, spider):
        self.__spider = spider
