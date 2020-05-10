from flask import Flask, redirect, url_for, render_template, flash, request

import json
import tmdbsimple as tmdb
import py2neo as p2n


tmdb.API_KEY = '3886f06b279c31dd0f8c4fed0837a04f'


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

    return render_template('index.html', peliculas=result["results"], len = len(result["results"]))



def api_search_movie(movie_title):
    search = tmdb.Search()
    response = search.movie(query=movie_title)
    for s in search.results:
        credits = api_search_cast(s["id"])
        s["cast"] = credits["cast"]
        s["director"] = get_director_from_crew(credits["crew"])

        if (s["poster_path"] == "None" or s["poster_path"] is None):
            s["poster_path"]= "https://www.theprintworks.com/wp-content/themes/psBella/assets/img/film-poster-placeholder.png"
        else:
            s["poster_path"]= "https://image.tmdb.org/t/p/w220_and_h330_face" + s["poster_path"]
            print("no none %s " %s["poster_path"])

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
