import time
from serpapi import GoogleSearch


API_KEY = "daf8b5b7b49a653e8ab557d4b5cab8b3737269703389193f6fd5cad180fe83b8"
HL = "en"
PAGE_SIZE = 20
FETCH_DELAY = 0.8

def fetch_author_results(api_key, author_id, hl="en", page_size=20, delay=1.0):
    all_articles = []
    start = 0
    last_results = None

    while True:
        params = {
            "engine": "google_scholar_author",
            "author_id": author_id,
            "hl": hl,
            "api_key": api_key,
            "start": start,
        }

        search = GoogleSearch(params)
        results = search.get_dict()
        last_results = results

        articles = results.get("articles", [])
        if not articles:
            break

        all_articles.extend(articles)

        serpapi_pagination = results.get("serpapi_pagination", {})
        if not serpapi_pagination.get("next") or len(articles) < page_size:
            break

        start += page_size
        time.sleep(delay)

    combined = (last_results or {}).copy()
    combined["articles"] = all_articles
    return combined

def safe_get(dct, *keys, default=None):
    cur = dct
    try:
        for k in keys:
            cur = cur[k]
        return cur
    except Exception:
        return default


