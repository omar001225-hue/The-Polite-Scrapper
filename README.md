# The Polite Scraper

A small scraping pipeline for Books to Scrape. It fetches catalogue pages, extracts book details, cleans the data, validates it, stores it as JSON, and writes a report of every run.

Pipeline: fetch → extract → normalize → validate → store → report

## Target classification

- **Site:** https://books.toscrape.com, part of toscrape.com, which describes itself as a sandbox built for practising web scraping.
- **Scope:** the first 3 catalogue pages only, which gives 60 book pages.
- **Data collected:** title, price, availability, star rating, description, plus the source page URL and the time of the fetch.
- **robots.txt:** [KEEP ONE: "I requested https://books.toscrape.com/robots.txt once and got a 404, so no robots file was found. A missing file is not permission, but the site's own sandbox statement is." OR "I requested robots.txt once and it said: ..."]
- **Why this is appropriate:** the site exists specifically for scraping practice, the scope is small, and I only collect public product data at a slow pace.

I will not reuse this code on another site without checking its rules and terms first.

## Install and run

Lane: Python 3.10+ with requests, Beautiful Soup and Pydantic.

```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python src/main.py
```

On macOS/Linux, activate with `source venv/bin/activate` instead.

The first run makes about 63 real requests and takes under a minute. Later runs read from the local `cache/` folder and finish almost instantly. Output goes to:

- `output/books.json`: the 60 validated records
- `output/errors.json`: records that failed validation, with the reason
- `output/run-report.json`: a summary of the run

## Record schema

| Field | Type | Notes |
|---|---|---|
| title | string | required |
| product_url | https URL | required, used as the record's identity |
| price_text | string | original text, e.g. "£51.77" |
| price_gbp | number | cleaned value, e.g. 51.77 |
| availability_text | string | e.g. "In stock (22 available)" |
| rating_text | string | e.g. "Three" |
| description | string or null | optional, null when the page has none |
| source_page | https URL | catalogue page the book was found on |
| fetched_at | string | UTC timestamp of the fetch |

Every record is validated with a Pydantic model before it is stored. Records that fail go to `errors.json` and never reach `books.json`.

## Politeness rules

- An honest User-Agent that names the project and links to this repo
- A 10 second timeout on every request
- A 0.6 second delay after every real request (cache hits need no delay)
- Pages are cached in `cache/`, so reruns do not hit the site again
- One retry only on a timeout or a 5xx error. A 404 or 403 is never retried.
- One broken page is logged and skipped, and the rest of the run continues

##