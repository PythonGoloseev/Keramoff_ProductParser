# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
import UNF_URL
import UNF_STRING


class Catalog_item(scrapy.Item):
    its_scructure_block = scrapy.Field()
    type_Card = scrapy.Field()
    structure = scrapy.Field()

    def __init__(self):
        super().__init__()
        self['type_Card'] = "Groups_structure"



class Catalog_group():
    number: int
    name: str
    url: str
    domain_url: str
    img_url: str
    img_logo_url: str
    sub_group_selectors = None
    slave_catalogs: list()

    def __init__(self, number, level, name, url, domain_url, img_url, img_logo_url, sub_group_selectors):
        self.number = number
        self.level = level
        self.name = name
        self.name = name
        self.name = name
        self.url = url
        self.domain_url = domain_url
        self.img_url = img_url
        self.img_logo_url = img_logo_url
        self.sub_group_selectors = sub_group_selectors

        self.slave_catalogs = list()

    def __str__(self):
        res_str: str

        res_str = f"Object CatalogItem name={self.name}   url={self.url}   "
        if self.sub_group_selectors == None:
            res_str += f"sub_group_selectors=None"
        else:
            res_str += f"sub_group_selectors len={len(self.sub_group_selectors)}"
        return (res_str)

    def to_dict(self):

        slave_group_pages_url_list = list()
        for each_slave_catalog in self.slave_catalogs:
            slave_group_pages_url_list.append(each_slave_catalog.to_dict())

        res_dict = {"level": self.level,
                    "number": self.number,
                    "name": self.name,
                    "url": self.url,
                    "domain_url": self.domain_url,
                    "slave_catalogs": slave_group_pages_url_list,
                    }
        return (res_dict)


class Url_page():
    url = ""
    domain = ""
    name = ""

    def __init__(self, url, name, domain):
        self.url = url
        self.name = name
        self.domain = domain


#-----------------------------------------------------------------------------------------------------------------
class Specification():
    name = ""
    value = ""

    def __init__(self, name, value):
        new_name = name.strip()
        new_name = new_name.partition(":")[0]
        self.name = new_name
        self.value = value.strip()

    def to_dict(self):
        result_dict = {
            "name": self.name,
            "value": self.value
        }
        return result_dict



#-----------------------------------------------------------------------------------------------------------------
class Product_from_list_page():
    domain_url: str
    name: str
    url: str
    img_url: str
    price: str
    list_page_full_url: str
    number_on_page: int
    group_page_info = None
    available_quantity: str
    reserv_quantity = str

    uploaded_img_rel_path = ""

    def __init__(self, name, domain_url, url, img_url, price, group,  list_page_full_url, available_quantity, reserv_quantity, number_on_page):
        self.name = name
        self.url = url
        self.domain_url = domain_url
        self.img_url = img_url
        self.price = price
        self.list_page_full_url = list_page_full_url
        self.number_on_page = number_on_page
        self.group = group
        self.uploaded_img_rel_path = get_rel_path_to_img_from_url("img_logo_", self.img_url, self.group_page_info.url)
        self.available_quantity = available_quantity
        self.reserv_quantity = reserv_quantity





    def __str__(self):
        res_str = f"Product_from_list_page object \n" \
                  f"            * number_on_page = {self.number_on_page}  \n" \
                  f"            * name={self.name} \n" \
                  f"            * price={self.price} \n" \
                  f"            * url={self.url} \n" \
                  f"            * img_url={self.img_url} \n" \
                  f"            * group={self.group.name}"
        return(res_str)

#-----------------------------------------------------------------------------------------------------------------
class Group_page_info():
    url: str
    name: str
    title: str

    pagination_other_pages_dict : dict
    pagination_next_page_url: str
    products_dict : dict
    slave_group_pages_dict: dict

    def __init__(self, url):
        self.url = url
        # self.name = url
        # self.title = None

    def __str__(self):
        return f"group_page_info url={self.url} "

#-----------------------------------------------------------------------------------------------------------------
class Product_scrapy_item(scrapy.Item):
    type_Card = scrapy.Field()
    name = scrapy.Field()
    full_url = scrapy.Field()
    domain_url = scrapy.Field()
    price = scrapy.Field()

    img_url = scrapy.Field()
    img_url_domain = scrapy.Field()
    uploaded_img_rel_path = scrapy.Field()

    currency = scrapy.Field()
    kod = scrapy.Field()
    brend = scrapy.Field()
    collection = scrapy.Field()
    artikul = scrapy.Field()
    description = scrapy.Field()

    specification_dicts_list = scrapy.Field()

    from_list_name = scrapy.Field()
    from_list_price = scrapy.Field()
    from_list_url = scrapy.Field()
    from_list_img_url = scrapy.Field()
    from_list_uploaded_img_rel_path = scrapy.Field()

    from_list_group_url = scrapy.Field()



    # def copy_params_from(self, product_list_item):
    #     for field_name in product_list_item._values:
    #         # print(f"list field_name {field_name} = {product_list_item[field_name]}")
    #         self[field_name] = product_list_item[field_name]

    def __init__(self, product_from_list: Product_from_list_page):
        super().__init__()
        self['type_Card'] = "short_info_from_list"
        self['domain_url'] = product_from_list.domain_url
        self['from_list_name'] = product_from_list.name
        self['from_list_url'] = product_from_list.url
        self['from_list_img_url'] = product_from_list.img_url
        self['from_list_uploaded_img_rel_path'] = product_from_list.uploaded_img_rel_path
        self['from_list_price'] = product_from_list.price
        self['from_list_group_url'] = product_from_list.group.url


        self['name'] = ""
        self['full_url'] = ""

        for key in self.fields:
            if not key in self._values.keys():
                self[key] = ""



#-----------------------------------------------------------------------------------------------------------------
def get_rel_path_to_img_from_url(prefiks, img_url, group_page_url):

    if img_url == None:
        return None

    sub_catalog = UNF_URL.convert_url_to_file_name(group_page_url)

    if sub_catalog != None and sub_catalog.strip() != "":
        img_rel_path = sub_catalog + "\\" + prefiks + UNF_URL.convert_url_to_file_name(img_url)
    else:
        img_rel_path = "other_images_" + UNF_URL.convert_url_to_file_name(img_url)

    return (img_rel_path)


