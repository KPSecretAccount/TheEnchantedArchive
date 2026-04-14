import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE_URL = "https://books.toscrape.com/catalogue/"
START_URL = "https://books.toscrape.com/catalogue/page-1.html"


def scrape_page(url):
    response = requests.get(url, timeout=10)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    books = []

    for book in soup.select("article.product_pod"):
        title = book.h3.a["title"]
        price = book.select_one("p.price_color").text.strip()
        rating = book.select_one("p.star-rating")["class"][1]
        image_path = book.img["src"].replace("../", "")
        image = urljoin(BASE_URL, image_path)

        books.append({
            "title": title,
            "price": price,
            "rating": rating,
            "image": image
        })

    return books


def scrape_all_books(total_pages=50):
    all_books = []

    for page in range(1, total_pages + 1):
        url = f"https://books.toscrape.com/catalogue/page-{page}.html"
        try:
            books = scrape_page(url)
            all_books.extend(books)
            print(f"Scraped page {page}: {len(books)} books")
        except requests.RequestException as error:
            print(f"Failed on page {page}: {error}")

    return all_books


if __name__ == "__main__":
    books = scrape_all_books()
    print(f"Total books scraped: {len(books)}")
    print(books[:5])