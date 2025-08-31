import time
import requests
from bs4 import BeautifulSoup
import csv

# ---- configuration ----

# HEADERS = HTTP headers to send with every request (to look like a browser)
HEADERS = {"User-Agent": "amr-yasser-learning-bot/1.0"}


# ---- helper: download and parse a web page ----
def get_soup(url):
    """
    Fetch the HTML content from the given URL
    and parse it into a BeautifulSoup object.
    """
    r = requests.get(url, headers=HEADERS, timeout=15)  # send request
    r.raise_for_status()  # raise error if request failed (404, 500, etc.)
    return BeautifulSoup(r.text, "lxml")  # parse HTML with lxml parser


# ---- helper: extract data from one page ----
def parse_page(soup):
    """
    Extract all quotes and authors from a single page.
    Returns a list of dictionaries: [{quote: "...", author: "..."}, ...]
    """
    rows = []
    # Each quote block is inside <div class="quote">
    for q in soup.select("div.quote"):
        text = q.select_one("span.text").get_text(strip=True)    # quote text
        author = q.select_one("small.author").get_text(strip=True)  # author name
        rows.append({"quote": text, "author": author})
    return rows


# ---- helper: find the "next page" link ----
def find_next(soup):
    """
    Looks for the pagination link (<li class="next">).
    If found, returns the absolute URL of the next page.
    Otherwise returns None.
    """
    nxt = soup.select_one("li.next > a")
    return BASE + nxt["href"] if nxt else None


# ---- main scraping loop ----
def scrape(start_url, max_pages=3):
    """
    Crawl starting from 'start_url'.
    Go up to 'max_pages' pages.
    Collect all quotes in a list and return them.
    """
    url = start_url
    all_rows = []
    pages = 0

    # loop until no next page or we hit max_pages
    while url and pages < max_pages:
        print(f"scraping: {url}")
        soup = get_soup(url)                # download + parse
        all_rows.extend(parse_page(soup))   # extract quotes
        url = find_next(soup)               # get next page URL
        pages += 1
        time.sleep(1)  # polite delay between requests

    return all_rows


# ---- entry point: run if this file is executed ----
if __name__ == "__main__":
    # Ask the user to enter a link
    BASE = input("Enter the starting URL (example: https://quotes.toscrape.com): ").strip()
    # start scraping from the base site
    data = scrape(BASE)

    # write the results into a CSV file
    with open("quotes.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["quote", "author"])
        writer.writeheader()
        writer.writerows(data)

    print(f"done! saved {len(data)} quotes")
