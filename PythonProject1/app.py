from flask import Flask, render_template, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
from encryption import encrypt_review, decrypt_review
import json, os, requests

app = Flask(__name__)
app.secret_key = "change-this-key"

USERS_FILE = "users.json"
REVIEWS_FILE = "reviews.json"


# INIT FILES
def init(file):
    if not os.path.exists(file):
        with open(file, "w") as f:
            json.dump([], f)

init(USERS_FILE)
init(REVIEWS_FILE)


def load(file):
    try:
        with open(file, "r") as f:
            return json.load(f)
    except:
        return []

def save(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=2)


#  BOOK SEARCH

def search_books(query):
    url = "https://openlibrary.org/search.json"
    res = requests.get(url, params={"q": query})

    if res.status_code != 200:
        return []

    data = res.json()
    books = []

    for item in data.get("docs", [])[:10]:
        books.append({ "title": item.get("title", "No title"), "author": ", ".join(item.get("author_name", ["Unknown"]))})

    return books


#  HOME SEARCH

@app.route("/", methods=["GET", "POST"])
def home():
    books = []

    if request.method == "POST":
        books = search_books(request.form.get("search", ""))

    return render_template("home.html", books=books)


# SIGNUP (NO DUPLICATES)
@app.route("/signup", methods=["GET", "POST"])
def signup():
    error = None

    if request.method == "POST":
        users = load(USERS_FILE)

        username = request.form["username"]
        password = request.form["password"]

        for u in users:
            if u["username"].lower() == username.lower():
                error = "Username already exists"
                return render_template("signup.html", error=error)

        hashed = generate_password_hash(password)

        users.append({
            "username": username,
            "password": hashed
        })

        save(USERS_FILE, users)

        session["user"] = username

        return redirect("/")

    return render_template("signup.html", error=error)

#  LOGIN (REAL CHECK)
@app.route("/login", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        users = load(USERS_FILE)

        username = request.form["username"]
        password = request.form["password"]

        for u in users:
            if u["username"] == username:

                if check_password_hash(u["password"], password):
                    session["user"] = username

                    next_page = request.form.get("next")

                    if next_page:
                        return redirect(next_page)

                    return redirect("/")

                else:
                    error = "Wrong password"
                    return render_template("login.html", error=error)

        return render_template("login.html", error="User not found")

    return render_template("login.html", error=error)
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/check_username")
def check_username():
    username = request.args.get("username", "").lower()

    users = load(USERS_FILE)

    for u in users:
        if u["username"].lower() == username:
            return {"exists": True}

    return {"exists": False}

#  BOOK PAGE

@app.route("/book/<name>", methods=["GET", "POST"])
def book(name):
    reviews = load(REVIEWS_FILE)

    if request.method == "POST":

        rating = int(request.form["rating"])
        review_text = request.form["review"]
        privacy = request.form["privacy"]

        # only logged-in users can do private
        if privacy == "private" and "user" not in session:
            return "You must sign in to write private reviews"

        if privacy == "private":
            review_text = encrypt_review(review_text)

        reviews.append({
            "user": session.get("user", "Anonymous"),
            "book": name,
            "rating": rating,
            "review": review_text,
            "privacy": privacy
        })

        save(REVIEWS_FILE, reviews)

        return redirect(f"/book/{name}")

    book_reviews = []
    ratings = []

    for r in reviews:
        if r["book"] == name:
            ratings.append(int(r["rating"]))

            if r["privacy"] == "private":
                text = decrypt_review(r["review"])
            else:
                text = r["review"]

            book_reviews.append({
                "user": r["user"],
                "rating": r["rating"],
                "review": text
            })

    avg = round(sum(ratings) / len(ratings), 1) if ratings else "N/A"

    return render_template("book.html", name=name, reviews=book_reviews, avg=avg)

#PROFILE
@app.route("/profile")
def profile():

    if "user" not in session:
        return redirect("/login")

    reviews = load(REVIEWS_FILE)

    user_reviews = []

    for r in reviews:

        if r["user"] == session["user"]:

            review_text = r["review"]

            # decrypt own private reviews
            if r["privacy"] == "private":
                review_text = decrypt_review(r["review"])

            user_reviews.append({
                "book": r["book"],
                "rating": r["rating"],
                "review": review_text,
                "privacy": r["privacy"]
            })

    return render_template(
        "profile.html",
        username=session["user"],
        reviews=user_reviews
    )


if __name__ == "__main__":
    app.run(debug=True)