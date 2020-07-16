#!/usr/bin/env python3

# Flask module imports
from flask import Flask, jsonify, render_template
from flask import redirect, flash, request, url_for
from flask import make_response as make_response
from flask import session
import flask
from flask_oauth import OAuth

# Facebook Oauth module imports
import facebook as FB

# Sqlalchemy and database module imports
from configure_database import Base, Book, Genre, User
import sqlalchemy
import sqlalchemy.orm
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, asc


app = Flask(__name__)
app.url_map.strict_slashes = False
ACCOUNT_DEFAULT_HTTP_PROTOCOL = 'https'


# ----------------------------------------------------------------------------------------------------------------
# Connect database.

# Connect to the database and create a database session_db.
engine = create_engine('sqlite:///BookDatabase.db',
                       connect_args={'check_same_thread': False})

# Bind the above engine to a session_db.
Session = sessionmaker(bind=engine)

# Create a session_db object.
session_db = Session()


# ----------------------------------------------------------------------------------------------------------------
# Facebook login set-up.


# Set up Facebook OAuth.

FACEBOOK_APP_ID = '731255797406579'
FACEBOOK_APP_SECRET = '1f55f01ea7da5fab91e2ef1e2df2ef09'
token = 'EAAKZAEsILW3MBALx6AjMNfr0KJ6DqxI4OPVOkJti' \
        + 'CrZBU3Ela4eVMECVF2MOiIZATiyqZCcrQ9lVXVrUJ' \
        + '8Wmm2lRqyWRFN4zbkCrGu0rlPD5W0QoYxK4ZAREF7' \
        + 'hceWOyOsitPWrUVzNP2T57ZCf7vpDnUfwn7gZBk1s' \
        + 'don533zznsduKJ1nn66LOyexGyZBWNZC2xqeZBX5L' \
        + 'S8kK8ZBGe3edQEqnV1zy0UqNZC2NUbihLUZAI8wZDZD'

oauth = OAuth()

facebook = oauth.remote_app(
                'facebook',
                base_url='https://graph.facebook.com/',
                request_token_url=None,
                access_token_url='/oauth/access_token',
                authorize_url='https://www.facebook.com/dialog/oauth',
                consumer_key=FACEBOOK_APP_ID,
                consumer_secret=FACEBOOK_APP_SECRET,
                request_token_params={'scope': 'public_profile'}
            )

# Acquire Facebook token.
@facebook.tokengetter
def get_facebook_token():
    return session.get('facebook_token')


def pop_login_session():
    session.pop('logged_in', None)
    session.pop('facebook_token', None)


# Create Login endpoint.
@app.route("/facebook_login")
def facebook_login():
    return facebook.authorize(callback=url_for(
        'facebook_authorized',
        next=request.args.get('next'), _external=True))


# Create Facebook authorization endpoint.
@app.route("/facebook_authorized")
@facebook.authorized_handler
def facebook_authorized(resp):
    next_url = request.args.get('next') or url_for('home')
    if resp is None or 'access_token' not in resp:
        return redirect(next_url)

    session['logged_in'] = True
    session['facebook_token'] = (resp['access_token'], '')

    return redirect(next_url)


# Create logout endpoint.
@app.route("/logout")
def logout():
    pop_login_session()
    return redirect(url_for('home'))


# ----------------------------------------------------------------------------------------------------------------
# Home page.

@app.route('/')
@app.route('/catalog/')
@app.route('/catalog/books/')
def home():
    genres = session_db.query(Genre).all()
    books = session_db.query(Book).all()
    return render_template(
        'index.html', genres=genres, books=books)


# -----------------------------------------------------------------------------------------------------------------
# CRUD functionalty


# --------------CRUD - 'Create' Supporting Functions --------------------------

# Check if the submitted book already exists in BookDatabase.
def check_book_duplicate(book_id):

    book = session_db.query(Book).filter_by(id=book_id).first()
    # If a book is present in the database, return a Boolean value of true.
    # This value is then used to check for duplicate items when
    #  new submissions are entered.
    if book:
        return True
    else:
        return False


# Check if the submitted genre already exists in BookDatabase.
def check_genre_duplicate(genre_id):

    genre = session_db.query(Genre).filter_by(id=genre_id).first()
    # If a genre is present in the database, return a Boolean value of true.
    # This value is then used to check for duplicate items when
    # new submissions are entered.
    if genre:
        return True
    else:
        return False


# --------------CRUD - 'Create' Functions ---------------------------


