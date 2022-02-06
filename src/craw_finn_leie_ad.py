import time
from datetime import date

import pandas as pd
from selenium import webdriver
from selenium.webdriver import FirefoxOptions


def craw_data(driver, data_url):
    data_list = []

    driver.get(data_url)
    time.sleep(2)
    elements = driver.find_elements_by_tag_name("article")

    for e in elements:
        try:
            data = {}
            data["title"] = e.find_elements_by_tag_name("a")[0].text
            data["url"] = e.find_elements_by_tag_name("a")[0].get_attribute("href")
            if e.find_elements_by_class_name("ads__unit__content__details"):
                data["address"] = e.find_elements_by_class_name(
                    "ads__unit__content__details"
                )[0].text
                area_price = e.find_elements_by_class_name("ads__unit__content__keys")[
                    0
                ].text
                data["price"] = area_price.replace(" ", "").replace("kr", "")
            elif e.find_elements_by_class_name("justify-between"):
                search_items = e.find_elements_by_class_name("justify-between")
                data["address"] = search_items[0].text
                data["area"] = search_items[1].text.split("\n")[0].replace(" m²", "")
                data["price"] = (
                    search_items[1]
                    .text.split("\n")[1]
                    .replace(" ", "")
                    .replace("kr", "")
                )
            data_list.append(data)

        except:
            print(f"something wrong with {e.find_elements_by_tag_name('a')[0].text}")
    return data_list


def get_new_data(driver, data_url):
    data_list = {}
    new_data = []
    try:
        finn_data = craw_data(driver, data_url)
        new_data = pd.DataFrame(finn_data)

    except:
        pass
    return new_data


def load_old_data(data_path):
    old_data = pd.read_csv(data_path, sep=",")
    old_data["rent_out"] = old_data["rent_out"].astype(str)
    old_data["rent_date"] = old_data["rent_date"].astype(str)
    return old_data


def load_data(driver, data_url, data_path):
    old_data = load_old_data(data_path)
    new_data = get_new_data(driver, data_url)

    for index, row in new_data.iterrows():

        found_index = old_data.index[old_data["address"] == row["address"]]
        if not found_index.size:
            print("Come new leie ad")
            new_row = {
                "title": row["title"],
                "address": row["address"],
                "area": row["area"],
                "price": row["price"],
                "date": date.today().strftime("%d-%m-%Y"),
                "url": row["url"],
            }
            old_data = old_data.append(new_row, ignore_index=True)
        elif old_data.at[found_index[0], "rent_out"] == "True":
            old_data.at[found_index[0], "rent_out"] == "False"

    for index, row in old_data[old_data["rent_out"] != "True"].iterrows():
        if not new_data.loc[new_data["address"] == row["address"]].size:
            print(f"{row['address']} with price {row['price']} rent out!")
            old_data.at[index, "rent_out"] = "True"
            old_data.at[index, "rent_date"] = date.today().strftime("%d-%m-%Y")

    old_data.to_csv(data_path, index=False)


opts = FirefoxOptions()
opts.add_argument("--headless")
driver = webdriver.Firefox(firefox_binary="/usr/bin/firefox")

hybel_url = "https://www.finn.no/realestate/lettings/search.html?area_from=20&area_to=50&location=1.22030.20045&no_of_bedrooms_from=1&property_type=16&sort=PUBLISHED_DESC&stored-id=53458586"
hybel_datafile = "/home/minshi/workdata/projects/finn_ad/data/hybel.csv"

print(f"download new hybel data from finn")
load_data(driver, hybel_url, hybel_datafile)

hybel_url = "https://www.finn.no/realestate/lettings/search.html?location=1.22030.20045&property_type=1&sort=PUBLISHED_DESC&stored-id=53652541"
hybel_datafile = "/home/minshi/workdata/projects/finn_ad/data/house.csv"

print(f"download new house data from finn")
load_data(driver, hybel_url, hybel_datafile)
