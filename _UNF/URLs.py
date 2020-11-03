
from urllib.parse import urlparse  # python 3.x

def get_base_domain(url, with_http_prefiks=True):
    # This causes an HTTP request; if your script is running more than,
    # say, once a day, you'd want to cache it yourself.  Make sure you
    # update frequently, though!

    hostname = urlparse(url).hostname

    if with_http_prefiks == True and hostname != "" and hostname != None:
        parts = url.partition(hostname)
        res_str = parts[0] + hostname
    else:
        res_str = hostname

    return res_str

def convert_url_to_file_name(url, remove_domain = True):

    if url == None:
        return None

    result_file_name = url.strip()

    if remove_domain:
        cur_domain = get_base_domain(url)
        if cur_domain != None and cur_domain.strip() != "":
            # print(f"cur_domain={cur_domain}")
            right_part = result_file_name.partition(cur_domain)[2]
            # print(f"right_part={right_part}")
            if right_part.strip() != "":
                result_file_name = right_part.strip()

    result_file_name = result_file_name.replace("/", "_")
    result_file_name = result_file_name.replace("?", "_")
    result_file_name = result_file_name.replace("&", "_")
    result_file_name = result_file_name.replace(":", "_")

    # print(f"result_file_name={result_file_name}")
    return(result_file_name)

