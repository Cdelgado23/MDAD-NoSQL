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
    return render_template('index.html')

@app.route('/movie/<movie_title>')
def search_movie(movie_title):

    #search in the local database
    
    #if not in the local bd, search in the api
    result = api_search_movie(movie_title)

    #return render_template('inicio.html', peliculas=result["results"])
    return result



def api_search_movie(movie_title):
    graph = p2n.Graph("bolt://localhost:7687", user=neouser, password=neopass)
    graph.schema.create_uniqueness_constraint("movie", "id")
    graph.schema.create_uniqueness_constraint("person", "id")
    graph.delete_all()#borrar en algun momento    
    search = tmdb.Search()
    response = search.multi(query=movie_title)
    for s in search.results:
        credits = api_search_cast(s["id"])
        s["cast"] = credits["cast"]
        s["director"] = get_director_from_crew(credits["crew"])
        
    for p in response["results"]:
        movie=p2n.Node("movie", title=p["title"],id=p["id"], release_date=p["release_date"],poster_path=p["poster_path"], votes=p["vote_count"], rate=p["vote_average"])
        graph.merge(movie, "movie", "id")
        
                     
        for d in p["director"]:
            d=person_info(d["id"])
            director=p2n.Node("person", name=d["name"],birthday=d["birthday"], deathdate=d["deathday"], id=d["id"])
            graph.merge(director, "person", "id")             
            directs=p2n.Relationship.type("directs")
            graph.merge(directs(director, movie), "person","id")
                      
                
        for d in p["cast"]:
            d=person_info(d["id"])
            actor=p2n.Node("person", name=d["name"],birthday=d["birthday"], deathdate=d["deathday"], id=d["id"])
            graph.merge(actor, "person", "id")             
            acts_in=p2n.Relationship.type("acts_in")
            graph.merge(acts_in(actor, movie), "person", "id")             

                            
                
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
