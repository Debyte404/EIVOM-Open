from flask import Flask, render_template, request, jsonify, redirect, url_for,flash ,send_from_directory
import requests
from flask_pymongo import PyMongo
from flask_pymongo import PyMongo
from flask_login import UserMixin, LoginManager, login_user, current_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from rec_sys import get_result,loads
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = '' #secret key
#"mongodb+srv://username:password@host/user_credentials?retryWrites=true&w=majority"
app.config["MONGO_URI"] = "" #mongo uri
mongo = PyMongo(app)
app.secret_key = ''#secret key
login_manager = LoginManager(app)


# Replace 'your_api_key' with the API key you obtained from TMDb
API_KEY = '' #tmdb api key
BASE_URL = 'https://api.themoviedb.org/3'

OMDB_API_KEY = '' #omdb api key

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

#-------------------------------------------------------------------------------------------------------------------


class User(UserMixin):
    def __init__(self, username, password_hash):
        self.username, self.password_hash = username, password_hash
        self.is_authenticated

    @staticmethod
    def validate_login(password_hash, password):
        return check_password_hash(password_hash, password)

    def get_id(self):
        return self.username


@login_manager.user_loader
def load_user(user_id):
    user_data = mongo.db.users.find_one({"username": user_id})
    return User(username=user_data['username'], password_hash=user_data['password']) if user_data else None

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = mongo.db.users.find_one({"username": request.form['username']})
        if user and User.validate_login(user['password'], request.form['password']):
            login_user(User(username=user['username'], password_hash=user['password']),remember=True)
            return redirect(url_for('home'))
        flash("Invalid username/password", 'error')
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logged out successfully", "info")
    return redirect(url_for('home'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username, password = request.form['username'], request.form['password']
        password_hash = generate_password_hash(password)

        if mongo.db.users.find_one({'username': username}) is None:
            mongo.db.users.insert_one({'username': username, 'password': password_hash})
            login_user(User(username=username, password_hash=password_hash))
            return redirect(url_for('home'))
        flash('Username already exists','conflict')
        
    return render_template('register.html')

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    can_username = False
    can_password = False
    try:
        fase = request.form['username']
        can_username = True
    except Exception as e:
        print(e)
        can_username = False
    try:
        fase2 = request.form['password']
        can_password = True
    except Exception as e:
        print(e)
        can_password = False

    if request.method == 'POST' and can_username:
        new_username = request.form['username']
        
        if mongo.db.users.find_one({'username': new_username}):
            flash('Username already exists', 'error')

        else:
            try:
                mongo.db.users.update_one({'username': current_user.username}, {'$set': {'username': new_username}})
            except Exception as e:
                print(e)
                
            flash('Profile username updated successfully', 'info')
            current_user.username = new_username

    if request.method == 'POST' and can_password:
        new_password = request.form['password']
        new_hash = generate_password_hash(new_password)

        if mongo.db.users.find_one({'password': new_hash}):
            flash('Password already in use','error')
        else:
            try:
                mongo.db.users.update_one({'password': current_user.password_hash}, {'$set': {'password': new_hash}})
            except Exception as e:
                print(e)
                
            flash('Profile Password updated successfully', 'info')
            current_user.password_hash = new_hash

    return render_template('profile.html', user=current_user)


#--------------------------------------------------------------------------------------------------------------------

def get_trending_movies():

    url = f'{BASE_URL}/trending/movie/week?api_key={API_KEY}'
    data = requests.get(url)
    response = list(data.json()['results'])
    for movie in response:
        idurl = f"https://api.themoviedb.org/3/movie/{movie['id']}/external_ids?api_key={API_KEY}"
        # new_id = requests.get(idurl).json()
        # print(new_id)
        new_id = requests.get(idurl).json()['imdb_id']
        movie['imdb_id'] = new_id
    # print(response)
    if data.status_code == 200:
        return response  # 'results' contains the list of trending movies
    else:
        return []


def get_movie_data(Id):

    url = f'http://www.omdbapi.com/?i={Id}&apikey={OMDB_API_KEY}'
    response = requests.get(url).json()

    if response['Response'] == 'True':
        return response
    else:
        return None
    
def get_liked_movies(username):
    user_document = mongo.db.users.find_one({'username': username})
    
    # Check if the user document was found
    if user_document:
        # Extract the liked_movies field which contains the movie IDs
        movie_ids = user_document.get('liked_movies', [])
        # return jsonify({'movie_ids': movie_ids}), 200
        return movie_ids
    else:
        return jsonify({'message': 'User not found'}), 404


def search_tmdb(query):
    url = f'{BASE_URL}/search/movie?api_key={API_KEY}&query={query}&include_adult=true'
    response = requests.get(url)
    # print(response.json())
    if response.status_code == 200:
        return response.json()['results']
    return []

def search_omdb(query):
    url = f'https://www.omdbapi.com/?s={query}&apikey={OMDB_API_KEY}'
    page2 = f'https://www.omdbapi.com/?s={query}&page=2&apikey={OMDB_API_KEY}'
    results = requests.get(url).json()
    if results['Response'] == 'True':
        response = results['Search']
        
        # try:
        #     page2 = requests.get(page2).json()['Search']
        #     response += page2
        # except Exception as e:
        #     print(e)
        # print(response.json())
        for result in response:
            imdbId = result['imdbID']
            url_rating = f'http://www.omdbapi.com/?i={imdbId}&apikey={OMDB_API_KEY}'
            data = requests.get(url_rating).json()
            rating = data['imdbRating']
            date = data["Released"]
            result['rating'] = rating
            result['release_date'] = date

        return response

    return []
    
    # print(response)

def recomend_res(listA):
    username = current_user.username
    # movie_ids = request.json['selections']
    idB = get_liked_movies(username)
    listB = []
    for items in idB:
        movie_title = get_movie_data(items)
        movie_title = movie_title['Title']
        listB.append(movie_title)
    
    print(listB)
    
    recommendations = loads(get_result(listA, listB))

    print(recommendations)

    final_results = []

    if recommendations is not None:
        for rec in recommendations:

            url = f'http://www.omdbapi.com/?t={rec}&apikey={OMDB_API_KEY}'
            data = requests.get(url).json()
            if data["Response"] == "True":
                final_results.append(data)

        # print(final_results)

    else:
        print("Ai aint active right now")

    return final_results

# def recomend_res_tests(listA):
#     listidoi = [listA]
#     for i in range(30000):
#         listidoi.append(str(i)+"aabababab")
#     return listidoi


######################################################################################################################################################
@app.route('/recomend',methods=['POST'])
@login_required
def recomend():
    data = request.get_json().get('data', [])
    recomendations = recomend_res(listA=data)
    # print(recomendations)
    # for item in recomendations:
    #     print(item)
    # modified_data = [item + 'abcd' for item in data]
    return jsonify({'status': 'success', 'modifiedData': recomendations})

@app.route('/why')
def testing():
    return "'eivom' is 'movie' but reversed... cuz i m reverse engineering the way you watch movies"

@app.route('/select_movie', methods=['POST'])
# @login_required
def select_movie():
    print(current_user.is_authenticated)
    movie_id = request.json['movie_id']
    # if movie_id not in selected_movies:
    #     selected_movies.append(movie_id)
    username = current_user.username
    # new_movie_id = request.json['movie_id']
    
    # Update the user document to add new movie ID to liked_movies list if not already present
    result = mongo.db.users.update_one(
        {'username': username},
        {'$addToSet': {'liked_movies': movie_id}}
    )
    
    if result.modified_count:
        # print(selected_movies)
        print('movie added successfully')
        flash('Movie added to favorites or already exists!', 'success')
        # return jsonify(success=True)
        return jsonify({'message': 'Movie added successfully or already exists'}), 200
    else:
        print('could not add movie')
        return jsonify({'message': 'Update failed or user not found'}), 200


@app.route('/remove_movie', methods=['POST'])
def remove_movie():
    username = current_user.username
    movie_id_to_remove = request.json['movie_id']
    print(movie_id_to_remove)
    # Update the user document to remove the specified movie ID from liked_movies list
    result = mongo.db.users.update_one(
        {'username': username},
        {'$pull': {'liked_movies': movie_id_to_remove}}
    )
    
    if result.modified_count:
        print('movie removed successfully')
        return jsonify({'message': 'Movie removed successfully'}), 200
    else:
        print('failed to remove movie')
        return jsonify({'message': 'Update failed or movie ID not found in list'}), 200
   
    

@app.route('/movie/<movie_id>')
def movie_details(movie_id):
    movie = get_movie_data(movie_id)  # Assuming this function fetches movie details
    in_liked = False
    if current_user.is_authenticated:
        username = current_user.username
        user_document = mongo.db.users.find_one({'username': username})
        
        # Check if the user document was found
        if user_document:
            # Extract the liked_movies field which contains the movie IDs
            movie_ids = user_document.get('liked_movies', [])
            # return jsonify({'movie_ids': movie_ids}), 200
            if movie['imdbID'] in movie_ids:
                in_liked = True;
            else:
                in_liked = False;
        else:
            in_liked=False;
            print("user not found")
    else:
        in_liked = False;
    
    return render_template('movie_details.html', movie=movie ,user=current_user,show=in_liked)

@app.route('/liked')
@login_required
def liked():
    username = current_user.username
    movie_ids = get_liked_movies(username)
    movies = []
    for movie in movie_ids:
        movies.append(get_movie_data(movie))

    # return str(movie_ids)
    return render_template('liked.html',movies=movies,user=current_user)

@app.route('/', methods=['GET', 'POST'])
def home():
    movies = get_trending_movies()
    print(current_user.is_authenticated)
    if request.method == 'POST':
        query = request.form['search_query']

        results = search_omdb(query)
        # print(results)
        return render_template('search_results.html', movies=results, query=query,user_agent=current_user)
    return render_template('home.html', movies=movies,user_agent=current_user)



if __name__ == '__main__':
    app.run()

