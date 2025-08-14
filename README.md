# 🎬 MovieReel AI: A Hybrid Movie Recommendation Engine

## 🌟 Overview
**MovieReel AI** is an advanced movie recommendation system built with **Streamlit**, **TensorFlow**, and the **Google Gemini API**. It provides highly personalized movie suggestions by combining **Content-Based Filtering** and **Neural Collaborative Filtering (NCF)**, delivering accurate, engaging, and explainable recommendations to users.  

---

## 🚀 Key Features

- **Hybrid Recommendation Engine**  
  - **Content-Based Filtering:** Recommends movies based on director, genre, and actor preferences.  
  - **Neural Collaborative Filtering (NCF):** Learns latent features from user-item interactions for personalized suggestions.  

- **AI-Powered Explanations**  
  - Integrates the **Google Gemini API** to generate human-like, personalized explanations for each recommendation.  

- **Cinematic Personality**  
  - Analyzes user preferences to assign a cinematic archetype (e.g., "Neo-Noir Dreamer," "Genre Hopper").  

- **Taste Evolution**  
  - Tracks user taste changes over time, showing their cinematic journey.  

- **User Authentication**  
  - Secure **login/register** system using **SQLite** for managing user ratings and preferences.  

- **Interactive UI**  
  - Clean, responsive design built with **Streamlit**, including rating functionality and AI explanations.  

---

## 🛠️ How It Works

### 1. Data Preparation
- **Movies Dataset:** Contains metadata such as titles, genres, directors, and actors.  
- **User Ratings:** Stored in a **SQLite** database to track user interactions and preferences.  

### 2. Recommendation Engine
- **Content-Based Filtering:**  
  - Filters movies using **director matches, genre overlaps, and actor similarities**.  
  - Enhances recommendations using **pre-trained movie embeddings from NCF**.  

- **Neural Collaborative Filtering (NCF):**  
  - Learns latent features from user-item interactions.  
  - Computes similarity scores between user embeddings and movie embeddings for personalized suggestions.  

### 3. AI-Powered Explanations
- Uses the **Google Gemini API** to generate human-like explanations.  
- API prompts include user preferences and movie metadata to provide engaging insights.  

### 4. Database Management
- **SQLite Database** stores user ratings and preferences.  
- Handles **CRUD operations** to ensure smooth user interaction.  

### 5. User Interface
- Built with **Streamlit** for an intuitive experience.  
- Displays movie posters, titles, ratings, and AI-generated explanations.  

---
  
- **API Integration:** Google Gemini API  

---
