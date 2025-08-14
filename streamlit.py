
import streamlit as st
import pandas as pd
import google.generativeai as genai
from ai_gen import generate_ai_explanation,get_personality,get_taste_evolution
from database import register_user, authenticate_user, save_rating, get_user_ratings, get_rating_count
from recommendation import get_general_recommendations, get_content_based_recommendations, get_ncf_recommendations

def show_movie_grid(movies_df, user_id,tab_name,ai_mode):
    """Display movies in a grid with rating options"""
    user_ratings = {}
    if user_id:
        user_ratings_df = get_user_ratings(user_id)
        user_ratings = dict(zip(user_ratings_df['movie_id'], user_ratings_df['rating']))
    movies = pd.read_csv(r'C:\Users\User\OneDrive\Desktop\Recommendation\data\curated_data (1).csv')   
    liked_movies = movies[movies['movie_id'].isin(user_ratings.keys())]
    user_profile = {
        'liked_directors': set(liked_movies['director'].dropna()),
        'liked_actors': set(a for actors in liked_movies['top_actors'].dropna() for a in actors.split(', ')),
        'liked_genres': set(g for genres in liked_movies['genres'].dropna() for g in genres.split(', ')),
    }
    cols = st.columns(4)
    for idx, (_, row) in enumerate(movies_df.iterrows()):
        with cols[idx % 4]:
            if pd.notna(row['poster_path']):
                poster_url = f"https://image.tmdb.org/t/p/w300{row['poster_path']}"
                st.image(poster_url, width=150)
            else:
                st.image("https://via.placeholder.com/150x225?text=No+Poster", width=150)
            
            st.markdown(f"**{row['title']}**")
            st.markdown(f"⭐ {row['vote_average']}/10")

            if ai_mode == True and tab_name=='personal' :
                with st.expander("🎬 Why We Think You’ll Love This", expanded=False):
                    try:
                        explanation = generate_ai_explanation(user_profile, row, st.session_state.gemini_api_key)
                        st.write(explanation)
                    except Exception as e:
                        st.write("Could not generate explanation. Please check your API key.")
            

            movie_id = row['movie_id'] 
            current_rating = user_ratings.get(movie_id, 0)
            rating = st.selectbox(
                "Rate this movie", 
                options=[0, 1, 2, 3, 4, 5], 
                index=current_rating,
                key=f"rating_{tab_name}_{movie_id}_{idx}", # Ensure unique key
                label_visibility="collapsed"
            )
            
            if rating != current_rating and rating > 3:
                save_rating(user_id, movie_id, rating)
                st.success("Saved!")
                st.rerun()
            
            st.markdown("---")

if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'username' not in st.session_state:
    st.session_state.username = None

st.set_page_config(page_title="🎬 MovieReel AI", layout="wide")

col1, col2 = st.columns([4, 1])
with col1:
    st.title("🎬 MovieReel AI")
    st.subheader("Your AI-powered cinematic companion")

with col2:
    if st.session_state.user_id:
        st.write(f"👋 Welcome, **{st.session_state.username}**")
        if st.button("Logout"):
            st.session_state.user_id = None
            st.session_state.username = None
            st.rerun()
    else:
        st.write("👤 Not logged in")

if not st.session_state.user_id:
    with st.expander("🔐 Login or Register", expanded=True):
        choice = st.radio("Choose action", ["Login", "Register"])
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        if st.button("Submit"):
            if choice == "Register":
                if register_user(username, password):
                    st.success("✅ Registered successfully! Please login.")
                else:
                    st.error("❌ Username already exists")
            else:
                user_id = authenticate_user(username, password)
                if user_id:
                    st.session_state.user_id = user_id
                    st.session_state.username = username
                    st.rerun()
                else:
                    st.error("❌ Invalid credentials")
    
    st.info("Please log in or register to see movie recommendations.")
    st.stop()


user_id = st.session_state.user_id
rating_count = get_rating_count(user_id)
user_ratings_df = get_user_ratings(user_id)

st.progress(min(rating_count / 15, 1.0))
if rating_count < 10:
    st.info(f"⭐ Rate {10 - rating_count} more movies to unlock **Personalized Recommendations**")
elif rating_count < 20:
    st.success(f"🎉 Personalized Recommendations unlocked! Rate {20 - rating_count} more for deep learning mode.")
else:
    st.success("🔥 You're in **Deep Learning Mode** — powered by NCF!")

tab1, tab2, tab3,tab4 = st.tabs(["General Recommendations", "Personalized Recommendations","NCF Recommenadation","Know Your Style"])

with tab1:
    st.subheader("🔮 Popular Films for Everyone")
    with st.spinner("Finding the best recent films..."):
        recs = get_general_recommendations()
    show_movie_grid(recs, user_id,'general',False)

with tab2:
    if rating_count < 10:
        st.info("🔒 Unlock this tab by rating 10 movies")
    else:
        st.subheader("🎯 Content-Based Recommendations")
        st.write("Based on directors, genres, and actors you've liked")
        
        with st.expander("🧠 AI-Powered Insights (Optional)", expanded=False):
            st.write("Unlock personalized AI explanations for each recommendation.")
            
            if 'gemini_api_key' in st.session_state:
                pass
            else:
                api_key = st.text_input("Enter your Google Gemini API Key", type="password")
                if st.button("💾 Save API Key"):
                    if api_key:
                        st.session_state.gemini_api_key = api_key
                        st.success("✅ API Key saved!")
                        st.rerun()
                    else:
                        st.warning("Please enter a valid API key")
        
        ai_mode = False
        if 'gemini_api_key' in st.session_state:
            if st.button("🎬 Generate AI Explanations"):
                ai_mode = True
        else:
            if st.button("🎬 Generate AI Explanations"):
                st.warning("Please save your API key first")

        with st.spinner("Building recommendations tailored to your cinematic taste..."):
            recs = get_content_based_recommendations(user_ratings_df)
        
        if ai_mode:
            show_movie_grid(recs, user_id, 'personal', ai_mode=True)
        else:
            show_movie_grid(recs, user_id, 'personal', ai_mode=False)


with tab3:
    if rating_count < 20:
        st.info("🔒 Unlock this tab by rating 20 movies")
    else:
        st.subheader("🧠 Deep Learning Recommendations")
        st.write("People with tastes like yours are loving these")
        with st.spinner("Curating your cinematic journey..."):
            recs = get_ncf_recommendations(user_ratings_df)
            show_movie_grid(recs, user_id,'get_ncf_recommedation',False)

with tab4:
    if rating_count < 10:
        st.info("🔒 Unlock this tab by rating 10 movies")
    else:
        if st.button('DO THE MAGIC'):

            st.subheader(" 🎬 Your Cinematic DNA")
            with st.spinner("Developing Your Profile"):
                st.write(get_personality(
                    user_ratings_df
                ))
            with st.spinner("Mapping Your Taste"):
                st.subheader("\n\n ⏳ Your Taste Evolution")
                st.write(get_taste_evolution(
                    user_ratings_df
                ))


