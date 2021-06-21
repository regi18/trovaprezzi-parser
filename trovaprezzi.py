import requests
from urllib.parse import urlparse
from random import choice
from bs4 import BeautifulSoup
import re


def GET_UA():
    uastrings = ["Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.111 Safari/537.36",\
                "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.72 Safari/537.36",\
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10) AppleWebKit/600.1.25 (KHTML, like Gecko) Version/8.0 Safari/600.1.25",\
                "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:33.0) Gecko/20100101 Firefox/33.0",\
                "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.111 Safari/537.36",\
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.111 Safari/537.36",\
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/600.1.17 (KHTML, like Gecko) Version/7.1 Safari/537.85.10",\
                "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko",\
                "Mozilla/5.0 (Windows NT 6.3; WOW64; rv:33.0) Gecko/20100101 Firefox/33.0",\
                "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.104 Safari/537.36"\
                ]

    return choice(uastrings)


def parse_url(url):

    headers = {'User-Agent': GET_UA()}
    content = None
    soup = None

    try:
        response = requests.get(url, headers=headers)
        ct = response.headers['Content-Type'].lower().strip()

        if 'text/html' in ct:
            content = response.content
            soup = BeautifulSoup(content, "html.parser")
        else:
            content = response.content
            soup = None

    except Exception as e:
        print("Error:", str(e))

    return {"content": content, "soup": soup, "contentType": ct}


# clears the log.txt file
open("log.txt", 'w').close()

s = requests.session()
req = []

with open("sites.txt", 'r') as sites:
    for line in sites:
        line = line.rstrip()

        req.append(parse_url(line)["soup"])

        print("[+] URL: " + line)

for doc in req:
    # Saves the base price, the total price (base price + shipping), the product's name and the shop's name
    price_basic = doc.find_all('div', {"class": "item_basic_price"}, limit=3)
    price_total = doc.find_all('div', {"class": "item_total_price"}, limit=3)
    shops = doc.find_all('div', {"class": "merchant_name_and_logo"}, limit=3)
    nome = doc.find('input', {"id": "libera"})
    nome_alt = doc.find('div', {"class": "name_and_rating"})

    # Get the best 3 prices
    price_regex_match = "[0-9]{1,3}(.[0-9]{3})*\,[0-9]+\s?€"
    price_t0 = re.search(price_regex_match, str(price_total[0])).group()
    price_t1 = re.search(price_regex_match, str(price_total[1])).group()
    price_t2 = re.search(price_regex_match, str(price_total[2])).group()

    # Get the relative shops' names
    shop0 = shops[0].find('span', {"class": "merchant_name"}).text
    shop1 = shops[1].find('span', {"class": "merchant_name"}).text
    shop2 = shops[2].find('span', {"class": "merchant_name"}).text

    id0 = str(nome)[str(nome).find("value=") + 7:]
    id0 = id0[:id0.find("\"")]

    # Name not found, try to look elsewhere
    if (id0 == "" and nome_alt):
        nome_s = str(nome_alt.contents)
        id0 = nome_s[(nome_s.find("<h1>") +
                      4):nome_s.find("<strong>")].strip() + " "
        id0 += nome_alt.find("strong").contents[0]

    # Write the results on the log.txt file
    with open("log.txt", 'a') as log:
        # Product's name
        log.write(id0 + "\n")

        # First offer
        log.write(str(price_t0) + " - " + shop0 + "\n")
        # Second offer
        log.write(str(price_t1) + " - " + shop1 + "\n")
        # Third offer
        log.write(str(price_t2) + " - " + shop2 + "\n")

        log.write("-----" + "\n")
        log.close()


# Reads the file on console
with open('log.txt') as f:
    print("\n\n\n\n")
    print(f.read())
    input("Press enter to exit...")
