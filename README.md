# web_scrape_python
Scraping web pages to get data for WoW Stats app:

https://troz.net/wow-stats/



Based on https://realpython.com/python-web-scraping-practical-introduction/



Requires `requests` and `BeautifulSoup`:

```bash
pip install requests BeautifulSoup4
```



Uses http://www.noxxic.com/wow/ to get a list of character class and specs.

Then construct the URL for each type and web scrapes the relevant data out of each page.

