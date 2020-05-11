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
#detail of a director
@app.route('/<searchType>/director/<id>')
def director_details(searchType, id):

    movies=[]
    matcher=NodeMatcher(graph)
    dir=matcher.match("person").where("_.id="+id).first()

    if (not dir["load"]):
        movies=api_search_by_director(id) 
        matcher=NodeMatcher(graph)
        for p in movies: 
            movie=matcher.match("movie").where("_.id="+str(p["id"])).first()

            if (movie==None):
                mov = tmdb.Movies(p["id"])
                response = mov.info()
                movie=Node("movie", original_title=response["original_title"],id=p["id"], release_date=response["release_date"],poster_path=p["poster_path"], vote_count=p["vote_count"], vote_average=p["vote_average"], load=False)
                graph.create(movie)
            for g in p["genre_ids"]:
                genre=matcher.match("genre").where("_.id="+str(g)).first()
                belongs_to=Relationship.type("belongs_to")
                graph.create(belongs_to(movie, genre))         

            directs=Relationship.type("directs")
            graph.create(directs(dir, movie))

        dir["load"]=True
        graph.push(dir)
    
    else:
        matcher=NodeMatcher(graph)
        for a in  graph.run("MATCH (p:person)-[a:directs]->(m:movie) WHERE p.id={x} RETURN m", x=dir["id"]).data():
            movies.append(a["m"])

    return render_template('ActorDetail.html',actor= dir, peliculas=movies,len=len(movies), searchType=searchType) 
#details of a actor
@app.route('/<searchType>/actor/<id>')
def actor_details(searchType, id):
    movies=[]
    matcher=NodeMatcher(graph)
    actor=matcher.match("person").where("_.id="+id).first()

    if (not actor["load"]):
        movies = api_search_by_actor(id)

        for p in movies: 
            matcher=NodeMatcher(graph)
            movie=matcher.match("movie").where("_.id="+str(p["id"])).first()

            if (movie==None):
                mov = tmdb.Movies(p["id"])
                response = mov.info()
                movie=Node("movie", original_title=response["original_title"],id=p["id"], release_date=response["release_date"],poster_path=p["poster_path"], vote_count=p["vote_count"], vote_average=p["vote_average"], load=False)
                graph.create(movie)
            for g in p["genre_ids"]:
                genre=matcher.match("genre").where("_.id="+str(g)).first()
                belongs_to=Relationship.type("belongs_to")
                graph.create(belongs_to(movie, genre))            

            acts_in=Relationship.type("acts_in")
            graph.create(acts_in(actor, movie))

        actor["load"]=True
        graph.push(actor)

    else:
        for a in  graph.run("MATCH (p:person)-[a:acts_in]->(m:movie) WHERE p.id={x} RETURN m", x=actor["id"]).data():
            movies.append(a["m"])
    return render_template('ActorDetail.html',actor= actor, peliculas=movies,len =len(movies), searchType=searchType)
#detalied movie and actors and directos load
@app.route('/<searchType>/details/<id>')
def movie_details(searchType, id):
    actors=[]
    genres=[]
    matcher=NodeMatcher(graph)
    movie=matcher.match("movie").where("_.id="+id).first()
    if not movie["load"]:#check if this movie cast was loaded before
        print("no db")
        credits = api_search_cast(movie["id"])
        cast = credits["cast"]
        credits = api_search_cast(movie["id"])
        directors = get_director_from_crew(credits["crew"])        
        movie["load"]=True
        graph.push(movie)
        for d in cast:#load actors
            matcher=NodeMatcher(graph)
            actor=matcher.match("person").where("_.id="+str(d["id"])).first()
            if (actor==None):#check if exists in our db
                d=person_info(d["id"])
                if (d["profile_path"] == "None" or d["profile_path"] is None):
                    d["profile_path"]= "https://www.theprintworks.com/wp-content/themes/psBella/assets/img/film-poster-placeholder.png"
                print(d)
                actor=Node("person", name=d["name"],birthday=d["birthday"], deathdate=d["deathday"], id=d["id"], profile_path=d["profile_path"], load=False)
                graph.create(actor)
                actors.append(actor)
                acts_in=Relationship.type("acts_in")
                graph.create(acts_in(actor, movie))
                
        for d in directors:#load directors
            matcher=NodeMatcher(graph)
            dir=matcher.match("person").where("_.id="+str(d["id"])).first()
            if (dir is None):#check if exists in our db
                d=person_info(d["id"])
                if (d["profile_path"] == "None" or d["profile_path"] is None):
                    d["profile_path"]= "https://www.theprintworks.com/wp-content/themes/psBella/assets/img/film-poster-placeholder.png"
                else:
                    d["profile_path"]= "https://image.tmdb.org/t/p/w220_and_h330_face" + d["profile_path"]            
                dir=Node("person", name=d["name"],birthday=d["birthday"], deathdate=d["deathday"], id=d["id"], profile_path=d["profile_path"],load=False)
                graph.create(dir)            
            directs=Relationship.type("directs")
            graph.create(directs(dir, movie)) 
            
    else:#if the cast was loaded just do a query to our db
        print("in db")
        for a in  graph.run("MATCH (p:person)-[a:acts_in]->(m:movie) WHERE m.id={x} RETURN p", x=movie["id"]).data():
            actors.append(a["p"])

    genres = list(graph.run("MATCH (m:movie)-[b:belongs_to]->(g:genre) WHERE m.id={x} RETURN g", x= movie["id"]).data())
    movie["genres_names"]=[]
    for g in genres:
        movie["genres_names"].append(g["g"])
    print(movie["genres_names"])


    return render_template('MovieDetail.html',pelicula= movie, actores=actors,len =len(actors), searchType=searchType)


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

