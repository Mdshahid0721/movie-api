import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Load datasets
movies = pd.read_csv("movies.csv")
ratings = pd.read_csv("ratings.csv")

# Remove junk titles
movies = movies[~movies['title'].str.contains("Interview", case=False, na=False)]
movies = movies[~movies['title'].str.contains("Conversation", case=False, na=False)]
movies = movies[~movies['title'].str.contains("Special", case=False, na=False)]
movies = movies[~movies['title'].str.contains("Documentary", case=False, na=False)]

# Fill missing values
movies['genres'] = movies['genres'].fillna('')
movies['overview'] = movies['overview'].fillna('')

# 🚫 DO NOT REMOVE ROWS HERE

# Create content feature
movies['content'] = movies['genres'] + " " + movies['overview']

# TF-IDF Vectorization
tfidf = TfidfVectorizer(stop_words='english')
tfidf_matrix = tfidf.fit_transform(movies['content'])

content_similarity = cosine_similarity(tfidf_matrix, tfidf_matrix)

# Collaborative (mean rating)
movie_avg_rating = ratings.groupby('movieId')['rating'].mean()

def hybrid_recommend(movie_title, user_id, top_n=6):

    matches = movies[movies['title'].str.contains(movie_title, case=False, na=False)]

    if matches.empty:
        return []

    idx = matches.index[0]

    similarity_scores = list(enumerate(content_similarity[idx]))
    similarity_scores = sorted(similarity_scores, key=lambda x: x[1], reverse=True)[1:top_n+20]

    recommendations = []

    for i, content_score in similarity_scores:

        movie_id = movies.iloc[i]['movieId']
        collab_score = movie_avg_rating.get(movie_id, 0)

        final_score = (0.6 * content_score) + (0.4 * (collab_score / 5))

        recommendations.append((
            movies.iloc[i]['title'],
            final_score
        ))

    recommendations = sorted(recommendations, key=lambda x: x[1], reverse=True)[:top_n]

    return recommendations