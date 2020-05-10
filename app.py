from flask import Flask, redirect, url_for, render_template, flash, request

import json
import tmdbsimple as tmdb
import py2neo as p2n




tmdb.API_KEY = '3886f06b279c31dd0f8c4fed0837a04f'

img_base_url="https://image.tmdb.org/t/p/w220_and_h330_face/"

neopass="Mhwgc5P9k3mUXEj"
neouser="neo4j"

app = Flask(__name__)


@app.route('/')
def index():
    graph = p2n.Graph("bolt://localhost:7687", user=neouser, password=neopass)
    matcher=p2n.NodeMatcher(graph)
    result=list(matcher.match("movie").limit(10))
    print(result)
    return render_template('index.html',peliculas=result,len = len(result))
    
    
@app.route('/movie/<movie_title>')
def search_movie(movie_title):
     
    #search in the local database
    
    #if not in the local bd, search in the api
    result = api_search_movie(movie_title)
        
    #return render_template('inicio.html', peliculas=result["results"])
    
    return render_template('index.html', peliculas=result["results"], len = len(result["results"]))

@app.route('/movie/<movie_id>')
def detail_movie(movie_id):
    graph = p2n.Graph("bolt://localhost:7687", user=neouser, password=neopass)
    matcher=p2n.NodeMatcher(graph)   
    movie=matcher.match("movie").where("_.id="+movie_id)
    


def api_search_movie(movie_title):
    graph = p2n.Graph("bolt://localhost:7687", user=neouser, password=neopass)
    graph.schema.create_uniqueness_constraint("movie", "id")
    graph.schema.create_uniqueness_constraint("person", "id")
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

        
    for p in response["results"]:
        movie=p2n.Node("movie", original_title=p["title"],id=p["id"], release_date=p["release_date"],poster_path=p["poster_path"], vote_count=p["vote_count"], vote_average=p["vote_average"])
        graph.merge(movie, "movie", "id")
        
                     
        for d in p["director"]:
            d=person_info(d["id"])
            director=p2n.Node("person", name=d["name"],birthday=d["birthday"], deathdate=d["deathday"], id=d["id"])
            graph.merge(director, "person", "id")             
            directs=p2n.Relationship.type("directs")
            graph.create(directs(director, movie))
                      
                
        for d in p["cast"]:
            d=person_info(d["id"])
            actor=p2n.Node("person", name=d["name"],birthday=d["birthday"], deathdate=d["deathday"], id=d["id"])
            graph.merge(actor, "person", "id")             
            acts_in=p2n.Relationship.type("acts_in")
            graph.create(acts_in(actor, movie))             

                            

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
