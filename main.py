from bs4 import BeautifulSoup

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary

import pandas as pd
import numpy as np
import csv
import os
import path
import datetime
from datetime import datetime

urldf = pd.read_csv("patch_all_cities_state_remove_duplicate_4_8_2022.csv")

binary = FirefoxBinary('path/to/firefox.exe')
driver = webdriver.Firefox(firefox_binary=binary)
# driver = webdriver.Firefox(executable_path="./geckodriver")

my_list = []
# start 61

# start_i = input("Enter start index: ")
# end_i = input("Enter end index : ")

# print(start_i)
# print(end_i)

for i in range(70, 100):
    sub = urldf['url'][i]
    print(sub)
    sub_split = sub.split("/")

    state = sub_split[3]
    print(state)

    city = sub_split[4]
    master_url = "https://web.archive.org/web/20201101000000*/"+sub+"/politics"
    print(master_url)
    # initiating the webdriver. Parameter includes the path of the webdriver.
    driver = webdriver.Chrome('./chromedriver')
    # driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

    driver.get(master_url)
    time.sleep(7)

    mast = []
    elems = driver.find_elements_by_tag_name('a')
    for elem in elems:
        href = elem.get_attribute('href')
        if href is not None:
            if(sub in href and ("2020" in href) and ("*" not in href)):
                print(href)
                mast.append(href)
    driver.close()  # close out the driver for get the master list

    res_json = {}
    data = []
    df = pd.DataFrame(data, columns=[
        'url', 'Date', 'Title', 'Thank', 'Reply', 'author', 'title', 'context'])  # initial df to collect all articles c

    article_set_city_state = set()
    for url in mast:
        print(url)
#             url = "https://web.archive.org/web/"+date +"/" + sub + "/politics"
        driver = webdriver.Chrome('./chromedriver')
        driver.get(url)
        time.sleep(7)
        try:
            json = driver.execute_script("return __NEXT_DATA__")
            main_content = json['props']['pageProps']['mainContent']
            if ("topicFeed" in main_content):
                sub_list = json['props']['pageProps']['mainContent']['topicFeed']
            else:
                sub_list = json['props']['pageProps']['mainContent']['feedData']
            for li in sub_list:
                if(len(li) > 17):
                    url = li['canonicalUrl']
                    date = li['created']
                    title = li['shortTitle']
                    thank = li['flags']['thankCount']
                    reply = li['totalReplies']

                    suburl = "https://patch.com/" + url

                    if suburl not in article_set_city_state:
                        driver2 = webdriver.Chrome('./chromedriver')
                        driver2.get(suburl)
                        time.sleep(7)

                        print(suburl + "\n")

                        context_elements = driver2.find_elements(
                            By.TAG_NAME, 'p')
                        str_ = ""

                        for i in range(0, len(context_elements)-4):
                            if i == 0:
                                str_ = context_elements[0].text
                            else:
                                str_ = str_ + "\n" + context_elements[i].text
        #                     print("str_ = " + str_ + "\n")

                        elements_author_title = driver2.find_elements(
                            By.TAG_NAME, 'h6')

                        author_name_title_temp = elements_author_title[1].text
                        if("," in author_name_title_temp):
                            author_name_temp = author_name_title_temp.split(',')[
                                0]
                            if("By" in author_name_temp):
                                author_name_temp = author_name_temp[len(
                                    "By "):]

                            author_title_temp = author_name_title_temp.split(',')[
                                1]
                            author_title_temp = author_title_temp[len(" "):]
                        else:
                            author_name_temp = elements_author_title[1].text
                            author_title_temp = elements_author_title[2].text
        #                     print("author_name_temp = " + author_name_temp + "\n")
        #                     print("author_title_temp = " + author_title_temp + "\n")

                        driver2.close()

                        df2 = {'url': url, 'Date': date, 'Title': title, 'Thank': thank, 'Reply': reply,
                               'author': author_name_temp, 'title': author_title_temp, "context": str_}

                        df = df.append(df2, ignore_index=True)
                        article_set_city_state.add(suburl)
        except:
            error_cities_states = [city, state, url]
            my_list.append(error_cities_states)

        driver.close()  # close out driver for all url as city state in mast list

    # finish off the result and put the res list in a csv file
    dirsname = "results"
    if not os.path.exists(dirsname):
        os.makedirs(dirsname)
    cwd = os.getcwd()
    path = os.path.join(dirsname, "out_"+city+"_"+state +
                        "_2020_complete_political.csv")
    path = os.path.join(cwd, path)
    print(path)
    df.to_csv(path)      # end of all url

#         except:
#             print("An exception occurred")
#             error_cities_states = [city,state, url]
#             my_list.append(error_cities_states)
#             print(sub)


 # finish off the result and put the res list in a csv file
    dirsname = "results"
    if not os.path.exists(dirsname):
        os.makedirs(dirsname)
    cwd = os.getcwd()
    path = os.path.join(dirsname, "out_"+city+"_"+state +
                        "_2020_complete_political.csv")
    path = os.path.join(cwd, path)
    print(path)
    df.to_csv(path,  encoding='utf-8')

# end of all cities
# print all error cities


now = datetime.now() # current date and time
dirsname = "error_log"
if not os.path.exists(dirsname):
    os.makedirs(dirsname)


filename =  "errors_log_"+now.strftime("%m%d%Y_%H%M%S")+".csv";
print(filename)
csvlogPath = os.path.join(dirsname,filename)


# end of all cities
# print all error cities
with open(csvlogPath, 'w') as f:

    # using csv.writer method from CSV package
    writer = csv.writer(f);
    writer.writerows(my_list)