#Called from the complete search card in movie search
@app.route('/title/<movie_title>/complete')
def search_movie_complete(movie_title):
    return search_movie(movie_title, True)

@app.route('/title/<movie_title>')
def search_movie(movie_title, force_api_search=False):
    result=[]
    if (not force_api_search):
        LocalResult=True
        #search in the local database
        print(movie_title)
        nodes = graph.run("MATCH (a:movie) WHERE toLower(a.original_title) CONTAINS toLower({x}) RETURN a", x=movie_title).data()
        for x in nodes:
            result.append(x["a"])

    #if not in the local bd, search in the api
    if (len(result)<1):
        LocalResult=False
        print("not in bd")
        result = api_search_movie(movie_title)["results"]

    return render_template('SearchPage.html', peliculas=result, len = len(result), searchType="title", localResult=LocalResult, currentSearch=movie_title)



@app.route('/director', methods=['POST', 'GET'])
def by_director_index():
    if request.method == "POST":
        return redirect('/director/' + request.form.get("user_input"))
    else:
        result= get_10_movies()
        return render_template('SearchPage.html',peliculas=result,len = len(result), searchType="director")


#Called from the complete search card in director search
@app.route('/director/<director_name>/complete')
def search_director_complete(director_name):
    return search_director(director_name, True)

@app.route('/director/<director_name>')
def search_director(director_name, force_api_search=False):
    print(director_name)
    result=[]
    if (not force_api_search):
        LocalResult=True
        nodes = graph.run("MATCH (a:person) WHERE toLower(a.name) CONTAINS toLower({x}) RETURN a", x=director_name).data()
        for x in nodes:
            result.append(x["a"])
        
    #if not in the local bd, search in the api
    if (len(result)<1):
        LocalResult=False
        people = api_search_people(director_name)["results"]
        for d in people:
            print("DIRS")
            print(d)
            matcher=NodeMatcher(graph)
            dir=matcher.match("person").where("_.id="+str(d["id"])).first()
            if (dir==None):
                pinfo= person_info(d["id"])
                dir=Node("person", name=pinfo["name"],birthday=pinfo["birthday"], deathdate=pinfo["deathday"], id=pinfo["id"], profile_path=pinfo["profile_path"], load=False)
                graph.create(dir)

            result.append(dir)

    return render_template('SearchPeoplePage.html', people=result, len = len(result), searchType="director", localResult=LocalResult, currentSearch=director_name)

@app.route("/genres")
def genres_all():
    result=[]
    nodes=graph.run("MATCH (g:genre) RETURN g").data()
    for x in nodes:
        result.append(x["g"])
    return render_template('GenresPage.html', genres=result, len = len(result), searchType="genres")

@app.route('/genres/<genre_id>/complete')
def search_genres_complete(genre_id):
    return search_genres(genre_id, True)

