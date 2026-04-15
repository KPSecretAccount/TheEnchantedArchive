from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from models import db, User, Favorite, Review, Style
from scraper import scrape_all_books
from sqlalchemy import func

app = Flask(__name__)
app.secret_key = "secret123"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///books.db'
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

all_books = scrape_all_books()

@app.route('/')
def home():
    query = request.args.get('q', '')

    books = [b for b in all_books if query.lower() in b['title'].lower()]

    favorites = []
    styles = {}

    if current_user.is_authenticated:
        favorites = [f.book_title for f in Favorite.query.filter_by(user_id=current_user.id)]

        user_styles = Style.query.filter_by(user_id=current_user.id).all()
        styles = {s.book_title: s for s in user_styles}

    averages = dict(
        db.session.query(
            Review.book_title,
            func.avg(Review.rating)
        ).group_by(Review.book_title).all()
    )

    return render_template(
        "index.html",
        books=books,
        query=query,
        favorites=favorites,
        styles=styles,
        averages=averages
    )

@app.route('/favorite/<path:title>')
@login_required
def favorite(title):
    existing = Favorite.query.filter_by(user_id=current_user.id, book_title=title).first()

    if existing:
        db.session.delete(existing)
    else:
        db.session.add(Favorite(user_id=current_user.id, book_title=title))

    db.session.commit()
    return redirect(url_for('home'))

@app.route('/book/<path:title>', methods=['GET', 'POST'])
def book(title):
    book = next((b for b in all_books if b['title'] == title), None)

    if request.method == 'POST' and current_user.is_authenticated:
        review = Review(
            user_id=current_user.id,
            book_title=title,
            rating=int(request.form['rating']),
            comment=request.form['comment']
        )
        db.session.add(review)
        db.session.commit()

    reviews = Review.query.filter_by(book_title=title).all()

    return render_template("book.html", book=book, reviews=reviews)

@app.route('/save_style', methods=['POST'])
@login_required
def save_style():
    title = request.form['title']
    color = request.form['color']
    size = request.form['size']
    font = request.form['font']

    style = Style.query.filter_by(user_id=current_user.id, book_title=title).first()

    if style:
        style.color = color
        style.size = size
        style.font = font
    else:
        db.session.add(Style(
            user_id=current_user.id,
            book_title=title,
            color=color,
            size=size,
            font=font
        ))

    db.session.commit()
    return redirect(url_for('home'))

@app.route('/profile')
@login_required
def profile():
    favorites = Favorite.query.filter_by(user_id=current_user.id).all()
    reviews = Review.query.filter_by(user_id=current_user.id).all()
    styles = Style.query.filter_by(user_id=current_user.id).all()

    return render_template("profile.html",
                           favorites=favorites,
                           reviews=reviews,
                           styles=styles)

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        db.session.add(User(
            username=request.form['username'],
            password=request.form['password']
        ))
        db.session.commit()
        return redirect('/login')

    return render_template("register.html")

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()

        if user and user.password == request.form['password']:
            login_user(user)
            return redirect('/')

    return render_template("login.html")

@app.route('/logout')
def logout():
    logout_user()
    return redirect('/')

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)