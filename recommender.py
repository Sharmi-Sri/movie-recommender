import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

ratings = pd.read_csv('data/ratings.csv')
movies = pd.read_csv('data/movies.csv')

movies['genres_clean'] = movies['genres'].str.replace('|', ' ', regex=False)
movies['year'] = pd.to_numeric(movies['title'].str.extract(r'\((\d{4})\)')[0], errors='coerce')
movies['language'] = movies['movieId'].apply(lambda x: 'tamil' if x >= 300000 else 'english')

avg_ratings = ratings.groupby('movieId')['rating'].mean().round(1)
movies['avg_rating'] = movies['movieId'].map(avg_ratings)

def _first_letter(title):
    for ch in title:
        if ch.isalpha():
            return ch.upper()
    return '#'

movies['first_letter'] = movies['title'].apply(_first_letter)

tfidf = TfidfVectorizer()
genre_matrix = tfidf.fit_transform(movies['genres_clean'])

id_indices = pd.Series(movies.index, index=movies['movieId'])

ALPHABET = list('ABCDEFGHIJKLMNOPQRSTUVWXYZ') + ['#']

def available_years():
    return sorted(movies['year'].dropna().unique().astype(int).tolist(), reverse=True)

def get_movies(category='all', letter=None, year=None, page=1, per_page=24):
    subset = movies
    if category == 'english':
        subset = subset[subset['language'] == 'english']
    elif category == 'tamil':
        subset = subset[subset['language'] == 'tamil']
    if letter:
        subset = subset[subset['first_letter'] == letter.upper()]
    if year:
        subset = subset[subset['year'] == int(year)]
    subset = subset.sort_values('title')
    total = len(subset)
    start = (page - 1) * per_page
    return subset.iloc[start:start + per_page], total

def search_movies(query, limit=60):
    q = query.strip().lower()
    if not q:
        return movies.iloc[0:0]
    words = q.split()
    q_nospace = q.replace(' ', '')

    def score(row):
        title = row['title'].lower()
        title_nospace = title.replace(' ', '')
        genre = row['genres_clean'].lower()

        if title == q:
            return 100
        if title.startswith(q):
            return 90
        if q in title:
            return 80
        if all(w in title for w in words):
            return 70
        if q_nospace in title_nospace:
            return 65
        if q in genre:
            return 60
        if any(w in genre for w in words):
            return 50
        return 0

    scored = movies.copy()
    scored['score'] = scored.apply(score, axis=1)
    scored = scored[scored['score'] > 0]
    return scored.sort_values(['score', 'title'], ascending=[False, True]).head(limit)

def get_movie_by_id(movie_id):
    idx = id_indices.get(int(movie_id))
    if idx is None:
        return None
    return movies.loc[idx]

def recommend_by_id(movie_id, n=6):
    idx = id_indices.get(int(movie_id))
    if idx is None:
        return movies.iloc[0:0]
    sim_scores = linear_kernel(genre_matrix[idx], genre_matrix).flatten()
    scores = sorted(enumerate(sim_scores), key=lambda x: x[1], reverse=True)[1:n+1]
    return movies.iloc[[i for i, _ in scores]]