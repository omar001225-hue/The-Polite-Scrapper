import requests 
from pathlib import Path 
import time

from bs4 import BeautifulSoup # stage 2 
from urllib.parse import urljoin # stage 2 

Header = {"User-Agent": "The-Polite-Scrapper (+https://github.com/omar001225-hue/The-Polite-Scrapper)"}  # Obviously , communication is done via JSON type , so we send a header in JSON format , containing our user agent

class FetchError(Exception):
    pass


# function will fetch the url and , check if there is already a cache file , if it does it exists , it will print the lenght of the text in it as a response 
# if not , it will fetch the text again from the site , and then produce the same response 

def fetch(url , cache_file):

    cache_file = Path(cache_file)

    if cache_file.exists():

        html = cache_file.read_text(encoding="utf-8")
        print(f"Cache Hit : {url} ({len(html)} chars)")
        return html

    resp = requests.get(url , headers=Header ,timeout= 10)  # Get request at the URL , with out introduction header , and a timeout condition for waiting 
    
    if resp.status_code != 200 :
        raise FetchError(f"{url} -> {resp.status_code}")

    html = resp.content.decode("utf-8")

    cache_file.parent.mkdir(exist_ok=True)
    cache_file.write_text(html, encoding="utf-8")

    print(f"Fetched {url} ({len(html)} chars)")
    return html 


# stage 2 function 


def discover( start_url ):
    page_url = start_url
    pages = 0 
    pairs=[]

    while page_url and pages < 3 :
        pages +=1 
        cache_file = f"cache/catalogue-page-{pages}.html"
        was_cached = Path(cache_file).exists()

        html = fetch(page_url , cache_file)

        if not was_cached :
            time.sleep(0.6)

        soup = BeautifulSoup(html , "html.parser")

        for a in soup.select("article.product_pod h3 a "):
            pairs.append((urljoin(page_url , a["href"]) , page_url))

        next = soup.select_one("li.next a ")

        if next : 
            page_url = urljoin(page_url , next["href"])
        
        else :
            None

    unique = {}
    for book_url , source in pairs :
        unique.setdefault(book_url , source)
    
    return pages, len(pairs), list(unique.items())








if __name__ == "__main__":
    pages, discovered, unique_pairs = discover("https://books.toscrape.com/catalogue/page-1.html")
    print(f"catalogue_pages={pages}, discovered={discovered}, unique_urls={len(unique_pairs)}")
