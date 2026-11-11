import requests 

url = "https://books.toscrape.com/robots.txt"
headers = {"User-Agent": "The-Polite-Scrapper (+https://github.com/omar001225-hue/The-Polite-Scrapper)"}

response = requests.get(url , headers=headers , timeout = 10)

print("Status :   ", response.status_code)
print(response.text[:500])

