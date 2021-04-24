import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import time

def search(name):
    url = 'https://www.amazon.com/s?i=videogames-intl-ship&bbn=16225016011&rh=n%3A20972781011%2Cn%3A20972797011%2Cp_89%3APlaystation&dc&language=es&fst=as%3Aoff&pf_rd_i=16225016011&pf_rd_m=ATVPDKIKX0DER&pf_rd_p=e963b29d-d654-4995-bbb2-582c8cfbb5e4&pf_rd_r=0E6CBDMYSY2Z4QW1EYKE&pf_rd_s=merchandised-search-3&pf_rd_t=101&qid=1619289230&rnid=20972781011&ref=sr_nr_n_3'

    # Selenium
    options = webdriver.ChromeOptions()
    options.add_argument('--incognito')

    driver = webdriver.Chrome(
        executable_path="../chromedriver", options=options)
    driver.get(url)

    time.sleep(2)

    searchTextBox = driver.find_element_by_id('twotabsearchtextbox')
    searchTextBox.clear()
    searchTextBox.send_keys(name)

    searchBtn = driver.find_element_by_id('nav-search-submit-button')
    searchBtn.click()

    # Amazon changes the search category when it can't find the item
    searchCategory = driver.find_element_by_id('nav-search-label-id')

    # Item
    price_whole = driver.find_element_by_xpath('//*[@id="search"]/div[1]/div/div[1]/div/span[3]/div[2]/div[1]/div/span/div/div/div[2]/div[2]/div/div[2]/div[1]/div/div[1]/div[2]/a/span/span[2]/span[2]')
    price_fraction = driver.find_element_by_xpath('//*[@id="search"]/div[1]/div/div[1]/div/span[3]/div[2]/div[1]/div/span/div/div/div[2]/div[2]/div/div[2]/div[1]/div/div[1]/div[2]/a/span/span[2]/span[3]')

    if (searchCategory.text != "Juegos de PlayStation 5"):
        print("No se encontro el elemento solicitado")
    else:
        print(price_whole.text)
        print(price_fraction.text)


search("Demon's Souls")