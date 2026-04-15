import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE_URL = "https://books.toscrape.com/catalogue/"

def scrape_page(url):
    res = requests.get(url)
    soup = BeautifulSoup(res.text, "html.parser")

    books = []

    for b in soup.select("article.product_pod"):
        books.append({
            "title": b.h3.a["title"],
            "price": b.select_one(".price_color").text,
            "rating": b.p["class"][1],
            "image": urljoin(BASE_URL, b.img["src"].replace("../", ""))
        })

    return books


def scrape_all_books():
    all_books = []

    for i in range(1, 6):
        url = f"https://books.toscrape.com/catalogue/page-{i}.html"
        all_books.extend(scrape_page(url))

    return all_books