from flask import Flask, redirect, url_for, render_template, flash, request

import json
import tmdbsimple as tmdb
from py2neo import Graph, Node, Relationship, NodeMatcher
from py2neo.matching import *
from py2neo.data import Subgraph


tmdb.API_KEY = '3886f06b279c31dd0f8c4fed0837a04f'

img_base_url="https://image.tmdb.org/t/p/w220_and_h330_face/"

neopass="Mhwgc5P9k3mUXEj"
neouser="neo4j"

app = Flask(__name__)
graph=None

@app.route('/<searchType>/director/<id>')
def director_details(searchType, id):
    director=person_info(id)
    movies=api_search_by_director(id)    

    return render_template('ActorDetail.html',actor= director, peliculas=movies,len=len(movies), searchType=searchType) 

@app.route('/<searchType>/actor/<id>')
def actor_details(searchType, id):
    movies=[]
    matcher=NodeMatcher(graph)
    actor=matcher.match("person").where("_.id="+id).first()
    for a in  graph.run("MATCH (p:person)-[a:acts_in]->(m:movie) WHERE p.id={x} RETURN m", x=actor["id"]).data():
        movies.append(a["m"])
    return render_template('ActorDetail.html',actor= actor, peliculas=movies,len =len(movies), searchType=searchType)

@app.route('/<searchType>/details/<id>')
def movie_details(searchType, id):
    actors=[]
    matcher=NodeMatcher(graph)
    movie=matcher.match("movie").where("_.id="+id).first()
    if not movie["load"]:
        print("no db")
        credits = api_search_cast(movie["id"])
        cast = credits["cast"]
        movie["load"]=True;
        graph.push(movie)
        for d in cast:
            d=person_info(d["id"])
            if (d["profile_path"] == "None" or d["profile_path"] is None):
                d["profile_path"]= "https://www.theprintworks.com/wp-content/themes/psBella/assets/img/film-poster-placeholder.png"
            else:
                d["profile_path"]= "https://image.tmdb.org/t/p/w220_and_h330_face" + d["profile_path"]              
            actor=Node("person", name=d["name"],birthday=d["birthday"], deathdate=d["deathday"], id=d["id"], profile_path=d["profile_path"])
            graph.merge(actor, "person", "id")
            actors.append(actor)
            acts_in=Relationship.type("acts_in")
            graph.create(acts_in(actor, movie))
    else:
        print("in db")
        for a in  graph.run("MATCH (p:person)-[a:acts_in]->(m:movie) WHERE m.id={x} RETURN p", x=movie["id"]).data():
            actors.append(a["p"])
            
    print(movie["load"])
    return render_template('MovieDetail.html',pelicula= movie, actores=actors,len =len(actors), searchType="searchType")


def get_10_movies():
    matcher=NodeMatcher(graph)
    return list(matcher.match("movie").limit(10))


@app.route('/')
def index():
    matcher=NodeMatcher(graph)
    result=list(matcher.match("movie").limit(10))
    print(result)
    return render_template('SearchPage.html',peliculas=result,len = len(result), searchType="title")
    

@app.route('/title', methods=['POST', 'GET'])
def by_title_index():
    if request.method == "POST":
        return redirect('/title/' + request.form.get("user_input"))
    else:
        result= get_10_movies()
        return render_template('SearchPage.html',peliculas=result,len = len(result), searchType="title")


@app.route('/director', methods=['POST', 'GET'])
def by_director_index():
    if request.method == "POST":
        return redirect('/director/' + request.form.get("user_input"))
    else:
        result= get_10_movies()
        return render_template('SearchPage.html',peliculas=result,len = len(result), searchType="director")


@app.route('/genre', methods=['POST', 'GET'])
def by_genre_index():
    if request.method == "POST":
        return redirect('/genre/' + request.form.get("user_input"))
    else:
        result= get_10_movies()
        return render_template('SearchPage.html',peliculas=result,len = len(result), searchType="genre")

@app.route('/director/<director_name')
def search_director(director_name):
    print(director_name)
    nodes = graph.run("MATCH (a:person) WHERE toLower(a.name) CONTAINS toLower({x}) RETURN a", x=director_name).data()
    result=[]
    for x in nodes:
        result.append(x["a"])
    
    #if not in the local bd, search in the api
    if (len(result)<1):
        result = api_search_people(director_name)["results"]

    return render_template('SearchPeoplePage.html', people=result, len = len(result), searchType="director")


