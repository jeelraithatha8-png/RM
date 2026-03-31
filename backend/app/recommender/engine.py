import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from app.models.user import Preference

def get_ml_score(u1_pref: Preference, u2_pref: Preference) -> float:
    # Extremely simplified one-hot-like encoding for MVP 
    # In a real scenario, use scikit-learn OneHotEncoder over the entire dataset
    
    def encode(p: Preference):
        return [
            1 if p.sleep_pref == "Morning" else 0,
            1 if p.sleep_pref == "Night" else 0,
            1 if p.guest_policy == "No Guests" else 0,
            1 if p.guest_policy == "Occasional" else 0,
            1 if p.noise_tolerance == "Quiet" else 0,
            1 if p.noise_tolerance == "Noisy" else 0,
            1 if p.personality == "Introvert" else 0,
            1 if p.personality == "Extrovert" else 0,
            1 if p.living_habit == "Organized" else 0,
            1 if p.living_habit == "Flexible" else 0
        ]
        
    vec1 = np.array(encode(u1_pref)).reshape(1, -1)
    vec2 = np.array(encode(u2_pref)).reshape(1, -1)
    
    # Handle zero vectors to avoid division by zero warning
    if not np.any(vec1) or not np.any(vec2):
        return 0.0
        
    sim = cosine_similarity(vec1, vec2)[0][0]
    return float(sim)


def generate_explanation(u1: Preference, u2: Preference) -> str:
    shared = []
    if u1.sleep_pref == u2.sleep_pref:
        shared.append(f"sleep schedule ({u1.sleep_pref})")
    if u1.noise_tolerance == u2.noise_tolerance:
        shared.append(f"noise preference ({u1.noise_tolerance})")
    if u1.guest_policy == u2.guest_policy:
        shared.append("guest policies")
        
    if len(shared) > 0:
        return f"Matched perfectly on: {', '.join(shared)}."
    return "Partial lifestyle match."


def calculate_compatibility(current_pref: Preference, candidate_pref: Preference):
    if current_pref is None or candidate_pref is None:
        return 0.0, "Missing preferences"
        
    # Rule-Based Score
    rule_score = 0
    max_rule_score = 15 + 6 + 1 # 3x5 + 2x3 + 1x1 = 22
    
    # High Weight (5 points)
    if current_pref.sleep_pref == candidate_pref.sleep_pref: rule_score += 5
    if current_pref.guest_policy == candidate_pref.guest_policy: rule_score += 5
    if current_pref.noise_tolerance == candidate_pref.noise_tolerance: rule_score += 5
    
    # Medium Weight (3 points)
    if current_pref.personality == candidate_pref.personality: rule_score += 3
    if current_pref.living_habit == candidate_pref.living_habit: rule_score += 3
    
    # Low Weight (1 point)
    if current_pref.sleep_sense == candidate_pref.sleep_sense: rule_score += 1
        
    normalized_rule_score = rule_score / max_rule_score
    
    # ML Score (0.0 to 1.0)
    ml_score = get_ml_score(current_pref, candidate_pref)
    
    # Combine (50% rule, 50% ML) mapped to 1-10 scale
    final_score = (normalized_rule_score * 0.5 + ml_score * 0.5) * 10
    final_score = round(final_score, 1)
    
    explanation = generate_explanation(current_pref, candidate_pref)
    return final_score, explanation
