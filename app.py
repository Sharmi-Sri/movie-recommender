from flask import Flask, render_template, request
from recommender import recommend, titles_alphabetical, titles_by_year
from dotenv import load_dotenv
import requests
import os

load_dotenv()

app = Flask(__name__)

TMDB_API_KEY = os.getenv("TMDB_API_KEY")

def get_poster(title):
    # TMDb search needs a clean title without the year, e.g. "Toy Story" not "Toy Story (1995)"
    clean_title = title.rsplit('(', 1)[0].strip()

    url = "https://api.themoviedb.org/3/search/movie"
    params = {"api_key": TMDB_API_KEY, "query": clean_title}

    try:
        response = requests.get(url, params=params, timeout=5)
        data = response.json()
        if data.get("results"):
            poster_path = data["results"][0].get("poster_path")
            if poster_path:
                return f"https://image.tmdb.org/t/p/w500{poster_path}"
    except Exception:
        pass

    return "https://via.placeholder.com/300x450?text=No+Poster"

@app.route('/', methods=['GET', 'POST'])
def home():
    recommendations = []
    selected_movie = None
    num_results = 5
    sort_by = request.values.get('sort_by', 'alphabetical')

    titles = titles_by_year if sort_by == 'year' else titles_alphabetical

    if request.method == 'POST':
        selected_movie = request.form.get('movie')
        num_results = int(request.form.get('num_results', 5))
        results = recommend(selected_movie, n=num_results)
        recommendations = [{"title": t, "poster": get_poster(t)} for t in results]

    return render_template('index.html',
                            titles=titles,
                            recommendations=recommendations,
                            selected_movie=selected_movie,
                            num_results=num_results,
                            sort_by=sort_by)

if __name__ == '__main__':
    app.run(debug=True)