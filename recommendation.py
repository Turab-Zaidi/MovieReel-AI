import pandas as pd
import pickle
import numpy as np
from data.director import TOP_DIRECTORS
#*****************************General Recommendation*********************************************
def get_general_recommendations(top_k=50):
    movies = pd.read_csv('data/curated_data (1).csv')
    movies['release_date'] = pd.to_datetime(movies['release_date'], errors='coerce')
    
    recent_movies = movies[
        (movies['director'].isin(TOP_DIRECTORS))
    ]    
    recent_movies = recent_movies.sort_values(
        'vote_average', 
        ascending=False
    )
    return recent_movies.head(top_k)


#*****************************Content Based Recommendation*********************************************
def get_content_based_recommendations(user_ratings_df, top_k=1):
    """Recommend movies based on director, actor, and genre similarity"""
    
    if len(user_ratings_df) == 0:
        return get_general_recommendations(top_k)
    
    movies = pd.read_csv('data/curated_data (1).csv')
    
    liked_movie_ids = user_ratings_df['movie_id'].values
    liked_movies = movies[movies['movie_id'].isin(liked_movie_ids)]
    
    if len(liked_movies) == 0:
        return get_general_recommendations(top_k)
    
    user_profile = {
        'directors': set(),
        'actors': set(),
        'genres': set()
    }
    
    for _, movie in liked_movies.iterrows():
        if pd.notna(movie['director']) and movie['director'] != "Unknown":
            user_profile['directors'].add(movie['director'])
        
        if 'top_actors_str' in movie and pd.notna(movie['top_actors_str']):
            actors = [a.strip() for a in movie['top_actors_str'].split(',') if a.strip()]
            user_profile['actors'].update(actors[:3])  # Top 3 actors
        
        if 'genres' in movie and pd.notna(movie['genres']):
            genres = [g.strip() for g in movie['genres'].split(',') if g.strip()]
            user_profile['genres'].update(genres)
    
    candidate_movies = movies[~movies['movie_id'].isin(liked_movie_ids)].copy()
    
    candidate_movies['director_match'] = candidate_movies['director'].isin(user_profile['directors'])
    candidate_movies['genres_list'] = candidate_movies['genres'].apply(
        lambda x: set([g.strip() for g in x if g.strip()]) if isinstance(x, list) or pd.notna(x) else set()
    )
    
    candidate_movies['actors_list'] = candidate_movies['top_actors'].apply(
        lambda x: set([a.strip() for a in x if a.strip()]) if isinstance(x, list) or pd.notna(x) else set()
    )
    
    def compute_score(row):
        score = 0.0
        
        if row['director_match']:
            score += 0.3
        
        actor_overlap = len(row['actors_list'].intersection(user_profile['actors']))
        score += 0.35 * min(actor_overlap / 3, 1.0)  
        
        genre_jaccard = len(row['genres_list'].intersection(user_profile['genres'])) / len(user_profile['genres']) if user_profile['genres'] else 0
        score += 0.25 * genre_jaccard
        
        popularity_norm = row['vote_average'] 
        score += 0.1 * popularity_norm
        
        return score
    
    candidate_movies['content_score'] = candidate_movies.apply(compute_score, axis=1)
    
    recommendations = candidate_movies.sort_values('content_score', ascending=False).head(top_k * 2)
    
    final_recs = []
    director_count = {}
    
    for _, movie in recommendations.iterrows():
        director = movie['director']
        if director not in director_count:
            director_count[director] = 0
        if director_count[director] < 2:  
            final_recs.append(movie)
            director_count[director] += 1
        if len(final_recs) >= top_k:
            break
    

    
    return pd.DataFrame(final_recs)


#*****************************NCF Based Recommendation*********************************************

def get_ncf_recommendations(user_ratings_df, top_k=12):
    """Use pseudo-user embedding from liked movies"""
    
    movies = pd.read_csv('data/curated_data (1).csv')
    
    liked_movie_ids = user_ratings_df['movie_id'].values
    with open('models/ncf_embeddings.pkl','rb') as data:
        data = pickle.load(data)
    item_enc = data['item_enc']
    item_embeddings = data['item_embeddings']
    try:
        item_indices = item_enc.transform(liked_movie_ids)
    except:
        return get_content_based_recommendations(user_ratings_df, top_k)
    
    liked_embs = item_embeddings[item_indices]
    pseudo_user_emb = liked_embs.mean(axis=0)
    
    scores = item_embeddings @ pseudo_user_emb
    top_indices = np.argsort(scores)[::-1][:3*top_k ] 
    
    movie_ids = item_enc.inverse_transform(top_indices)
    
    recs = movies[movies['movie_id'].isin(movie_ids)].sort_values(
    by='vote_average', 
    ascending=False
).head(top_k)
    return recs