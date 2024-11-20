import pickle
import streamlit as st
import requests

# Set up the background image CSS and text color CSS
page_bg_img = '''
<style>
.stApp {
    background-image: url("https://images.pexels.com/photos/7234246/pexels-photo-7234246.jpeg?auto=compress&cs=tinysrgb&w=800");  /* Change to the path of your background image */
    background-size: cover;
    background-attachment: fixed;
    background-position: center;
    color: #FFFFFF;
}

/* Style the button for hover effect */
.stButton>button {
    color: #3891a6;
    font-weight: bold;
    border-radius: 5px;
    padding: 10px 20px;
    transition: background-color 0.1s ease;
}

.stButton>button:hover {
    background-color: #4C5B5C;
}

div.stSelectbox > label {
    color: white;
}

/* Set the color of the "Recommended Movies" section to white */
.stMarkdown h3 {
    color: white;
}
</style>
'''

# Apply the background image CSS to the Streamlit app
st.markdown(page_bg_img, unsafe_allow_html=True)


# Function to fetch poster and overview from TMDB API
def fetch_movie_details(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"
    data = requests.get(url).json()
    poster_path = data.get('poster_path', "")
    overview = data.get('overview', "No overview available.")
    full_path = f"https://image.tmdb.org/t/p/w500/{poster_path}"
    return full_path, overview


# Function to recommend movies based on selected movie
def recommend(movie):
    # Get the index of the movie
    index = movies[movies['title'] == movie].index[0]

    # Get similarity scores and sort them
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])

    recommended_movie_names = []
    recommended_movie_posters = []
    recommended_movie_overviews = []
    recommended_movie_links = []

    # Fetch top 5 recommendations
    for i in distances[1:6]:
        movie_id = movies.iloc[i[0]].movie_id  # Access movie_id from the DataFrame
        poster, overview = fetch_movie_details(movie_id)
        recommended_movie_posters.append(poster)
        recommended_movie_names.append(movies.iloc[i[0]].title)
        recommended_movie_overviews.append(overview)
        recommended_movie_links.append(f"https://www.themoviedb.org/movie/{movie_id}")  # Link to TMDB

    return recommended_movie_names, recommended_movie_posters, recommended_movie_overviews, recommended_movie_links


# Load the movie DataFrame and similarity matrix
movies = pickle.load(open("./movies.pkl", "rb"))
similarity = pickle.load(open("./similarity.pkl", "rb"))
credits = pickle.load(open("./credits.pkl",
                           "rb"))  # Assuming you have a 'credits.pkl' file

# Creating movie_id to vote_average mapping
movie_id_to_vote_average = dict(zip(credits["movie_id"], credits["vote_average"]))

# Streamlit interface
st.markdown('<h1 style="color: white;">🎬 Popcorn Picks</h1>', unsafe_allow_html=True)
st.markdown('<h2 style="color: white;">Find Your Next Favorite Movie!</h2>', unsafe_allow_html=True)

# Dropdown menu for movie selection
selected_movie = st.selectbox(
    "Type or select a movie from the dropdown",
    movies['title'].values
)

# Fetch vote_average for the selected movie
selected_movie_id = movies[movies['title'] == selected_movie].movie_id.values[0]
selected_movie_vote = movie_id_to_vote_average.get(selected_movie_id, "N/A")

# Display the vote average for the selected movie
st.write(f"**{selected_movie}**")
st.markdown(f'<p style="color: yellow; font-size: 20px;">Recommendation Scale : {selected_movie_vote}</p>', unsafe_allow_html=True)


# Button to show recommendations
if st.button('Suggest movies'):
    recommended_movie_names, recommended_movie_posters, recommended_movie_overviews, recommended_movie_links = recommend(
        selected_movie)

    # Show recommendations in a row of columns
    st.markdown('<h3 style="color: white;">Recommended Movies:</h3>', unsafe_allow_html=True)
    for i in range(5):
        with st.container():
            col1, col2 = st.columns([1, 3])
            with col1:
                st.image(recommended_movie_posters[i], width=120)
            with col2:
                st.write(f"**{recommended_movie_names[i]}**")
                st.write(f"_Overview:_ {recommended_movie_overviews[i]}")
                # Add a clickable link to TMDB
                st.markdown(f"[Watch now ➡️]({recommended_movie_links[i]})", unsafe_allow_html=True)

        st.divider()
