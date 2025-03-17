from flask import Blueprint, render_template, request
from app.database import Database

queries_bp = Blueprint("query", __name__)


@queries_bp.route("/list_tables")
def list_tables():
    """List all tables in the database."""

    # >>>> TODO 1: Write a query to list all the tables in the database. <<<<

    query = "show tables;"

    with Database() as db:
        tables = db.execute(query)
    return render_template("list_tables.html", tables=tables)


@queries_bp.route("/search_movie", methods=["POST"])
def search_movie():
    """Search for movies by name."""
    movie_name = request.form["movie_name"]

    # >>>> TODO 2: Search Motion Picture by Motion picture name. <<<<
    #              List the movie `name`, `rating`, `production` and `budget`.

    query = ""
    query = """SELECT name, rating, production, budget FROM MotionPicture WHERE name = %s"""
    
    with Database() as db:
        movies = db.execute(query, (f"%{movie_name}%",))
    return render_template("search_results.html", movies=movies)


@queries_bp.route("/search_liked_movies", methods=["POST"])
def search_liked_movies():
    """Search for movies liked by a specific user."""
    user_email = request.form["user_email"]

    # >>>> TODO 3: Find the movies that have been liked by a specific user’s email. <<<<
    #              List the movie `name`, `rating`, `production` and `budget`.

    query = "SELECT m.name, m.rating, m.production, m.budget  FROM MotionPicture M, Likes P where M.id = P.mpid and P.uemail = %s and M.id in (select mpid from Movie)"

    with Database() as db:
        movies = db.execute(query, (user_email,))
    return render_template("search_results.html", movies=movies)


@queries_bp.route("/search_by_country", methods=["POST"])
def search_by_country():
    """Search for movies by country using the Location table."""
    country = request.form["country"]

    # >>>> TODO 4: Search motion pictures by their shooting location country. <<<<
    #              List only the motion picture names without any duplicates.

    query = """SELECT name FROM MotionPicture WHERE id IN (SELECT mpid FROM Location WHERE country = %s)"""

    with Database() as db:
        movies = db.execute(query, (country,))
    return render_template("search_results_by_country.html", movies=movies)


@queries_bp.route("/search_directors_by_zip", methods=["POST"])
def search_directors_by_zip():
    """Search for directors and the series they directed by zip code."""
    zip_code = request.form["zip_code"]

    # >>>> TODO 5: List all directors who have directed TV series shot in a specific zip code. <<<<
    #              List the director name and TV series name only without duplicates.

    query = """ Select DISTINCT People.name, MotionPicture.name FROM role, MotionPicture, Likes, People, Location, Series
                where role_name = "Director" AND role.mpid = Location.mpid AND Location.zip = %s
                and role.mpid = MotionPicture.id AND Series.mpid = MotionPicture.id and People.id = role.pid;"""

    with Database() as db:
        results = db.execute(query, (zip_code,))
    return render_template("search_directors_results.html", results=results)


@queries_bp.route("/search_awards", methods=["POST"])
def search_awards():
    """Search for award records where the award count is greater than `k`."""
    k = int(request.form["k"])

    # >>>> TODO 6: Find the people who have received more than “k” awards for a single motion picture in the same year. <<<<
    #              List the person `name`, `motion picture name`, `award year` and `award count`.

    query = """SELECT P.name, M.name, award_year, COUNT(*) AS award_count 
                FROM People P, MotionPicture M, Award A 
                WHERE P.id = A.pid AND M.id = A.mpid 
                GROUP BY P.name, M.name, award_year 
                HAVING award_count > %s"""

    with Database() as db:
        results = db.execute(query, (k,))
    return render_template("search_awards_results.html", results=results)


