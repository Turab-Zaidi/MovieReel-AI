import google.generativeai as genai
import pandas as pd

def generate_ai_explanation(user_profile, movie, api_key):
    """Generate AI explanation using Gemini"""
    genai.configure(api_key=api_key)
    
    system_prompt = """
    You are MovieReel AI, a cinematic expert who explains movie recommendations with emotional intelligence and storytelling flair.
    
    Your job is to explain why a movie is recommended to a user based on:
    - Their taste (favorite directors, actors, genres)
    - The movie's plot, themes, and style
    - Emotional or thematic connections to films they've liked
    - Your explanation should be very personal to the user , use the user profile effectively
    
    Guidelines:
    - Be warm, insightful, and slightly poetic — like a film critic who knows the user personally
    - Keep explanations to 2-3 sentences
    - Mention specific connections: director, actor, genre, mood, or theme
    - Do not use markdown, emojis, or technical terms like "based on your preferences"
    - Never say "I recommend" — say "we think you'll love" or "this might resonate"
    
    Example:
    "We think you'll love Arrival because it shares the mind-bending mystery of Arrival, but with a deeply emotional core. Like Villeneuve's other films, it's visually stunning and lingers in your mind long after."
    """
    
    prompt = f"""
    User Profile:
    - Loves directors: {', '.join(list(user_profile['liked_directors'])[:2])}
    - Enjoys actors: {', '.join(list(user_profile['liked_actors'])[:3])}
    - Favorite genres: {', '.join(list(user_profile['liked_genres'])[:3])}
  

    Movie Recommended:
    - Title: {movie['title']}
    - Director: {movie['director']}
    - Stars: {', '.join(movie['top_actors'].split(', ')[:3]) if 'top_actors_str' in movie and pd.notna(movie['top_actors']) else 'Unknown'}
    - Genres: {', '.join(movie['genres'].split(', ') if 'genres' in movie and pd.notna(movie['genres']) else ['Unknown'])}
    - Plot: {movie['plot'] if 'plot' in movie and pd.notna(movie['plot']) else 'No plot available'}

    Explain why we think the user will love this movie. Make it personal, emotional, and insightful.
    """
    
    try:
        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash-lite",
            system_instruction=system_prompt
        )
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"This {movie['genres'].split(',')[0] if 'genres' in movie else 'film'} shares themes with movies you've enjoyed and has excellent reviews (⭐ {movie['vote_average']}/10)."
    


    

def get_personality(user_ratings_df):
    

    movies_df = pd.read_csv('data/curated_data (1).csv')
    liked_movies = movies_df[movies_df['movie_id'].isin(user_ratings_df['movie_id'])]
    
    directors = [d for d in liked_movies['director'].dropna().tolist()]
    genres = [g for genres in liked_movies['genres'].dropna() for g in genres.split(', ')]
    actors = [a for actors in liked_movies['top_actors'].dropna() for a in actors.split(', ')]
    
    from collections import Counter
    top_directors = [d for d, _ in Counter(directors).most_common(3)]
    top_genres = [g for g, _ in Counter(genres).most_common(3)]
    top_actors = [a for a, _ in Counter(actors).most_common(3)]
    
    prompt = f"""
You are a cinematic personality expert. Create a fun, engaging cinematic identity for a movie lover.

Based on their preferences:
- Directors they like: {', '.join(top_directors)}
- Genres they prefer: {', '.join(top_genres)}
- Actors they enjoy: {', '.join(top_actors)}

Create a creative cinematic archetype (e.g., 'Neo-Noir Dreamer', 'Genre Hopper') with:
- A fun name (bolded)
- A short, witty description like 6-7 lines
- Many relevant emojis in middle and at the end(e.g., 🎬, 🕶️, 🌌, 🎭)
- Keep it warm and insightful


Format:
## **[PERSONALITY NAME]**
[Description with emojis]
"""
    model = genai.GenerativeModel(
            model_name="gemini-2.5-flash-lite",
            system_instruction=prompt
        )
    response = model.generate_content(prompt)
    return response.text.strip()


def get_taste_evolution(user_ratings_df):


    movies_df = pd.read_csv('data/curated_data (1).csv')


    user_ratings_with_movies = user_ratings_df.merge(
        movies_df[['movie_id', 'title', 'plot', 'release_date','genres']], 
        left_on='movie_id', 
        right_on='movie_id', 
        how='left'
    )
    
    user_ratings_with_movies['timestamp'] = pd.to_datetime(user_ratings_with_movies['timestamp'])
    
    if len(user_ratings_with_movies) > 10:
        user_ratings_with_movies = user_ratings_with_movies.sample(n=10, random_state=42).sort_values('timestamp')
    
    movie_entries = []
    for _, row in user_ratings_with_movies.iterrows():
        plot = row['plot'] if pd.notna(row['plot']) else "No plot available"
        movie_entries.append(f"• **{row['title']}** : **genres - {row['genres']}** : {plot}")
    
    prompt = f"""
You are a cinematic taste analyst. Help users understand their movie journey.

Based on their viewing history in chronological order:
{chr(10).join(movie_entries)}

Analyze their taste evolution with:
- How their emotional or thematic preferences have changed
- Any narrative or stylistic shifts
- A fun, positive tone
- 2-3 emojis to make it engaging (e.g., 🎞️, 🌱, 🚀, 🔄)
- No markdown

Example format:
"Your journey began with [theme] and has evolved into [new theme]! 🌱 You started with [early films] and now explore [later films] — what a transformation! 🎬"

Make it feel personal and cinematic. 🌟
"""
    model = genai.GenerativeModel(
            model_name="gemini-2.5-flash-lite",
            system_instruction=prompt
        )
    response = model.generate_content(prompt)
    return response.text.strip()