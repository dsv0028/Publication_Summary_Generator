from flask import Flask, render_template, request
from logic import fetch_author_results, safe_get, API_KEY, HL, PAGE_SIZE, FETCH_DELAY

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    results = []
    profile= None
    if request.method == "POST":
        author_id = request.form.get("author_id")
        if author_id:
            data = fetch_author_results(API_KEY, author_id, hl=HL, page_size=PAGE_SIZE, delay=FETCH_DELAY)
            results = [
    {
        "title": safe_get(article, "title", default="No Title"),
        "link": safe_get(article, "link", default="#"),
        "year": safe_get(article, "year", default="N/A"),
        "citations": safe_get(article, "cited_by", "value", default=0),
    }
    for article in data.get("articles", [])
]
            profile = {
    "name": safe_get(data, "author", "name", default="N/A"),
    "affiliations": safe_get(data, "author", "affiliations", default="N/A"),
    "email": safe_get(data, "author", "email", default="N/A"),
    "thumbnail": safe_get(data, "author", "thumbnail", default=""),
    "interests": [i.get("title") for i in safe_get(data, "author", "interests", default=[])],
    "citations_all": safe_get(data, "cited_by", "table", 0, "citations", "all", default=0),
    "citations_recent": safe_get(data, "cited_by", "table", 0, "citations", "since_2020", default=0),
    "h_index": safe_get(data, "cited_by", "table", 1, "h_index", "all", default=0),
    "h_index_recent": safe_get(data, "cited_by", "table", 1, "h_index", "since_2020", default=0),
    "i10_index": safe_get(data, "cited_by", "table", 2, "i10_index", "all", default=0),
    "i10_index_recent": safe_get(data, "cited_by", "table", 2, "i10_index", "since_2020", default=0),
    "open_access_available": safe_get(data, "public_access", "available", default=0),
    "open_access_not_available": safe_get(data, "public_access", "not_available", default=0),
}

    return render_template("index.html", results=results, profile=profile)

if __name__ == "__main__":
    app.run(debug=True)