@queries_bp.route("/find_youngest_oldest_actors", methods=["GET"])
def find_youngest_oldest_actors():
    """
    Find the youngest and oldest actors based on the difference 
    between the award year and their date of birth.
    """

    # >>>> TODO 7: Find the youngest and oldest actors to win at least one award. <<<<
    #              List the actor names and their age (at the time they received the award). 
    #              The age should be computed from the person’s date of birth to the award winning year only. 
    #              In case of a tie, list all of them.

    query = """ select people.name, CAST(Award.award_year as INT) - CAST(YEAR(People.dob) as INT)  
                from People, Award 
                where Award.pid = people.id  """

    with Database() as db:
        actors = db.execute(query)
    
    # Filter out actors with null ages (if any)
    actors = [actor for actor in actors if actor[1] is not None]
    if actors:
        min_age = min(actors, key=lambda x: x[1])[1]
        max_age = max(actors, key=lambda x: x[1])[1]
        youngest_actors = [actor for actor in actors if actor[1] == min_age]
        oldest_actors = [actor for actor in actors if actor[1] == max_age]
        return render_template(
            "actors_by_age.html",
            youngest_actors=youngest_actors,
            oldest_actors=oldest_actors,
        )
    else:
        return render_template(
            "actors_by_age.html", youngest_actors=[], oldest_actors=[]
        )


@queries_bp.route("/search_producers", methods=["POST"])
def search_producers():
    """
    Search for American producers based on a minimum box office collection and maximum budget.
    """
    box_office_min = float(request.form["box_office_min"])
    budget_max = float(request.form["budget_max"])

    # >>>> TODO 8: Find the American [USA] Producers who had a box office collection of more than or equal to “X” with a budget less than or equal to “Y”. <<<< 
    #              List the producer `name`, `movie name`, `box office collection` and `budget`.

    query = """SELECT MP.Production, MP.name, M.boxoffice_collection, MP.budget 
                FROM MotionPicture MP, Movie M 
                WHERE MP.id = M.mpid AND MP.id IN (SELECT mpid FROM Location WHERE country = 'USA') 
                AND M.boxoffice_collection >= %s AND MP.budget <= %s"""

    with Database() as db:
        results = db.execute(query, (box_office_min, budget_max))
    return render_template("search_producers_results.html", results=results)


@queries_bp.route("/search_multiple_roles", methods=["POST"])
def search_multiple_roles():
    """
    Search for people who have multiple roles in movies with a rating above a given threshold.
    """
    rating_threshold = float(request.form["rating_threshold"])

    # >>>> TODO 9: List the people who have played multiple roles in a motion picture where the rating is more than “X”. <<<<
    #              List the person’s `name`, `motion picture name` and `count of number of roles` for that particular motion picture.

    query = """SELECT P.name, MP.name, Count(R1.role_name) as role_count
                FROM MotionPicture MP, People P, Role R1
                where  MP.rating > %s and MP.id = R1.mpid and P.id = R1.pid
                GROUP BY P.name, MP.name
                HAVING role_count > 1;"""

    with Database() as db:
        results = db.execute(query, (rating_threshold,))
    return render_template("search_multiple_roles_results.html", results=results)


@queries_bp.route("/top_thriller_movies_boston", methods=["GET"])
def top_thriller_movies_boston():
    """Display the top 2 thriller movies in Boston based on rating."""

    # >>>> TODO 10: Find the top 2 rates thriller movies (genre is thriller) that were shot exclusively in Boston. <<<<
    #               This means that the movie cannot have any other shooting location. 
    #               List the `movie names` and their `ratings`.

    query = """SELECT name, rating FROM MotionPicture 
                WHERE id IN (SELECT mpid FROM Genre WHERE genre_name = 'Thriller') 
                AND id NOT IN (SELECT mpid FROM Location WHERE city != 'Boston') 
                AND id IN (SELECT mpid FROM Movie)
                ORDER BY rating DESC LIMIT 2"""

    with Database() as db:
        results = db.execute(query)
    return render_template("top_thriller_movies_boston.html", results=results)



@queries_bp.route("/search_movies_by_likes", methods=["POST"])
def search_movies_by_likes():
    """
    Search for movies that have received more than a specified number of likes,
    where the liking users are below a certain age.
    """
    min_likes = int(request.form["min_likes"])
    max_age = int(request.form["max_age"])

    # >>>> TODO 11: Find all the movies with more than “X” likes by users of age less than “Y”. <<<<
    #               List the movie names and the number of likes by those age-group users.

    query = """select MotionPicture.name, Count(uemail) as num_likes 
                from likes L, Users U, MotionPicture
                where U.age < %s and L.uemail = U.email and MotionPicture.id = L.mpid and MotionPicture.id in (select mpid from Movie)
                group by L.mpid
                Having num_likes > %s; """

    with Database() as db:
        results = db.execute(query, (max_age, min_likes))
    return render_template("search_movies_by_likes_results.html", results=results)


