from flask import Flask, redirect, url_for, render_template, flash, request

import json
import tmdbsimple as tmdb
import py2neo as p2n


tmdb.API_KEY = '3886f06b279c31dd0f8c4fed0837a04f'

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/movie/<movie_title>')
def search_movie(movie_title):

    #search in the local database
    
    #if not in the local bd, search in the api
    result = api_search_movie(movie_title)

    return render_template('inicio.html', peliculas=result["results"])
    #return result

def api_search_movie(movie_title):
    
    search = tmdb.Search()
    response = search.multi(query=movie_title)
    for s in search.results:
        s["cast"] = api_search_cast(s["id"])

    return response


def api_search_cast(id):
    movie = tmdb.Movies(id)
    response = movie.credits()
    return response


if __name__ == '__main__':
    
    app.run(debug=True)