@app.route('/title/<movie_title>')
def search_movie(movie_title):
    #search in the local database
    print(movie_title)
    nodes = graph.run("MATCH (a:movie) WHERE toLower(a.original_title) CONTAINS toLower({x}) RETURN a", x=movie_title).data()
    result=[]
    for x in nodes:
        result.append(x["a"])
    #if not in the local bd, search in the api
    if (len(result)<1):
        print("not in bd")
        result = api_search_movie(movie_title)["results"]

    return render_template('SearchPage.html', peliculas=result, len = len(result), searchType="title")

def api_search_people(p_name):
    search = tmdb.Search()
    response = search.person(query=p_name)
    for s in search.results:

        if (s["profile_path"] == "None" or s["profile_path"] is None):
            s["profile_path"]= "https://www.theprintworks.com/wp-content/themes/psBella/assets/img/film-poster-placeholder.png"
        else:
            s["profile_path"]= "https://image.tmdb.org/t/p/w220_and_h330_face" + s["profile_path"]

    return response




def api_search_by_director(director_id):
    people = tmdb.People(director_id)
    response = people.combined_credits()

    result=[]

    if ("crew" in response):
        for d in response["crew"]:
            if d["job"]=="Director":
                if (d["poster_path"] == "None" or d["poster_path"] is None):
                    d["poster_path"]= "https://www.theprintworks.com/wp-content/themes/psBella/assets/img/film-poster-placeholder.png"
                else:
                    d["poster_path"]= "https://image.tmdb.org/t/p/w220_and_h330_face" + d["poster_path"]  
                result.append(d)
    return result

def api_search_movie(movie_title):
    search = tmdb.Search()
    response = search.movie(query=movie_title)
    for s in search.results:
        credits = api_search_cast(s["id"])
        s["director"] = get_director_from_crew(credits["crew"])
        
        

        if (s["poster_path"] == "None" or s["poster_path"] is None):
            s["poster_path"]= "https://www.theprintworks.com/wp-content/themes/psBella/assets/img/film-poster-placeholder.png"
        else:
            s["poster_path"]= "https://image.tmdb.org/t/p/w220_and_h330_face" + s["poster_path"]

        
    for p in response["results"]:
        movie=Node("movie", original_title=p["title"],id=p["id"], release_date=p["release_date"],poster_path=p["poster_path"], vote_count=p["vote_count"], vote_average=p["vote_average"], load=False)
        graph.merge(movie, "movie", "id")

        
                     
        for d in p["director"]:
            d=person_info(d["id"])
            if (d["profile_path"] == "None" or d["profile_path"] is None):
                d["profile_path"]= "https://www.theprintworks.com/wp-content/themes/psBella/assets/img/film-poster-placeholder.png"
            else:
                d["profile_path"]= "https://image.tmdb.org/t/p/w220_and_h330_face" + d["profile_path"]            
            director=Node("person", name=d["name"],birthday=d["birthday"], deathdate=d["deathday"], id=d["id"], profile_path=d["profile_path"])
            graph.merge(director, "person", "id")             
            directs=Relationship.type("directs")
            graph.create(directs(director, movie))
                      
                            

    return response

def person_info(id):
    person = tmdb.People(id)
    response = person.info()
    if (response["profile_path"] == "None" or response["profile_path"] is None):
        response["profile_path"]= "https://www.theprintworks.com/wp-content/themes/psBella/assets/img/film-poster-placeholder.png"
    else:
        response["profile_path"]= "https://image.tmdb.org/t/p/w220_and_h330_face" + response["profile_path"]  
    return response

    

def get_director_from_crew(credits):
    return [c for c in credits if c["job"] == "Director"]


def api_search_cast(id):
    movie = tmdb.Movies(id)
    response = movie.credits()
    return response
def genres(genre_id):
    genre=tmdb.Genres()
    respones=genre.movie_list()
    


if __name__ == '__main__':
    graph = Graph("bolt://localhost:7687", user=neouser, password=neopass)
    app.run(debug=True)