@queries_bp.route("/actors_marvel_warner", methods=["GET"])
def actors_marvel_warner():
    """
    List actors who have appeared in movies produced by both Marvel and Warner Bros.
    """

    # >>>> TODO 12: Find the actors who have played a role in both “Marvel” and “Warner Bros” productions. <<<<
    #               List the `actor names` and the corresponding `motion picture names`.

    query = """WITH X AS (SELECT pid, production FROM Role JOIN MotionPicture ON mpid = id) 
               SELECT P.name, M.name FROM People P JOIN Role R ON P.id = R.pid JOIN MotionPicture M ON R.mpid = M.id 
               WHERE P.id IN (SELECT pid FROM Role WHERE role_name = 'Actor') 
               AND P.id IN (SELECT pid FROM X WHERE production = 'Marvel') 
               AND P.id IN (SELECT pid FROM X WHERE Production = 'Warner Bros')"""

    with Database() as db:
        results = db.execute(query)
    return render_template("actors_marvel_warner.html", results=results)


@queries_bp.route("/movies_higher_than_comedy_avg", methods=["GET"])
def movies_higher_than_comedy_avg():
    """
    Display movies whose rating is higher than the average rating of comedy movies.
    """

    # >>>> TODO 13: Find the motion pictures that have a higher rating than the average rating of all comedy (genre) motion pictures. <<<<
    #               Show the names and ratings in descending order of ratings.

    query = """Select MP.name, MP.rating from MotionPicture MP 
                where MP.rating > (select Avg(MP.rating ) from MotionPicture MP, Genre G 
                                    where MP.id = G.mpid and G.genre_name = "comedy" and MP.id in (select mpid from Movie)) 
                order by Mp.rating desc"""

    with Database() as db:
        results = db.execute(query)
    return render_template("movies_higher_than_comedy_avg.html", results=results)


@queries_bp.route("/top_5_movies_people_roles", methods=["GET"])
def top_5_movies_people_roles():
    """
    Display the top 5 movies that involve the most people and roles.
    """

    # >>>> TODO 14: Find the top 5 movies with the highest number of people playing a role in that movie. <<<<
    #               Show the `movie name`, `people count` and `role count` for the movies.

    query = """SELECT M.name, COUNT(DISTINCT P.id) AS people_count, COUNT( R.role_name) AS role_count 
                FROM MotionPicture M JOIN Role R ON M.id = R.mpid JOIN People P ON R.pid = P.id 
                where M.id in (select mpid from Movie)
                GROUP BY M.id 
                ORDER BY people_count DESC, role_count DESC LIMIT 5"""

    with Database() as db:
        results = db.execute(query)
    return render_template("top_5_movies_people_roles.html", results=results)


@queries_bp.route("/actors_with_common_birthday", methods=["GET"])
def actors_with_common_birthday():
    """
    Find pairs of actors who share the same birthday.
    """

    # >>>> TODO 15: Find actors who share the same birthday. <<<<
    #               List the actor names (actor 1, actor 2) and their common birthday.

    query = """select P1.name, P2.name, P1.birthday from 
    (select P.name, P.id, Concat(MonthName(P.dob), " ", DayOfMonth(P.dob)) as birthday from People P where P.id in (select distinct R.pid from Role R where role_name = "actor")) P1,
    (select P.name, P.id, Concat(MonthName(P.dob), " ", DayOfMonth(P.dob)) as birthday  from People P where P.id in (select distinct R.pid from Role R where role_name = "actor")) P2
    where P1.id < P2.id and P1.birthday = P2.birthday""" 

    with Database() as db:
        results = db.execute(query)
    return render_template("actors_with_common_birthday.html", results=results)
