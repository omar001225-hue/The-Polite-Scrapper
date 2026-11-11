# The Polite Scraper

A small, polite scraping pipeline for the FlyRank Internship (Backend Track, Week 5, Assignment A9). It downloads the first three catalogue pages of Books to Scrape, visits every book page, and turns the HTML into clean, validated JSON.

## Target classification

- **Site:** Books to Scrape (https://books.toscrape.com), part of toscrape.com.
- **Why this site:** toscrape.com states that it is a sandbox built for people to practise web scraping on. That statement is the permission to scrape it.
- **Scope:** the first 3 catalogue pages only, which link to 60 book pages. Nothing beyond that.
- **Data collected:** title, product URL, price, availability, rating, description, source page, and fetch time. It is a fake bookshop, so there is no personal data.
- **robots.txt result:** requested once, got HTTP 404 (no robots file found). A missing file is not permission, so permission rests on the sandbox statement above.
- **Why this is appropriate:** it is a public practice sandbox made for exactly this purpose, and I access it at a low, polite rate (honest user-agent, timeout, delay between requests, local cache).

We will not reuse this code on another site without checking its rules and terms first.