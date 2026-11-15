import requests 
from pathlib import Path 
import time

from datetime import datetime, timezone


from bs4 import BeautifulSoup # stage 2 
from urllib.parse import urljoin # stage 2 

import re, json # stage 4 
from pydantic import BaseModel, HttpUrl, ValidationError # stage 4 
from typing import Optional # stage 4 


Header = {"User-Agent": "The-Polite-Scrapper (+https://github.com/omar001225-hue/The-Polite-Scrapper)"}  # Obviously , communication is done via JSON type , so we send a header in JSON format , containing our user agent

class FetchError(Exception):
    pass


# function will fetch the url and , check if there is already a cache file , if it does it exists , it will print the lenght of the text in it as a response 
# if not , it will fetch the text again from the site , and then produce the same response 

STATS = {"pages_fetched": 0, "cache_hits": 0}


class FetchError(Exception):
    def __init__(self, message, status=None):
        super().__init__(message)
        self.status = status          # lets us tell a 404 from a 500


def fetch(url, cache_file):
    cache_file = Path(cache_file)
    if cache_file.exists():
        html = cache_file.read_text(encoding="utf-8")
        STATS["cache_hits"] += 1
        print(f"CACHE HIT {url} ({len(html)} chars)")
        return html
    resp = requests.get(url, headers=HEADERS, timeout=10)
    time.sleep(0.6)                   # polite delay after every real request
    if resp.status_code != 200:
        raise FetchError(f"{url} -> {resp.status_code}", status=resp.status_code)
    html = resp.content.decode("utf-8")
    cache_file.parent.mkdir(parents=True, exist_ok=True)
    cache_file.write_text(html, encoding="utf-8")
    STATS["pages_fetched"] += 1
    print(f"FETCH {url} ({len(html)} chars)")
    return html


def fetch_with_retry(url, cache_file):
    try:
        return fetch(url, cache_file)
    except (requests.Timeout, requests.ConnectionError):
        pass                                      # retryable, fall through
    except FetchError as e:
        if e.status is None or e.status < 500:    # 404, 403, etc: do NOT retry
            raise
    print(f"RETRY {url}")
    time.sleep(2)
    return fetch(url, cache_file)                 # one more try, errors now propagate


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


def extract(html, product_url, source_page):
    soup = BeautifulSoup(html, "html.parser")
    product = soup.select_one("div.product_main")
    desc_header = soup.select_one("#product_description")
    return {
        "title": product.h1.get_text(strip=True),
        "product_url": product_url,
        "price_text": product.select_one("p.price_color").get_text(strip=True),
        "availability_text": product.select_one("p.availability").get_text(" ", strip=True),
        "rating_text": product.select_one("p.star-rating")["class"][1],
        "description": desc_header.find_next_sibling("p").get_text(strip=True) if desc_header else None,
        "source_page": source_page,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
    }


class Book(BaseModel):
    title: str
    product_url: HttpUrl
    price_text: str
    price_gbp: float
    availability_text: str
    rating_text: str
    description: Optional[str] = None
    source_page: HttpUrl
    fetched_at: str


def normalize(raw):
    raw = dict(raw)
    raw["price_gbp"] = float(re.sub(r"[^\d.]", "", raw["price_text"]))
    return raw
















if __name__ == "__main__":
    start = datetime.now(timezone.utc)
    t0 = time.perf_counter()

    pages, discovered, unique_pairs = discover("https://books.toscrape.com/catalogue/page-1.html")
    print(f"catalogue_pages={pages}, discovered={discovered}, unique_urls={len(unique_pairs)}")

    # Removed TEMPORARY failure test: remove this line after proving it works

    raw_records = []
    failed = []
    for i, (book_url, source_page) in enumerate(unique_pairs, start=1):
        try:
            html = fetch_with_retry(book_url, f"cache/book-{i}.html")
            raw_records.append(extract(html, book_url, source_page))
        except Exception as e:
            print(f"FAILED {book_url}: {e}")
            failed.append({"url": book_url, "reason": str(e)})

    print(f"detail_pages={len(raw_records)}")

    good = {}
    errors = []
    for raw in raw_records:
        try:
            book = Book(**normalize(raw))
            good[str(book.product_url)] = book.model_dump(mode="json")
        except (ValidationError, ValueError, KeyError) as e:
            errors.append({"record": raw, "reason": str(e)})

    Path("output").mkdir(exist_ok=True)
    Path("output/books.json").write_text(
        json.dumps(list(good.values()), indent=2, ensure_ascii=False), encoding="utf-8")
    Path("output/errors.json").write_text(
        json.dumps(errors, indent=2, ensure_ascii=False), encoding="utf-8")

    report = {
        "start_time": start.isoformat(),
        "duration_seconds": round(time.perf_counter() - t0, 2),
        "pages_fetched": STATS["pages_fetched"],
        "cache_hits": STATS["cache_hits"],
        "valid_records": len(good),
        "invalid_records": len(errors),
        "failed_pages": len(failed),
    }
    Path("output/run-report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(report)