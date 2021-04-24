import multiprocessing as mp
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import time
from socket_client import Socket_Client
import json
import pickle

# Insertion at server from 24 to 24 games
def insertAllGames(games):
    url = 'http://localhost:8888/loadGames'
    header = {"content-type": "application/json"}
    data = json.dumps({'array': games})
    res = requests.post(url, data=data, headers=header, verify=False)
    print("NODE_1>Games inserted in server: " + res.text)

# Clean the games list
def deleteAllGames():
    url = 'http://localhost:8888/deleteAllGames'
    res = requests.get(url)
    print("NODE_1>Delete all games in server: " + res.text)


# Get PS5 games by page
def parse(page):
    ps5_list = []
    url = 'https://store.playstation.com/es-cr/category/d71e8e6d-0940-4e03-bd02-404fc7d31a31/' + str(page)

    # Selenium
    options = webdriver.ChromeOptions()
    options.add_argument('--incognito')

    driver = webdriver.Chrome(
        executable_path="../chromedriver", options=options)
    driver.get(url)

    time.sleep(2)

    games = driver.find_elements_by_xpath('/html/body/div[3]/main/section/div/div/ul/li')

    for item in games:
        # url
        game_url = item.find_element_by_xpath('.//div[@class="ems-sdk-product-tile"]/a/div/div/span[2]/img').get_attribute('src')
        modify_url = game_url.split(sep="?")

        # name
        game_name = item.find_element_by_xpath('.//section[@class="ems-sdk-product-tile__details"]/span').text

        # price
        game_price = item.find_element_by_xpath('.//section[@class="ems-sdk-product-tile__details"]/div/span[@class="price"]').text

        newGame = {
            "name": game_name,
            "price": game_price,
            "store": "PlayStation",
            "url": modify_url[0],
            "time": "",
            "meta": ""
        }

        ps5_list.append(newGame)

    driver.close()
    return ps5_list

# 
def prepare_data(page):
    print("NODE_1>Multiprocessing: Working on Page: " + str(page))
    print("NODE_1>Process: "+str(mp.current_process().name))
    block_games = parse(page)
    insertAllGames(block_games)

    # Data ready to start to working with Node 1 & 2
    result = reduce_data(block_games)
    data = pickle.dumps(result)

    # Send by sockets
    if page % 2 == 0:
        client2 = Socket_Client("localhost", 11000, data)
        client2.send()
    else:
        client = Socket_Client("localhost", 10000, data)
        client.send()


# prepare data to secondary nodes
def reduce_data(games):
    res = ""
    size = len(games)
    for game in games:
        res += game['name']+'\\~'+game['price']
        if games.index(game) != (size-1):
            res += '\\^'
    return res


# Get range of games Multiprocessing
def get_ps5_games_multiprocessing(quantity):
    task = []
    for i in range(1, (quantity + 1)):
        task.append(i)
    
    # Multiprocessing
    pool = mp.Pool(mp.cpu_count())
    pool.map(prepare_data, task)
    print("NODE_1>Multiprocessing: All data Sended!")

# Get range of games secuential
def get_ps5_games_secuential(quantity):
    for page in range(1, (quantity + 1)):
        print("NODE_1>Secuential: Working on Page: " + str(page))
        block_games = parse(page)
        insertAllGames(block_games)

        # Data ready to start to working with Node 1 & 2
        result = reduce_data(block_games)
        data = pickle.dumps(result)

        # Send by sockets
        if page % 2 == 0:
            client2 = Socket_Client("localhost", 11000, data)
            client2.send()
        else:
            client = Socket_Client("localhost", 10000, data)
            client.send()

    print("NODE_1>Secuential: All data Sended!")

# Loop to keep update 
def get_data(quantity, multiprocessing, seconds):
    print("\nNODE_1>Update process")
    deleteAllGames()
    if multiprocessing:
        get_ps5_games_multiprocessing(quantity)
    else:
        get_ps5_games_secuential(quantity)
    
    time.sleep(seconds)
    print("NODE_1>Sleep process")
    get_data(quantity, multiprocessing, seconds)

if __name__ == "__main__":
    quantity = 4 # Note: quantity = (quantity * 24)
    multiprocessing = True
    seconds = 300 # Seconds wait to refress data

    get_data(quantity, multiprocessing, seconds)
    print("NODE_1>Finished all process")