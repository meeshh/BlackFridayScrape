import requests
import json
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from product import Product
from utils import convert_price_toNumber
from web_driver_conf import get_web_driver_options
from web_driver_conf import get_chrome_web_driver
from web_driver_conf import set_ignore_certificate_error
from web_driver_conf import set_browser_as_incognito
from web_driver_conf import set_automation_as_head_less

NUMBER_OF_PAGES_TO_SEARCH = 3
QUESTION_PRODUCT = "What are you looking for?\n:"
search_term = str(input(QUESTION_PRODUCT))  # changed input to raw_input
URL = "http://www.euronics.lv/products-en"
query = "?query=" + search_term.replace(' ', '+')


options = get_web_driver_options()
set_automation_as_head_less(options)
set_ignore_certificate_error(options)
set_browser_as_incognito(options)
driver = get_chrome_web_driver(options)


products = []
elements = []
page = NUMBER_OF_PAGES_TO_SEARCH

biggest_discount = 0.0
lowest_price = 0.0
cheepest_product = Product("", "", "", "")
best_deal_product = Product("", "", "", "")
search_terms = search_term.split(" ")

# driver.get(URL+"/"+str(page)+query)
# elements = driver.find_elements_by_class_name("product")


while True:
    elements = []
    if page == 0:
        print('---------DONE----------')
        break
    else:
        try:
            driver.get(URL+"/nr/"+str(page)+query)
            elements = driver.find_elements_by_class_name("product")
        except:
            break

    print('Searching page ' + str(page))

    for element in elements:
        # counter = 0
        should_add = True
        name_and_link = element.find_element_by_class_name("name")

        name = name_and_link.find_element_by_tag_name('span').text

        for word in search_term.split((' ')):
            if word.lower() not in name.lower():
                should_add = False

        priceTemp = element.find_element_by_class_name(
            "price").text.split(' \u20ac')[0]

        price = 0.0 if priceTemp.strip() == "" else float(priceTemp)

        if price == 0.0:
            should_add = False

        priceClasses = element.find_element_by_class_name(
            "price").get_attribute('class')

        prev_price = float(element.find_element_by_css_selector(
            "p.price.discount").find_elements_by_tag_name("span")[1].text.split('Normal price ')[1].replace(' \u20ac', '')) if 'discount' in priceClasses else price

        link = name_and_link.find_element_by_tag_name(
            "a").get_attribute("href")

        product = Product(name, price, prev_price, link)
        if should_add:
            products.append(product)

    page = page - 1

run = 0

driver.close()
driver.quit()

for product in products:
    not_right = False

    if not not_right:
        if run == 0:
            lowest_price = product.price
            cheepest_product = product
            run = 1
        elif product.price < lowest_price:
            lowest_price = product.price
            cheepest_product = product
        discount = product.prev_price - product.price
        if discount > biggest_discount:
            biggest_discount = discount
            best_deal_product = product

with open('products.json', 'w') as json_file:
    data = {}
    data["products"] = []
    for prod in products:
        data["products"].append(prod.serialize())
    json.dump(data, json_file, sort_keys=True, indent=4)

print(json.dumps(cheepest_product.serialize(), indent=4, sort_keys=True))
print(json.dumps(best_deal_product.serialize(), indent=4, sort_keys=True))

options = get_web_driver_options()
set_ignore_certificate_error(options)
driver = get_chrome_web_driver(options)

driver.get(cheepest_product.link)
driver.find_element_by_tag_name('body').send_keys(Keys.COMMAND + 't')
