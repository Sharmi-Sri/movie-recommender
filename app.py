from flask import Flask, render_template, request
from recommender import recommend, get_titles
from dotenv import load_dotenv
import requests
import os

load_dotenv()

app = Flask(__name__)

TMDB_API_KEY = os.getenv("TMDB_API_KEY")

def get_poster(title):
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
    category = request.values.get('category', 'all')

    if request.method == 'POST':
        selected_movie = request.form.get('movie')
        num_results = int(request.form.get('num_results', 5))
        sort_by = request.form.get('sort_by', sort_by)
        category = request.form.get('category', category)
        results = recommend(selected_movie, n=num_results)
        recommendations = [{"title": t, "poster": get_poster(t)} for t in results]

    titles = get_titles(category, sort_by)

    return render_template('index.html',
                            titles=titles,
                            recommendations=recommendations,
                            selected_movie=selected_movie,
                            num_results=num_results,
                            sort_by=sort_by,
                            category=category)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))