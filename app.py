from flask import Flask, render_template, request
from dotenv import load_dotenv
import pandas as pd
import requests
import os
import recommender as rec

load_dotenv()
app = Flask(__name__)
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
PER_PAGE = 24

poster_cache = {}

def get_tmdb_info(title):
    if title in poster_cache:
        return poster_cache[title]
    clean_title = title.rsplit('(', 1)[0].strip()
    info = {"poster": "https://via.placeholder.com/300x450?text=No+Poster", "overview": ""}
    try:
        url = "https://api.themoviedb.org/3/search/movie"
        params = {"api_key": TMDB_API_KEY, "query": clean_title}
        response = requests.get(url, params=params, timeout=5)
        data = response.json()
        if data.get("results"):
            result = data["results"][0]
            if result.get("poster_path"):
                info["poster"] = f"https://image.tmdb.org/t/p/w500{result['poster_path']}"
            info["overview"] = result.get("overview", "")
    except Exception:
        pass
    poster_cache[title] = info
    return info

def to_card(row, with_poster=True):
    card = {
        "id": int(row['movieId']),
        "title": row['title'],
        "year": int(row['year']) if pd.notna(row['year']) else None,
        "genres": row['genres'].replace('|', ', '),
        "rating": row['avg_rating'] if pd.notna(row['avg_rating']) else None,
    }
    if with_poster:
        card["poster"] = get_tmdb_info(row['title'])['poster']
    return card

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/browse')
def browse():
    category = request.args.get('category', 'english')
    page = int(request.args.get('page', 1))
    rows, total = rec.get_movies(category=category, page=page, per_page=PER_PAGE)
    cards = [to_card(r) for _, r in rows.iterrows()]
    total_pages = max(1, (total + PER_PAGE - 1) // PER_PAGE)
    heading = "Tamil Movies" if category == "tamil" else "English Movies"
    return render_template('browse.html', cards=cards, category=category,
                            page=page, total_pages=total_pages, heading=heading)

@app.route('/alphabet')
def alphabet():
    letter = request.args.get('letter')
    page = int(request.args.get('page', 1))
    cards, total_pages = [], 1
    if letter:
        rows, total = rec.get_movies(letter=letter, page=page, per_page=PER_PAGE)
        cards = [to_card(r) for _, r in rows.iterrows()]
        total_pages = max(1, (total + PER_PAGE - 1) // PER_PAGE)
    return render_template('alphabet.html', letters=rec.ALPHABET, letter=letter,
                            cards=cards, page=page, total_pages=total_pages)

@app.route('/year')
def year_view():
    year = request.args.get('year')
    page = int(request.args.get('page', 1))
    cards, total_pages = [], 1
    if year:
        rows, total = rec.get_movies(year=year, page=page, per_page=PER_PAGE)
        cards = [to_card(r) for _, r in rows.iterrows()]
        total_pages = max(1, (total + PER_PAGE - 1) // PER_PAGE)
    return render_template('year.html', years=rec.available_years(), year=year,
                            cards=cards, page=page, total_pages=total_pages)

@app.route('/search')
def search():
    q = request.args.get('q', '').strip()
    results = rec.search_movies(q) if q else rec.movies.iloc[0:0]
    cards = [to_card(r) for _, r in results.iterrows()]
    return render_template('search.html', query=q, cards=cards)

@app.route('/movie/<int:movie_id>')
def movie_detail(movie_id):
    row = rec.get_movie_by_id(movie_id)
    if row is None:
        return "Movie not found", 404
    info = get_tmdb_info(row['title'])
    movie = to_card(row, with_poster=False)
    movie['poster'] = info['poster']
    movie['overview'] = info['overview'] or "No description available."
    similar_rows = rec.recommend_by_id(movie_id, n=6)
    similar = [to_card(r) for _, r in similar_rows.iterrows()]
    return render_template('movie.html', movie=movie, similar=similar)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))