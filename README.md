# 🎬 Movie Recommender

A content-based movie recommendation web app that suggests similar movies based on genre similarity, using TF-IDF vectorization and cosine similarity.

## Features
- Genre-based movie recommendations using TF-IDF + cosine similarity (scikit-learn)
- Live movie posters via The Movie Database (TMDb) API
- Sort movies alphabetically or by release year
- Adjustable number of recommendations
- Built with Flask and a custom-designed responsive UI

## Tech Stack
- **Backend:** Python, Flask
- **ML:** pandas, scikit-learn (TF-IDF, cosine similarity)
- **Data:** MovieLens dataset (ml-latest-small)
- **Frontend:** HTML, CSS, Jinja2 templating
- **API:** TMDb (The Movie Database)

## How It Works
1. Movie genres are converted into TF-IDF vectors
2. Cosine similarity is computed between all movies based on genre overlap
3. When a user selects a movie, the top N most similar movies are returned
4. Posters are fetched live from TMDb for each recommendation

## Setup
1. Clone this repo
2. Install dependencies: `pip install -r requirements.txt`
3. Create a `.env` file with your TMDb API key: `TMDB_API_KEY=your_key_here`
4. Run: `python app.py`
5. Open `http://127.0.0.1:5000`

## Dataset
This project uses the [MovieLens Latest Small dataset](https://grouplens.org/datasets/movielens/latest/) from GroupLens Research.