# Create a new genre.
@app.route("/catalog/genre/new/", methods=['GET', 'POST'])
def add_genre():

    try:
        FBtoken = (get_facebook_token())[0]
        print(FBtoken)
    except Exception:
        flash('Please log in to create a genre.')
        return redirect(url_for('home'))

    if request.method == 'POST':

        genre = session_db.query(Genre).\
            filter_by(name=request.form['new-genre-name']).first()
        # Check if the entered genre already exists in the database.
        # If it does, redirect to the creation page.
        if genre:
            flash('The submitted genre already exists.')
            return redirect(url_for('add_genre'))

        new_genre = Genre(
            user_id=(facebook.get('/me?fields=id').data)["id"],
            name=request.form['new-genre-name']
            )

        session_db.add(new_genre)
        session_db.commit()
        flash('New genre (%s) successfully created!' % new_genre.name)
        return redirect(url_for('home'))
    else:
        return render_template('new_genre.html')


# Create a new book.
@app.route("/catalog/book/new/", methods=['GET', 'POST'])
def add_book():

    try:
        FBtoken = (get_facebook_token())[0]
        print(FBtoken)
    except Exception:
        flash('Please log in to create a book.')
        return redirect(url_for('home'))

    if request.method == 'POST':

        book = session_db.query(Book).\
            filter_by(name=request.form['new-book-name']).first()
        # Check if the entered book already exists in the database.
        # If it does, redirect to the creation page.
        if book:
            flash('The submitted book already exists.')
            return redirect(url_for('add_book'))

        new_book = Book(
            user_id=(facebook.get('/me?fields=id').data)["id"],
            name=request.form['new-book-name'],
            description=request.form['description']
        )

        session_db.add(new_book)
        session_db.commit()
        flash('New book successfully created!')
        return redirect(url_for('home'))

    else:
        books = session_db.query(Book).order_by(Book.id.desc())
        genre = session_db.query(Genre).order_by(Genre.id.desc())
        return render_template(
            'new_book.html',
            books=books,
            genre=genre
        )


# Within a genre, create a new book.
@app.route("/catalog/genre/<int:genre_id>/book/new/",
           methods=['GET', 'POST'])
def add_book_by_genre(genre_id):
    # Check if user is logged in. If user is not logged in (via Facebook),
    # redirect to home page with flash notification.
    try:
        FBtoken = (get_facebook_token())[0]
        print(FBtoken)

    except Exception:
        flash('Please log in to create a book.')
        return redirect(url_for('home'))

    if request.method == 'POST':
        # Check if the book already exists in the database.
        # If it does, display an error.
        book = session_db.query(Book)\
            .filter_by(name=request.form['new-book-name']).first()
        # Check if the entered book already exists in the database.
        # If it does, redirect to the creation page.
        if book:
            if book.name == request.form['new-book-name']:
                flash('This book already exists in the database!')
                return redirect(url_for("add_book"))

        new_book = Book(
            user_id=(facebook.get('/me?fields=id').data)["id"],
            genre_id=genre_id,
            name=request.form['new-book-name'],
            description=request.form['description']
            )

        session_db.add(new_book)
        session_db.commit()
        flash('New book created successfully!')
        return redirect(url_for('show_books_in_genre',
                                genre_id=genre_id))

    else:
        genre = session_db.query(Genre).filter_by(id=genre_id).first()
        return render_template('new_book.html', genre=genre)


# --------------CRUD - 'Read' Functions ---------------------------------------


# View a book.
@app.route('/catalog/book/<int:book_id>/')
def view_book(book_id):

    if not check_book_duplicate(book_id):
        flash('The entered Book ID does not exist in the database.')
        return redirect(url_for('home'))

    else:
        book = session_db.query(Book).filter_by(id=book_id).first()
        genre = session_db.query(Genre)\
            .filter_by(id=book.genre_id).first()
        return render_template(
            "view_book.html",
            book=book,
            genre=genre
        )


# View the books in a particular genre.
@app.route('/catalog/genre/<int:genre_id>/books/')
def show_books_in_genre(genre_id):

    if not check_genre_duplicate(genre_id):
        flash("The entered Genre ID does not exist in the database.")
        return redirect(url_for('home'))

    genre = session_db.query(Genre).filter_by(id=genre_id).first()
    total = session_db.query(Book).filter_by(genre_id=genre.id).count()
    books = session_db.query(Book).filter_by(genre_id=genre.id).all()

    return render_template(
        'view_books_in_genre.html',
        genre=genre,
        total=total,
        books=books
        )


# --------------CRUD - 'Update' Functions -------------------------------------


