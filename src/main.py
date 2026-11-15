import requests 
from pathlib import Path 


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


if __name__ == "__main__":
    fetch("https://books.toscrape.com/catalogue/page-1.html","cache/catalogue-page-1.html")