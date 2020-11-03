import os

def testOS():
    pass

def clear_text_file(path_to_file):
    if not os.path.exists(path_to_file):
        print(f"   - не могу очистить не существующий файл {path_to_file}")
    elif os.path.isdir(path_to_file):
        print(f"   - не могу очисить файл, потому как укзаан путь к папке, вместо файла  {path_to_file}")
    else:
        with open(path_to_file, 'w', encoding='utf-8') as output_file:
            pass
            # output_file.write(text)
            # ничего не делаем, так что файл будет записан пустым

def make_dir_if_not_exists(dir_path, show_success_message = False):
    # if not os.path.islink(dir_path):
    #     print(f"НЕ МОГУ СОЗДАТЬ КАТАЛОГ. ПОТОМУ КАК УКАЗАН НЕККОРЕКТНЫЙ ПУТЬ {dir_path}")


    if os.path.exists(dir_path):
        pass
        #каталог уже создан, все ок
    else:
        access_rights = 0o755  # Это нужно для создания
        try:
            # os.mkdir(catalog_path, access_rights) # это просто создает директорую
            os.makedirs(dir_path, access_rights) # это создает сложную директорию
        except OSError:
            print("ОШИБКА: Создать директорию %s не удалось" % dir_path)
        else:
            if show_success_message:
                print(f"      - Успешно создана директория {dir_path}")



def Save_text_to_file(file_name, catalog_path, text):
    current_path = os.getcwd()
    # print("      - Текущая рабочая директория %s" % current_path)

    if file_name == None or file_name.strip() == "":
        print(f"ОШИБКА: процедура Save_text_to_file получила пустой file_name ")
        return
    elif catalog_path == None or catalog_path.strip() == "":
        print(f"ОШИБКА: процедура Save_text_to_file получила пустой catalog_path ")
        return
    elif type(text) == list:
        print(f"ОШИБКА: процедура Save_text_to_file в качестве text получила список (list) вместо строки")
        return


    # print(f"Save_text_to_file {catalog_path}")

    if not os.path.exists(catalog_path):
        # print("      - Создаю каталог " + catalog_path)
        # define the access rights
        access_rights = 0o755 #Это нужно для создания
        try:
            #os.mkdir(catalog_path, access_rights)
            os.makedirs(catalog_path, access_rights)
        except OSError:
            print("ОШИБКА: Создать директорию %s не удалось" % catalog_path)
        else:
            print("      - Успешно создана директория %s" % catalog_path)

    full_path_to_file = catalog_path + "\\" + file_name
    # print(f"   - пробую записать данные в файл={full_path_to_file}")

    # other coding cp1251
    with open(full_path_to_file, 'w', encoding='utf-8') as output_file:
        output_file.write(text)
        print(f"      - записал файл={full_path_to_file}")

    return full_path_to_file

#
# print(f"------------os.path.abspath(r'/')      ={os.path.abspath(r'/')}     диск с которго запущен текущий корневой скрипт решения python")
# print(f"------------os.path.abspath('')        = {os.path.abspath('')}      каталог из которого запущен корневой скрипт решения python")
# print(f"------------os.path.abspath('../')     = {os.path.abspath('../')}   каталог выше уровнем текущего корневого скрипта решения Pyерщт")
# print(f"------------os.path.realpath(__file__) = {os.path.realpath(__file__)}  каталог текущего файла py")
#

# os.path.dirname(p) #get dir name
# os.path.basename(p) #get file name
# os.path.splitext(os.path.basename(full_path)) # из полного пути получить имя файла и расширение
# os.path.abspath(os.path.join(PATH_TO_GET_THE_PARENT, os.pardir))   #Получить родительский каталог
# os.path.exists(path) # проверить существует ли путь
# os.path.isdir(dirname) # проверить это директория?
# os.path.isfile(filename)
# os.path.islink(symlink) # проверить что это путь к файлу
