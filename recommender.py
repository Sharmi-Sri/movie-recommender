import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

# Load data
ratings = pd.read_csv('data/ratings.csv')
movies = pd.read_csv('data/movies.csv')

# Replace '|' with spaces so TF-IDF treats each genre as a separate word
movies['genres_clean'] = movies['genres'].str.replace('|', ' ', regex=False)

# Extract release year from title, e.g. "Toy Story (1995)" -> 1995
movies['year'] = movies['title'].str.extract(r'\((\d{4})\)')
movies['year'] = pd.to_numeric(movies['year'], errors='coerce')

# Tag language based on movieId range (Tamil additions used IDs 300000+)
movies['language'] = movies['movieId'].apply(lambda x: 'tamil' if x >= 300000 else 'english')

# Convert genres into TF-IDF vectors (sparse matrix, memory-light)
tfidf = TfidfVectorizer()
genre_matrix = tfidf.fit_transform(movies['genres_clean'])

# Build a lookup: movie title -> row index
indices = pd.Series(movies.index, index=movies['title']).drop_duplicates()

def get_titles(category='all', sort_by='alphabetical'):
    """Return a list of titles filtered by category and sorted as requested."""
    subset = movies

    if category == 'english':
        subset = subset[subset['language'] == 'english']
    elif category == 'tamil':
        subset = subset[subset['language'] == 'tamil']

    if sort_by == 'year':
        subset = subset.sort_values(['year', 'title'], ascending=[False, True])
    else:
        subset = subset.sort_values('title')

    return subset['title'].tolist()

def recommend(title, n=5):
    if title not in indices:
        return []

    idx = indices[title]

    # Compute similarity for just this one movie against all others, on demand
    sim_scores = linear_kernel(genre_matrix[idx], genre_matrix).flatten()

    scores = list(enumerate(sim_scores))
    scores = sorted(scores, key=lambda x: x[1], reverse=True)
    scores = scores[1:n+1]  # skip the movie itself

    movie_indices = [i[0] for i in scores]
    return movies['title'].iloc[movie_indices].tolist()