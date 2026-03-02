from flask import Flask, render_template, request
import requests
import math

app = Flask(__name__)

# ==========================================
# BOOK MODEL
# ==========================================

class Book:
    def __init__(self, title, subjects, publishers,
                 edition_count, ratings_count,
                 average_rating, link):

        self.title = title
        self.subjects = subjects or []
        self.publishers = publishers or []
        self.edition_count = edition_count or 0
        self.ratings_count = ratings_count or 0
        self.average_rating = average_rating or 0
        self.link = link

        self.popularity = 0
        self.correctness = 0
        self.relevance = 0

    # ---------------------------------
    # Popularity Score
    # ---------------------------------
    def compute_popularity(self):
        self.popularity = min(
            10,
            (self.edition_count * 0.1) +
            (self.ratings_count * 0.02)
        )

    # ---------------------------------
    # Correctness Score
    # ---------------------------------
    def compute_correctness(self):

        publisher_score = min(2, len(self.publishers) * 0.5)
        subject_score = min(2, len(self.subjects) * 0.2)
        rating_score = min(1.5, self.average_rating * 0.5)
        edition_score = min(1.5, self.edition_count * 0.05)

        self.correctness = min(
            5,
            publisher_score +
            subject_score +
            rating_score +
            edition_score
        )

    # ---------------------------------
    # Relevance Score
    # ---------------------------------
    def compute_relevance(self, topic, user_type):

        text = (self.title + " " + " ".join(self.subjects)).lower()
        topic_match = 0.5 if topic.lower() in text else 0.2

        if user_type == "Beginner":
            keywords = ["basic", "introduction", "guide", "fundamentals"]
        elif user_type == "Student":
            keywords = ["theory", "concept", "principle"]
        else:
            keywords = ["advanced", "analysis", "proof", "research"]

        level_boost = sum(0.1 for k in keywords if k in text)

        self.relevance = min(1, topic_match + level_boost)

    # ---------------------------------
    # Final Ranking Formula
    # ---------------------------------
    def final_score(self, topic, user_type):

        self.compute_popularity()
        self.compute_correctness()
        self.compute_relevance(topic, user_type)

        P = self.popularity
        C = self.correctness
        R = self.relevance

        return R * (
            0.5 * math.sqrt(P) +
            0.3 * C +
            0.2 * (P * C)
        )


# ==========================================
# FETCH FROM OPEN LIBRARY
# ==========================================

def fetch_openlibrary(topic):

    url = f"https://openlibrary.org/search.json?q={topic}&limit=20"
    response = requests.get(url)
    data = response.json()

    books = []

    for doc in data.get("docs", []):

        title = doc.get("title")
        if not title:
            continue

        subjects = doc.get("subject", [])
        publishers = doc.get("publisher", [])
        edition_count = doc.get("edition_count", 0)
        ratings_count = doc.get("ratings_count", 0)

        # Open Library link
        key = doc.get("key")
        link = f"https://openlibrary.org{key}" if key else "#"

        book = Book(
            title,
            subjects,
            publishers,
            edition_count,
            ratings_count,
            0,
            link
        )

        books.append(book)

    return books


# ==========================================
# FETCH FROM GOOGLE BOOKS
# ==========================================

def fetch_googlebooks(topic):

    url = f"https://www.googleapis.com/books/v1/volumes?q={topic}&maxResults=20"
    response = requests.get(url)
    data = response.json()

    books = []

    for item in data.get("items", []):

        info = item.get("volumeInfo", {})
        title = info.get("title")

        if not title:
            continue

        subjects = info.get("categories", [])
        publishers = [info.get("publisher")] if info.get("publisher") else []
        edition_count = info.get("ratingsCount", 0)
        ratings_count = info.get("ratingsCount", 0)
        average_rating = info.get("averageRating", 0)

        link = info.get("previewLink", "#")

        book = Book(
            title,
            subjects,
            publishers,
            edition_count,
            ratings_count,
            average_rating,
            link
        )

        books.append(book)

    return books


# ==========================================
# MAIN ROUTE
# ==========================================

@app.route("/", methods=["GET", "POST"])
def index():

    rankings = []

    if request.method == "POST":

        topic = request.form.get("topic")
        source = request.form.get("source")
        user_type = request.form.get("user_type")

        if source == "OpenLibrary":
            books = fetch_openlibrary(topic)
        else:
            books = fetch_googlebooks(topic)

        scored = []

        for book in books:
            score = book.final_score(topic, user_type)

            scored.append({
                "title": book.title,
                "popularity": round(book.popularity, 2),
                "correctness": round(book.correctness, 2),
                "relevance": round(book.relevance, 2),
                "score": round(score, 4),
                "link": book.link
            })

        rankings = sorted(scored, key=lambda x: x["score"], reverse=True)

    return render_template("index.html", rankings=rankings)


if __name__ == "__main__":
    app.run(debug=True)
