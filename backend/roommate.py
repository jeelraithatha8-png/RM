import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.metrics.pairwise import cosine_similarity
import joblib

# 1. Load your CSV Data
df = pd.read_csv('Girls_pg_hostel_CSV_data-1.csv')

# 2. Define features matching your Frontend UI
categorical_features = [
    'work_shift', 'profession', 'personality', 'cleanliness', 
    'sleep_type', 'noise_preference', 'room_type_preference', 
    'pets', 'smoking_drinking', 'dietary_restrictions'
]
numerical_features = ['social_energy_rating']

# 3. Build Preprocessing Pipeline
preprocessor = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), numerical_features),
        ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), categorical_features)
    ])

# 4. Train Model (Fit and Transform)
feature_vectors = preprocessor.fit_transform(df)

# 5. Save Model Components for Backend Usage
joblib.dump(preprocessor, 'preprocessor.pkl')
joblib.dump(feature_vectors, 'feature_vectors.pkl')
joblib.dump(df, 'dataset.pkl')

# --- INFERENCE FUNCTION FOR YOUR APP ---

def get_top_roommate_matches(user_input_dict, top_n=5):
    """
    Finds matches based on frontend questionnaire data.
    """
    prep = joblib.load('preprocessor.pkl')
    vectors = joblib.load('feature_vectors.pkl')
    data = joblib.load('dataset.pkl')
    
    # Convert input to dataframe
    user_df = pd.DataFrame([user_input_dict])
    
    # Generate feature vector for new user
    user_vector = prep.transform(user_df)
    
    # Calculate similarity across the entire dataset
    scores = cosine_similarity(user_vector, vectors).flatten()
    
    # Get top N matches
    best_indices = scores.argsort()[-top_n:][::-1]
    results = data.iloc[best_indices].copy()
    results['compatibility_score'] = scores[best_indices] * 100
    
    return results[['user_name', 'profession', 'compatibility_score']]

# Example Usage with Frontend Data:
new_user = {
    'work_shift': 'Morning',
    'profession': 'Engineer',
    'personality': 'Introvert',
    'cleanliness': 'Organised',
    'sleep_type': 'Light Sleeper',
    'noise_preference': 'Quiet',
    'social_energy_rating': 2, # Proxy for 'No Guests'
    'room_type_preference': 'Private Room',
    'pets': 'No Pets',
    'smoking_drinking': 'Non-Smoker/Non-Drinker',
    'dietary_restrictions': 'Vegetarian'
}

print(get_top_roommate_matches(new_user))