# Edit an existing book.
@app.route("/catalog/book/<int:book_id>/edit/", methods=['GET', 'POST'])
def edit_book(book_id):

    # Check if user is logged in. If user is not logged in (via Facebook),
    # redirect to home page with flash notification.
    try:
        FBtoken = (get_facebook_token())[0]
        print(FBtoken)
    except Exception:
        flash('Please log in to edit a book.')
        return redirect(url_for('home'))

    if not check_book_duplicate(book_id):
        flash("You have inputted a duplicate book.")
        return redirect(url_for('home'))

    book = session_db.query(Book).filter_by(id=book_id).first()

    owner = book.user_id
    current_user_id = (facebook.get('/me?fields=id').data)["id"]

    owner_int = int(owner)
    current_user_id_int = int(current_user_id)

    if current_user_id_int != owner_int:
        flash("You do not have permission to edit this book.")
        return redirect(url_for('home'))

    if request.method == 'POST':
        if request.form['name']:
            book.name = request.form['name']
        if request.form['description']:
            book.description = request.form['description']
        session_db.add(book)
        session_db.commit()
        flash('Book successfully updated!')
        return redirect(url_for('view_book', book_id=book_id))
    else:
        return render_template(
            'update_book.html',
            book=book,
            owner=owner
        )


# Edit a genre.
@app.route('/catalog/genre/<int:genre_id>/edit/',
           methods=['GET', 'POST'])
def update_genre(genre_id):

    # Check if user is logged in. If user is not logged in (via Facebook),
    # redirect to home page with flash notification.
    try:
        FBtoken = (get_facebook_token())[0]
        print(FBtoken)
    except Exception:
        flash('Please log in to edit a genre.')
        return redirect(url_for('home'))

    genre = session_db.query(Genre).filter_by(id=genre_id).first()

    if not check_genre_duplicate(genre_id):
        flash("You have inputted a duplicate genre.")
        return redirect(url_for('home'))

    if request.method == 'POST':
        if request.form['name']:
            genre.name = request.form['name']
            session_db.add(genre)
            session_db.commit()
            flash('Genre successfully updated!')
            return redirect(url_for('show_books_in_genre',
                                    genre_id=genre.id))
    else:
        return render_template('update_genre.html', genre=genre)


# --------------CRUD - 'Delete' Functions -------------------------------------


# Delete an existing book.
@app.route("/catalog/book/<int:book_id>/delete_book/", methods=['GET', 'POST'])
def delete_book(book_id):

    # Check if user is logged in. If user is not logged in (via Facebook),
    # redirect to home page with flash notification.
    try:
        FBtoken = (get_facebook_token())[0]
        print(FBtoken)
    except Exception:
        flash('Please log in to delete a book.')
        return redirect(url_for('home'))

    book = session_db.query(Book).filter_by(id=book_id).first()

    if request.method == 'POST':
        session_db.delete(book)
        session_db.commit()
        flash("Book deleted successfully!")
        return redirect(url_for('home'))
    else:
        return render_template('delete_book.html', book=book)


# Delete a genre.
@app.route('/catalog/genre/<int:genre_id>/delete/',
           methods=['GET', 'POST'])
def delete_genre(genre_id):

    # Check if user is logged in. If user is not logged in (via Facebook),
    # redirect to home page with flash notification.
    try:
        FBtoken = (get_facebook_token())[0]
        print(FBtoken)
    except Exception:
        flash('Please log in to delete a genre.')
        return redirect(url_for('home'))

    genre = session_db.query(Genre).filter_by(id=genre_id).first()

    if request.method == 'POST':
        session_db.delete(genre)
        session_db.commit()
        flash("Genre successfully deleted!")
        return redirect(url_for('home'))
    else:
        return render_template("delete_genre.html", genre=genre)


# ----------------------------------------------------------------------------------------------------------------
# JSON Endpoints


# Return JSON of all the books in the catalog.
@app.route('/api/v1/catalog.json')
def show_catalog_json():

    books = session_db.query(Book).order_by(Book.id.desc())
    return jsonify(catalog=[i.serialize for i in books])


# Return JSON of a particular book in the catalog.
@app.route(
    '/api/v1/genres/<int:genre_id>/book/<int:book_id>/JSON')
def catalog_book_json(genre_id, book_id):

    if check_genre_duplicate(genre_id) and check_book_duplicate(book_id):
        book = session_db.query(Book)\
               .filter_by(id=book_id, genre_id=genre_id).first()
        # Check if the entered book already exists in the database.
        # If it does, redirect to the creation page.
        if book:
            return jsonify(book=book.serialize)
        else:
            return jsonify(
                error='book {} does not belong to genre {}.'
                .format(book_id, genre_id))
    else:
        return jsonify(error='This book or the genre does not exist.')


# Return JSON of all the genres in the genre.
@app.route('/api/v1/genres/JSON')
def genres_json():

    genres = session_db.query(Genre).all()
    return jsonify(genres=[i.serialize for i in genres])


# ----------------------------------------------------------------------------------------------------------------
# Main function

if __name__ == '__main__':
    app.debug = False
    app.secret_key = '\xc9\xb2\x06\xeeGF\xd5\xa94\xc7\xd4\xc5\xb4\x1f\x7f\xf1p'
    app.run(host='0.0.0.0', port=5000)
