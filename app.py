  
from flask import Flask, redirect, url_for, render_template, flash, request

import json
import tmdbsimple as tmdb


tmdb.API_KEY = '3886f06b279c31dd0f8c4fed0837a04f'

img_base_url="https://image.tmdb.org/t/p/w220_and_h330_face/"


app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/movie/<movie_title>')
def search_movie(movie_title):

    #search in the local database
    
    #if not in the local bd, search in the api
    result = api_search_movie(movie_title)

    return " - "


def api_search_movie(movie_title):
    search = tmdb.Search()
    response = search.multi(query=movie_title)
    for s in search.results:
        credits = api_search_cast(s["id"])
        s["cast"] = credits["cast"]
        s["director"] = get_director_from_crew(credits["crew"])

    print(search.results[0]["director"])
    print(person_info(search.results[0]["director"][0]["id"]))
    return response

def person_info(id):
    person = tmdb.People(id)
    response = person.info()
    return response

def get_director_from_crew(credits):
    return [c for c in credits if c["job"] == "Director"]


def api_search_cast(id):
    movie = tmdb.Movies(id)
    response = movie.credits()
    return response


if __name__ == '__main__':
    
    app.run(debug=True)