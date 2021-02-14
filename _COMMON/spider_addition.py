import json
import os
import configparser
from _COMMON.add_settings import Add_spider_settings, CustomEncoder
import urllib3

import argparse
import sys
import ssl
import requests
import webbrowser

from sys import path as sys_path #im naming it as pylib so that we won't get confused between os.path and sys.path
# sys_path += [os.path.abspath('../../')] # подключаем каталог выше запущенного корневого скрипта scrapy на уровень
sys_path += [os.path.abspath('../')] # подключаем каталог выше запущенного корневого скрипта scrapy на уровень
#print(f"подключаю папку: {os.path.abspath('../')}")
from _UNF import OS as UNF_OS
from _UNF import String as UNF_STR
from scrapy.http import FormRequest


#import httplib2



class Spider_addition():
    settings_file_name: str

    uploaded_pages = list()
    cancelled_pages = list()
    failed_upload_urls_dict = {}

    requested_groups_dict = {}
    uploaded_groups_dict = {}

    requested_groups_paginations = list()
    uploaded_groups_paginations = list()

    requested_products_dict = {}
    uploaded_products_dict = {}


    catalogs_list = list()

    error_pages = list()
    error_messages = list()

    uploaded_images = dict()

    add_settings = Add_spider_settings()

    alternative_sesion = None
    start_time: None
    finish_time: None
    duration: None


    def init_addition(self, settings_file):

        #включим цветной вывод в консоли
        import ctypes
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)

        if settings_file == None:
            UNF_STR.print_fuksi(f"!!!!!!!!!!!!!!!!!!!!! НЕОБХОДИМО УКАЗАТЬ ПАРАМЕТР -a setting_file=name_of_setting_file.json")
            UNF_STR.print_fuksi(f"для запуска используйте такую строку:\n"
                + "scrapy crawl Universal_spider --loglevel WARNING -a settings_file=---settings_centrsantehniki_com.json")
            UNF_STR.print_fuksi(f"!!!!!!!!!!!!!!!!!!!!! СПИСОК ЗАГРУЖАЕМЫХ РЕСУРСОВ ОЧИЩАЮ")
            self.start_urls = []
            return
        elif not os.path.exists(settings_file):

            UNF_STR.print_fuksi(f"!!!!!!!!!!!!!!!!!!!!! ----ВНИМАНИЕ, НЕ НАЙДЕН ФАЙЛ НАСТРОЕК {settings_file} ---- !!!!!!!!!!!!!!!!!!!!!")
            UNF_STR.print_fuksi(f"!!!!!!!!!!!!!!!!!!!!! ----СПИСОК ЗАГРУЖАЕМЫХ РЕСУРСОВ ОЧИЩАЮ")
            self.start_urls = []
            return

        else:
            self.settings_file_name = settings_file
            print(f"   - указано использовать файл настроек {self.settings_file_name}")


        save_default_params_file()

        # name_of_settings_file = "---settings_centrsantehniki_com.json"
        add_settings = Add_spider_settings()
        add_settings = add_settings.load_settings(self.settings_file_name)
        print(f"   - загрузил настройки из {self.settings_file_name} version={add_settings.version}  comment={add_settings.comment}")

        self.add_settings = add_settings

        self.start_urls = add_settings.start_url_list

        # self.settings.set('ROBOTSTXT_OBEY', False) #не взлетит

        if self.add_settings.stop_after_number_of_groups != None and self.add_settings.stop_after_number_of_groups >0:
            UNF_STR.print_fuksi(f"   - установлено ограничение количества загружаемых групп {self.add_settings.stop_after_number_of_groups}")

        if self.add_settings.stop_after_number_of_products_on_page != None and self.add_settings.stop_after_number_of_products_on_page >0:
            UNF_STR.print_fuksi(f"   - установлено ограничение количества загружаемых товаров {self.add_settings.stop_after_number_of_products_on_page}")

        print(f"   - данные выгружаются в каталог: {self.add_settings.result_catalog}")

        self.clear_old_output_files()

        UNF_OS.make_dir_if_not_exists(self.add_settings.get_result_files_path())
        UNF_OS.make_dir_if_not_exists(self.add_settings.get_saved_pages_path())
        UNF_OS.make_dir_if_not_exists(self.add_settings.get_saved_images_path())



    def RaiseErrorMessage(self, text, url=None, desctiption=None):
        show_text = f"ОШИБКА:"
        show_text = "" + UNF_STR.decor_red() + show_text + UNF_STR.decor_default()


        show_text = show_text + UNF_STR.decor_bold() + f" {text}" + UNF_STR.decor_default()

        if url:
            show_text = show_text + f"  {url}"

        if desctiption:
            show_text = show_text + f"\n {desctiption}"

        print(show_text)
        error_object = Crawling_Error(text, url, desctiption)
        self.error_messages.append(error_object)

    def debug_print(self, text):
        if self.add_settings.show_debug_messages:
            UNF_STR.print_green(text)

    def clear_old_output_files(self):
        # удалим ранее созданные файцы
        current_path = os.getcwd()

        if not os.path.exists(self.add_settings.get_result_files_path()):
            return

        # ищем файлы экспорта
        file_list = os.listdir(self.add_settings.get_result_files_path())

        # удаляем найденный файлы после проверки расширения
        for file_item in file_list:
            if file_item.endswith(".json") or file_item.endswith(".xml"):
                file_path = os.path.join(self.add_settings.get_result_files_path(), file_item)
                #UNF_STR.print_fuksi(f"      - finded old result file to clear: {file_path}")
                UNF_OS.clear_text_file(file_path)


    def get_progress_file_name(self):
        res_file_name = "spider_progress.json"
        return res_file_name

    def get_summary_file_name(self):
        res_file_name = "spider_summary.json"
        return res_file_name

    def delete_progress_file(self):
        path_to_progress_file = os.path.join(self.add_settings.get_result_files_path(), self.get_progress_file_name())
        if os.path.exists(path_to_progress_file):
            #UNF_STR.print_fuksi(f"удаляю старый файл {path_tu_summary}")
            os.remove(path_to_progress_file)

    def delete_summary_file(self):
        path_to_summary = os.path.join(self.add_settings.get_result_files_path(), self.get_summary_file_name())
        if os.path.exists(path_to_summary):
            #UNF_STR.print_fuksi(f"удаляю старый файл {path_to_summary}")
            os.remove(path_to_summary)

    def save_progress_file(self):
        self.save_object_to_json_file(self.get_progress_file_name(), self.get_sprider_summary())

    def get_abs_path(self, img_rel_path):
        img_abs_path = self.add_settings.get_saved_images_path() + "\\" + img_rel_path
        return (img_abs_path)

    def upload_img_if_not_exists(self, img_full_url, img_abs_path):

        if img_abs_path == None or img_abs_path.strip() == "":
            self.RaiseErrorMessage(f"Не могу сохранить картинку {img_full_url} потому как получен пустой путь к файлу!")
            return
        elif img_full_url == None or img_full_url.strip() == "":
            self.RaiseErrorMessage(f"Не могу сохранить картинку {img_full_url} потому как получен пустой путь к файлу!")
            return

        dir_path = os.path.dirname(img_abs_path)
        if not os.path.exists(dir_path):
            UNF_OS.make_dir_if_not_exists(dir_path)

        if os.path.exists(img_abs_path):
            self.debug_print(f'   - картинка уже есть, скачивать не будут {img_abs_path}')
            return

        work_dir = os.getcwd()
        rel_path = img_abs_path.partition(work_dir)[2]

        self.debug_print(f"      - сохраняю {img_full_url}  в файл {rel_path}")

        img_response = self.alternative_upload_page(img_full_url)
        content = img_response.content
        # if ".vogtrade.ru" in img_full_url:
        #     img_response = self.alternative_upload_page(img_full_url)
        #     content = img_response.content
        # else:
        #     #обычный алгоритм
        #     cache_dir = self.add_settings.get_cache_files_path()
        #     http = httplib2.Http(cache_dir, disable_ssl_certificate_validation=True)
        #     response, content = http.request(img_full_url)


        with open(img_abs_path, 'wb') as image_file:
            image_file.write(content)
            #UNF_STR.print_fuksi(f"записал " + img_abs_path)

        self.uploaded_images[img_full_url] = img_full_url

    def save_object_to_json_file(self, file_name, object, catalog_path = None):
        if not catalog_path:
            catalog_path = self.add_settings.get_result_files_path()

        file_path = os.path.join(catalog_path, file_name)
        with open(file_path, "w", encoding="utf-8") as config_file:
            try:
                json.dump(object, config_file, indent=4, cls=CustomEncoder, ensure_ascii=False)
                self.debug_print(f"      - записал объект {file_name}")
            except:
                self.RaiseErrorMessage(f"Не смог сохранить в файле {file_name} объект {object}")


    def login(self):

        my_formdata = self.add_settings.login_formdata
        my_login_url = self.add_settings.login_url

        session = self.alternative_sesion
        verify_ssl = self.add_settings.verify_ssl

        #formRequest = FormRequest(my_login_url , method="POST", formdata=my_formdata, callback=self.login_parse, dont_filter=True)

        response = session.post(my_login_url, data=my_formdata, verify=verify_ssl)

        #     result = scrapy.FormRequest(url=my_login_url, encoding="ascii",
        #                               headers={"X-Requested-With": "XMLHttpRequest"},
        #                               formdata=my_form_data,
        #                               callback=self.parse, dont_filter=True)

        # file_name = "authorization_page.html"
        # catalog_path = self.add_settings.get_result_files_path()
        # UNF_OS.Save_text_to_file(file_name=file_name, catalog_path=catalog_path, text=response.text)
        # file_path = os.path.join(catalog_path, file_name)
        # webbrowser.open(file_path, new=0) ##new=2 Для новой вкладки

        if self.success_autorization(response):
            UNF_STR.print_green(f"   - успешно авторизовался")
        else:
            self.RaiseErrorMessage("Неудачная попытка авторизации")

        pass


    def alternative_upload_page(self, url):

        if self.alternative_sesion == None:
            #UNF_STR.print_fuksi(f"   - создаю новую alternative_sesion")
            self.alternative_sesion = requests.Session()
            self.alternative_sesion.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:83.0) Gecko/20100101 Firefox/83.0'})


            if self.add_settings.login_required:
                #UNF_STR.print_fuksi("   вижу потребность авторизоваться ")
                self.login()



        session = self.alternative_sesion

        # session.auth = ('user', 'pass')

        data = None
        verify_ssl = self.add_settings.verify_ssl
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        try:
            response = session.get(url, data = data, verify = verify_ssl)
        except requests.exceptions.HTTPError:
            response = None
            UNF_STR.print_fuksi(f"Ошибка загрузки HTTPError url={url}")
        except requests.exceptions.ConnectionError:
            response = None
            UNF_STR.print_fuksi(f"Ошибка загрузки ConnectionError url={url}")
        except requests.exceptions.Timeout:
            response = None
            UNF_STR.print_fuksi(f"Ошибка загрузки Timeout url={url}")
        except requests.exceptions.RequestException:
            response = None
            UNF_STR.print_fuksi(f"Ошибка загрузки прочие RequestException url={url}")
        finally:
            if response==None:
                UNF_STR.print_fuksi(f"неудачная попытка загрузки {url}")
            elif response.status_code != 200:
                self.failed_upload_urls_dict[response.url] = response.status_code
                UNF_STR.print_fuksi(f"загрузка страницы вернула плохой код ответа {response.status_code}  url={url}")
            else:
                #UNF_STR.print_yellow(f"      - страница успешно альтернативно загружана  url={url}")
                pass

        response.encoding = 'utf-8'

        return response

    def remove_background_prefix(self, img_url):
        if UNF_STR.is_empty(img_url):
            return("")

        parts = img_url.partition("background-image: url(")
        if not UNF_STR.is_empty(parts[1]):
            new_img_url=parts[2]
            new_img_url=new_img_url[0:-1]
        else:
            new_img_url=img_url

        return new_img_url





    def get_sprider_summary(self):
        res_dict = {
            "start_time": self.start_time,
            "finish_time": self.finish_time,
            "duration_minutes": self.duration,
            "num_of_cancelled_pages": len(self.cancelled_pages),
            "num_of_error_messages": len(self.error_messages),

            "num_of_requested_groups": len(self.requested_groups_dict),
            "num_of_uploaded_groups": len(self.uploaded_groups_dict),

            "num_of_requested_groups_paginations": len(self.requested_groups_paginations),
            "num_of_uploaded_groups_paginations": len(self.uploaded_groups_paginations),

            "num_of_requested_products": len(self.requested_products_dict),
            "num_of_uploaded_products": len(self.uploaded_products_dict),

            "num_of_requested_products": len(self.requested_products_dict),

            "num_of_uploaded_images": len(self.uploaded_images),
            "num_of_failed_upload_urls": len(self.failed_upload_urls_dict),

            "need_to_upload_images": self.add_settings.need_to_upload_images,
            "filter_groups_only_url": self.add_settings.filter_groups_only_url,
            "Read_Only_List_Without_SingleProductPages": self.add_settings.Read_Only_List_Without_SingleProductPages,
            "stop_after_number_of_groups": self.add_settings.stop_after_number_of_groups,
            "stop_after_number_of_products_on_page": self.add_settings.stop_after_number_of_products_on_page,



            "error_messages": self.error_messages,

        }
        return(res_dict)




    def success_autorization(self, response):

        auth_words = "?authorize=yes"
        deauth_words = "?logout=yes"

        #UNF_STR.print_fuksi(f"пробую авторизоваться")

        if auth_words in response.text:
            # file_name = "auth_page.txt"
            # UNF_OS.Save_text_to_file(file_name, self.add_settings.get_saved_pages_path(), response.text)
            # UNF_STR.print_red(f"нашел auth_words={auth_words} в тексте ответа")
            #self.RaiseErrorMessage(f"авторизация неудачна, потому как нашел текст auth_words={auth_words}")
            result_success = False
        elif deauth_words in response.text:
            #UNF_STR.print_green(f"авторизация успешна, нашел текст deauth_words={deauth_words}")
            result_success = True
        else:
            result_success = False
            file_name = "auth_page.txt"
            UNF_OS.Save_text_to_file(file_name, self.add_settings.get_saved_pages_path(), response.text)
            self.RaiseErrorMessage(f"авторизация неудачна, потому как не нашел нашел текст auth_words={auth_words} или текст deauth_words={deauth_words}")


        return result_success





#-----------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------
class Crawling_Page():
    url = None
    name = None
    description = None

    def __init__(self, url, name=None, description=None):
        self.url = url
        self.name = name
        self.description = description

class Crawling_Error():
    text = None
    url = None
    description = None

    def __init__(self, text, url, description):
        self.text = text
        self.url = url
        self.description = description





def save_default_params_file():
    default_settings_file_name = "settings_default.json"
    default_settings = Add_spider_settings()
    default_settings.set_default_settings()
    default_settings.save_current_settings(default_settings_file_name)

def Get_text_by_xpath(selector, xpath):

    if UNF_STR.is_empty(xpath):
        result = ""
    else:
        result = selector.xpath(xpath).extract_first()

    if result == None: result = ""

    result = UNF_STR.remove_spec_chars(result)



    return (result)

