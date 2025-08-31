import time
from serpapi import GoogleSearch
import google.generativeai as genai

API_KEY = "daf8b5b7b49a653e8ab557d4b5cab8b3737269703389193f6fd5cad180fe83b8"
HL = "en"
PAGE_SIZE = 20
FETCH_DELAY = 0.8

genai.configure(api_key="AIzaSyDc0yJC6JV3DidwdvyXlL-8iQlMjfxS0f4") 
model = genai.GenerativeModel('gemini-1.5-flash-latest')


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

def generate_author_summary(api_key, author_id):
    data = fetch_author_results(api_key, author_id, hl=HL, page_size=PAGE_SIZE, delay=FETCH_DELAY)

    # Sort by citations safely
    articles = sorted(
        data.get("articles", []),
        key=lambda x: x.get("cited_by", {}).get("value") or 0,
        reverse=True
    )

    
    top_articles = articles[:30]

    
    article_text = "\n".join(
        f"{a.get('title', 'No Title')} ({a.get('year', 'N/A')}), "
        f"Citations: {a.get('cited_by', {}).get('value', 0)}"
        for a in top_articles
    )

    prompt = f"""
    Author Profile:
    Name: {safe_get(data, 'author', 'name', default='N/A')}
    Affiliation: {safe_get(data, 'author', 'affiliations', default='N/A')}
    Interests: {", ".join([i.get("title") for i in safe_get(data, 'author', 'interests', default=[])])}

    Articles (Top {len(top_articles)}):
    {article_text}

    Please generate a concise research profile summary.
    """

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"[WARN] Gemini failed: {e}")
        return (
            f"Could not generate AI summary.\n\n"
            f"Here are the top {len(top_articles)} articles:\n" + article_text
        )

