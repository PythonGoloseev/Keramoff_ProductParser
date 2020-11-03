
# def isNoneOrEmptyOrBlankString (myString):
#     if myString:
#         if not myString.strip():
#             return True
#         else:
#             return False
#     return False

def is_empty(str):
    if str == None or str.strip() == "":
        result = True
    else:
        result = False
    return(result)


def decor_red():
    #подробнее https://all-python.ru/osnovy/tsvetnoj-vyvod-teksta.html
    return("\033[31m")

def decor_yellow():
    #https://all-python.ru/osnovy/tsvetnoj-vyvod-teksta.html
    return("\033[33m")

def decor_blue():
    #https://all-python.ru/osnovy/tsvetnoj-vyvod-teksta.html
    return("\033[34m")

def decor_green():
    #https://all-python.ru/osnovy/tsvetnoj-vyvod-teksta.html
    return("\033[32m")

def decor_fuksi():
    #https://all-python.ru/osnovy/tsvetnoj-vyvod-teksta.html
    return("\033[35m")


def decor_bold():
    #https://all-python.ru/osnovy/tsvetnoj-vyvod-teksta.html
    return("\033[1m")

def decor_default():
    #https://all-python.ru/osnovy/tsvetnoj-vyvod-teksta.html
    return("\033[0m")

def print_red(text):
    print(f"{decor_red()}{text}{decor_default()}")

def print_green(text):
    print(f"{decor_green()}{text}{decor_default()}")

def print_black(text):
    print(f"{decor_default()}{text}{decor_default()}")

def print_fuksi(text):
    print(f"{decor_fuksi()}{text}{decor_default()}")

def print_blue(text):
    print(f"{decor_blue()}{text}{decor_default()}")

def print_yellow(text):
    print(f"{decor_yellow()}{text}{decor_default()}")

def format_dict(dict):
    import json
    result = json.dumps(dict, indent=4, sort_keys=True)
    return result

def remove_spec_chars(text):

    bad_chars = []
    for kod_ord in range(1,32):
        bad_chars.append(chr(kod_ord))

    # using filter() to
    # remove bad_chars
    result_string = filter(lambda i: i not in bad_chars, text)

    result_string = "".join(result_string)

    return result_string


