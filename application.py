from flask import Flask, render_template, jsonify, request, redirect, url_for, make_response, flash
from database_setup import Base, Genres, Movies, new_engine, new_session, seed_db
from flask import session as login_session
try:
    from urllib.request import urlretrieve  # Python 3
except ImportError:
    from urllib import urlretrieve  # Python 2

# IMPORTS FOR GOOGLE OAUTH
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
import requests
import shutil
import random
import string

engine = new_engine("movie_catalog")
session = new_session(engine)
seed_db(session)

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Movie Catalog Application (Movie Buff)"


# Login route
@app.route('/login')
def show_login():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    output = ''
    output += '<h3>Welcome, '
    output += login_session['username']
    output += '</br>'
    output += '</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += '" style = "width: 150px; height: 150px;border-radius: 150px;-webkit-border-radius: ' \
              '150px;-moz-border-radius: 150px;"> '
    output += '</br>'
    flash("you are now logged in as %s" % login_session['username'])
    print("done!")
    return output


@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print('Access Token is None')
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print('In gdisconnect access token is %s', access_token)
    print('User name is: ')
    print(login_session['username'])
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print('result is ')
    print(result)
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return redirect('/')
    else:
        response = make_response(json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# Show home page
@app.route('/')
@app.route('/genres/')
def show_genres():
    movies = session.query(Genres).all()
    return render_template('main.html', movies=movies, login_data=login_session)

# Movie genre json
@app.route('/genres/json')
def genres_json():
    genres = session.query(Genres).all()

    return jsonify(genres=[g.serialize for g in genres])

# Movie catalog json
@app.route('/movies/json')
def movies_json():
    movies = session.query(Movies).all()
    items = session.query(Movies).all()
    return jsonify(movies=[m.serialize for m in movies])

# Create new movie in a genre (category)
@app.route('/genres/<int:genre_id>/movies/new', methods=['GET', 'POST'])
def new_movie_item(genre_id):
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        new_movie = Movies(name=request.form['name'], description=request.form['desc'], genre_id=genre_id,
                           author=login_session['username'])
        session.add(new_movie)
        session.commit()

        url = request.form['url']
        urlretrieve(url, request.form['name'] + '.png')

        shutil.move(request.form['name'] + '.png', 'static/img/' + request.form['name'] + '.png')

        return redirect(url_for('show_movies', genre_id=genre_id))
    else:
        return render_template('new_movie_item.html', genre_id=genre_id)

# Show movies for a category
@app.route('/genres/<int:genre_id>/')
@app.route('/genres/<int:genre_id>/movies/')
def show_movies(genre_id):
    if 'username' not in login_session:
        return redirect('/login')
    genre = session.query(Genres).filter_by(id=genre_id).one()
    movies = session.query(Movies).filter_by(genre_id=genre_id).all()

    return render_template('movies.html', genre=genre, movies=movies)

# Update Movie (IF USER CREATED)
@app.route('/genres/<int:genre_id>/movies/<int:movie_id>/edit/', methods=['GET', 'POST'])
def edit_movie(genre_id, movie_id):
    if 'username' not in login_session:
        return redirect('/login')
    edited_item = session.query(Movies).filter_by(id=movie_id).one()
    old_name = edited_item.name
    if request.method == 'POST':
        if request.form['name']:
            edited_item.name = request.form['name']
        if request.form['desc']:
            edited_item.description = request.form['name']

        # Update image name on edit
        shutil.move('static/img/' + old_name + '.png', 'static/img/' + edited_item.name + '.png')

        session.add(edited_item)
        session.commit()

        return redirect(url_for('show_movie', movie_id=movie_id, genre_id=genre_id))
    else:
        return render_template(
            'edit_movie.html', genre_id=genre_id, movie_id=movie_id, item=edited_item, login_info=login_session)

# Delete movie (IF USER CREATED)
@app.route('/genres/<int:genre_id>/movies/<int:movie_id>/delete/', methods=['GET', 'POST'])
def delete_movie(genre_id, movie_id):
    if 'username' not in login_session:
        return redirect('/login')
    item_to_delete = session.query(Movies).filter_by(id=movie_id).one()
    if request.method == 'POST':
        if request.form['options'] == "true":
            print("DELETE REQUEST RECEIVED")
            session.delete(item_to_delete)
            session.commit()

            return redirect(url_for('show_movies', movie_id=movie_id, genre_id=genre_id))
        else:
            movie = session.query(Movies).filter_by(id=movie_id).one()

            return render_template('movie.html', genre_id=genre_id, movie_id=movie_id, movie=movie)
    else:
        return render_template(
            'delete_movie.html', genre_id=genre_id, movie_id=movie_id, item=item_to_delete, login_info=login_session)


# Show single movie
@app.route('/genres/<int:genre_id>/movies/<int:movie_id>/')
def show_movie(genre_id, movie_id):
    if 'username' not in login_session:
        return redirect('/login')
    movie = session.query(Movies).filter_by(id=movie_id).one()

    return render_template('movie.html', genre_id=genre_id, movie_id=movie_id, movie=movie)


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