@app.route("/genres/<genre_id>")
def search_genres(genre_id, force_api_search=False):
    result=[]
    print(genre_id)
    query = "MATCH (m:movie)-[b:belongs_to]->(g:genre) WHERE g.id=" + str(genre_id)+" RETURN m"
    nodes=graph.run(query).data()
    print(nodes)
    matcher =NodeMatcher(graph)
    gen=matcher.match("genre").where("_.id="+str(genre_id)).first()
    for x in nodes:
        result.append(x["m"])
    if(not force_api_search):
        LocalResult=True
    else:
        LocalResult=False
        news=api_search_genres_movies(genre_id, gen["page"])
        gen["page"]+=1
        graph.push(gen)
        for p in news["results"]:
            movie=matcher.match("movie").where("_.id="+str(p["id"])).first()
            if (movie is None):
                if (p["poster_path"] == "None" or p["poster_path"] is None):
                    p["poster_path"]= "https://www.theprintworks.com/wp-content/themes/psBella/assets/img/film-poster-placeholder.png"
                else:
                    p["poster_path"]= "https://image.tmdb.org/t/p/w220_and_h330_face" + p["poster_path"]                
                movie=Node("movie", original_title=p["title"],id=p["id"], release_date=p["release_date"],poster_path=p["poster_path"], vote_count=p["vote_count"], vote_average=p["vote_average"], load=False)
                graph.create(movie)
                belongs_to=Relationship.type("belongs_to")
                graph.create(belongs_to(movie, gen))
                result.append(movie)
        
    return render_template('GenreDetail.html', peliculas=result, len=len(result), searchType="genre", localResult=LocalResult, currentSearch=gen)

def api_search_genres_movies(g_id, g_page):
    genres=tmdb.Genres(g_id)
    response=genres.movies(page=g_page)
    return response
def api_search_people(p_name):
    search = tmdb.Search()
    response = search.person(query=p_name)
    for s in search.results:

        if (s["profile_path"] == "None" or s["profile_path"] is None):
            s["profile_path"]= "https://www.theprintworks.com/wp-content/themes/psBella/assets/img/film-poster-placeholder.png"
        else:
            s["profile_path"]= "https://image.tmdb.org/t/p/w220_and_h330_face" + s["profile_path"]

    return response


def api_search_by_actor(actor_id):
    people = tmdb.People(actor_id)
    response = people.movie_credits()
    result=[]
    if ("cast" in response):
        for d in response["cast"]:
            print(d)
            if (d["poster_path"] == "None" or d["poster_path"] is None):
                d["poster_path"]= "https://www.theprintworks.com/wp-content/themes/psBella/assets/img/film-poster-placeholder.png"
            else:
                d["poster_path"]= "https://image.tmdb.org/t/p/w220_and_h330_face" + d["poster_path"]  
            result.append(d)
    return result

def api_search_by_director(director_id):
    people = tmdb.People(director_id)
    response = people.movie_credits()

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
        if (s["poster_path"] == "None" or s["poster_path"] is None):
            s["poster_path"]= "https://www.theprintworks.com/wp-content/themes/psBella/assets/img/film-poster-placeholder.png"
        else:
            s["poster_path"]= "https://image.tmdb.org/t/p/w220_and_h330_face" + s["poster_path"]
            
    matcher=NodeMatcher(graph)
    for p in response["results"]:
        movie=matcher.match("movie").where("_.id="+str(p["id"])).first()
        if (movie is None):
            movie=Node("movie", original_title=p["title"],id=p["id"], release_date=p["release_date"],poster_path=p["poster_path"], vote_count=p["vote_count"], vote_average=p["vote_average"], load=False)
            graph.create(movie) 
            for g in p["genre_ids"]:
                genre=matcher.match("genre").where("_.id="+str(g)).first()
                belongs_to=Relationship.type("belongs_to")
                graph.create(belongs_to(movie, genre))  
        
            
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

def api_get_genre():
    genres=tmdb.Genres()
    response=genres.movie_list()
    matcher=NodeMatcher(graph) 
    for g in response["genres"]:
        gen=matcher.match("genre").where("_.id="+str(g["id"])).first()
        if (gen is None):
            gen=Node("genre", id=g["id"], name=g["name"], page=1)
            graph.create(gen)
    
    


if __name__ == '__main__':
    graph = Graph("bolt://localhost:7687", user=neouser, password=neopass)
    api_get_genre()
    app.run(debug=True)
