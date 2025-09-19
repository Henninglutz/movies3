from __future__ import annotations
import statistics
from sqlalchemy import create_engine, text
import os
import requests
import random
from environment import OMDB_API_KEY

# Define the database URL
DB_URL = "sqlite:///movies.db"

engine = create_engine(DB_URL, echo=True)

def _get_api_key(explicit_key: str | None = None) -> str:
    key = os.environ.get("OMDB_API_KEY")
    if not key:
        raise RuntimeError("OMDB_API_KEY fehlt – setze ihn als Umgebungsvariable oder übergib api_key=...")
    return key


# Create the movies table if it does not exist
with engine.connect() as connection:
    connection.execute(text("""
        CREATE TABLE IF NOT EXISTS movies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT UNIQUE NOT NULL,
            year INTEGER NOT NULL,
            rating REAL NOT NULL,
            poster TEXT NOT NULL
        )
    """))
    connection.commit()


def list_movies():
    """Retrieve all movies from the database."""
    with engine.connect() as connection:
        rows = connection.execute(text("SELECT title, year, rating, poster FROM movies")).mappings().all()

        movies = {
            r["title"]:
                {
                    "year": r["year"],
                    "rating": r["rating"],
                    "poster_url": r["poster"]
                }
            for r in rows
        }

        for title, info in movies.items():
            print(f"{title} ({info['year']}), rating={info['rating']}, poster={info['poster_url']}")

        return movies


def delete_movie(title:str):
    """Delete a movie from the database."""
    with engine.begin() as conn:
        result = conn.execute(
            text(
                "DELETE from movies "
                 "WHERE title = :t"),
            {"t": title},
        )


def update_movie(title: str, rating: float) -> int:
    with engine.begin() as conn:
        result = conn.execute(
            text(
                "UPDATE movies SET rating = :r "
                 "WHERE title = :t"),
            {"t": title, "r": rating},
        )
    print(f"Movie '{title}' updated successfully with new rating: {rating}.")
    return result.rowcount


def stats_movies_new():
#get database for further analysis:-->> statistics
    with (engine.connect() as connection):
        rows = connection.execute(text("SELECT title, year, rating, poster FROM movies")).mappings().all()

#start of specific statistic
        dict_statistic = {r["title"]: float(r["rating"]) for r in rows}
        ratings = list(dict_statistic.values())
        average_rating = sum(ratings) / len(ratings)
        print(f"Average rating: {average_rating:.2f}")

        median_movies = statistics.median(ratings)
        print(f"Median rating: {median_movies:.2f}")

        best_title = max(dict_statistic, key=dict_statistic.get)
        print(f"Best movie: {best_title}, {dict_statistic[best_title]:.2f}")

        worst_title = min(dict_statistic, key=dict_statistic.get)
        print(f"Worst movie: {worst_title}, {dict_statistic[worst_title]:.2f}")

def random_movie():
    movies = list_movies()
    title, info = random.choice(list(movies.items()))
    print(f"{title} ({info['year']}), rating={info['rating']}, poster={info['poster_url']}")

#funtion with new SQL request, to search from scratch - stabil function
def search_movie():
    with engine.connect() as conn:
        rows = conn.execute(
            text(r"""
                SELECT title, year, rating, poster
                FROM movies
            """)
        ).mappings().all()

    user_search_title = input("Search title: ")
    user_search_title_lower = user_search_title.lower()

    for r in rows:
        title = r["title"]
        title_lower = title.lower()
        if title_lower == user_search_title_lower:
            print(f"{title_lower} ({r['year']}), rating={r['rating']}, poster={r['poster']}")
            return

#sorted by rating via SQL request
def sorted_movies():
    with engine.connect() as conn:
        rows = conn.execute(
            text(r"""
                SELECT title, year, rating, poster
                FROM movies
                ORDER BY rating DESC
            """)
        ).mappings().all()
    for r in rows:
        print(r["title"], r["year"], r["rating"], r["poster"])


#funtion helps to get movies fron URL source
def get_movie_info_from_omdb(title: str, api_key: str, timeout: int = 10) -> dict:
    api_key = _get_api_key(api_key)
    resp = requests.get("https://omdbapi.com/", params={"t": title, "apikey": api_key},timeout=timeout)
    resp.raise_for_status()
    data = resp.json()
    if data.get("Response") != "True":
        raise ValueError(f"OMDb: {data.get('Error', 'not found')}")

    title_norm = data.get("Title")
    year_str = (data.get("Year"))
    year = int(year_str)
    rating_str = data.get("imdbRating")
    rating = float(rating_str)
    poster_url = data.get("Poster")

    return {"title": title_norm, "year": year, "rating": rating, "poster": poster_url}


def add_movie_with_api(title:str, api_key:str) -> dict:
    movie = get_movie_info_from_omdb(title, api_key=api_key)
    sql = """
       INSERT INTO movies (title, year, rating, poster)
       VALUES (:t, :y, :r, :p)
       ON CONFLICT(title) DO UPDATE SET
           year   = excluded.year,
           rating = excluded.rating,
           poster = excluded.poster
       """
    with engine.begin() as conn:
        conn.execute(text(sql), {"t": movie["title"],
                                 "y": movie["year"],
                                 "r": movie["rating"],
                                 "p": movie["poster"]
                                 })
    return movie