"""
Hybrid Recommendation Engine for Nest & Found.

Combines Rule-Based weighted scoring with ML Cosine Similarity
to produce a compatibility score on a 1-10 scale.

Architecture:
  - Rule-Based (50%): Strict weighted matching on non-negotiable preferences
  - ML Cosine (50%): One-hot encoded preference vectors compared via cosine similarity
  - Final: Combined score mapped to 0-10 scale with tier labeling
"""
import numpy as np
import httpx
from app.models.user import Preference, User
from app.config import settings


# Compatibility tier thresholds
TIER_EXCELLENT = 8.0
TIER_GOOD = 6.0
TIER_FAIR = 4.0


def get_ml_score(u1_pref: Preference, u2_pref: Preference) -> float:
    """
    Compute cosine similarity between two users' one-hot encoded preference vectors.
    
    Encodes preferences across 10 binary features covering sleep, guest policy,
    noise tolerance, personality, and living habits.
    
    Returns:
        Float between 0.0 (no similarity) and 1.0 (identical preferences).
    """
    def encode(p: Preference) -> np.ndarray:
        return np.array([
            1 if p.sleep_pref == "Morning" else 0,
            1 if p.sleep_pref == "Night" else 0,
            1 if p.sleep_pref == "Evening" else 0,
            1 if p.guest_policy == "No Guests" else 0,
            1 if p.guest_policy == "Occasional" else 0,
            1 if p.guest_policy == "Male Allowed" else 0,
            1 if p.noise_tolerance == "Quiet" else 0,
            1 if p.noise_tolerance == "Noisy" else 0,
            1 if p.personality == "Introvert" else 0,
            1 if p.personality == "Extrovert" else 0,
            1 if p.living_habit == "Organized" else 0,
            1 if p.living_habit == "Flexible" else 0,
            1 if p.sleep_sense == "Light Sleeper" else 0,
            1 if p.sleep_sense == "Heavy Sleeper" else 0,
            1 if p.food_pref == "Vegetarian" else 0,
            1 if p.food_pref == "Non-Veg" else 0,
            1 if p.pet_friendly == "Pet-Lover" else 0,
            1 if p.pet_friendly == "No Pets" else 0,
            1 if p.smoking_habit == "Non-Smoker" else 0,
            1 if p.smoking_habit == "Smoker" else 0,
            1 if p.ac_usage == "Always On" else 0,
            1 if p.ac_usage == "Eco-friendly" else 0,
        ])
        
    vec1 = encode(u1_pref)
    vec2 = encode(u2_pref)
    
    # Handle zero vectors to avoid division by zero
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    
    if norm1 == 0 or norm2 == 0:
        return 0.0
        
    sim = np.dot(vec1, vec2) / (norm1 * norm2)
    return float(sim)


def get_compatibility_tier(score: float) -> str:
    """Return a human-readable tier label for the given score."""
    if score >= TIER_EXCELLENT:
        return "Excellent Match 🌟"
    elif score >= TIER_GOOD:
        return "Good Match ✨"
    elif score >= TIER_FAIR:
        return "Fair Match 👍"
    else:
        return "Low Match"


def generate_basic_explanation(u1: Preference, u2: Preference, score: float) -> str:
    """
    Generate a human-readable explanation of why two users are compatible.
    Lists shared preferences and includes the compatibility tier.
    """
    shared = []
    differences = []
    
    if u1.sleep_pref == u2.sleep_pref:
        shared.append(f"🌙 Same sleep schedule ({u1.sleep_pref})")
    else:
        differences.append("sleep schedule")
        
    if u1.noise_tolerance == u2.noise_tolerance:
        shared.append(f"🔇 Same noise preference ({u1.noise_tolerance})")
    else:
        differences.append("noise tolerance")
        
    if u1.guest_policy == u2.guest_policy:
        shared.append(f"👥 Same guest policy ({u1.guest_policy})")
    else:
        differences.append("guest policy")

    if u1.personality == u2.personality:
        shared.append(f"🧠 Same personality ({u1.personality})")
        
    if u1.living_habit == u2.living_habit:
        shared.append(f"🏠 Same living style ({u1.living_habit})")

    if u1.sleep_sense == u2.sleep_sense:
        shared.append(f"😴 Same sleep sensitivity ({u1.sleep_sense})")

    tier = get_compatibility_tier(score)
    
    if shared:
        match_text = " | ".join(shared)
        return f"{tier} — {match_text}"
    
    return f"{tier} — Complementary lifestyle match."

def generate_explanation(u1: Preference, u2: Preference, score: float) -> str:
    """Generate dynamic explanation using Groq AI if key is set, else fallback to basic."""
    basic_exp = generate_basic_explanation(u1, u2, score)
    if not settings.GROQ_API_KEY:
        return basic_exp
        
    try:
        prompt = (
            f"You are a dating/roommate app AI. User 1: {u1.sleep_pref} sleeper, {u1.noise_tolerance} noise, {u1.living_habit} living, {u1.food_pref} food, {u1.smoking_habit} smoking, {u1.pet_friendly} pet attitude. "
            f"User 2: {u2.sleep_pref} sleeper, {u2.noise_tolerance} noise, {u2.living_habit} living, {u2.food_pref} food, {u2.smoking_habit} smoking, {u2.pet_friendly} pet attitude. "
            f"Compatibility score: {score}/10. "
            f"Write a short, punchy 1-sentence Tinder-style explanation of why they are a match. Focus on their shared lifestyle or complementary habits. Don't use quotes."
        )
        response = httpx.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {settings.GROQ_API_KEY}"},
            json={
                "model": "llama3-8b-8192",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 60,
                "temperature": 0.7
            },
            timeout=3.0
        )
        if response.status_code == 200:
            data = response.json()
            return data["choices"][0]["message"]["content"].strip()
    except Exception:
        pass
        
    return basic_exp


def calculate_compatibility(current_user: User, candidate_user: User):
    """
    Calculate the final compatibility score between two users.
    
    Uses a 50/50 weighted combination of:
    - Rule-Based scoring (weighted exact matches and age proximity)
    - ML Cosine Similarity (one-hot encoded preference vectors)
    """
    current_pref = current_user.preference
    candidate_pref = candidate_user.preference

    if current_pref is None or candidate_pref is None:
        return 0.0, "Missing preferences"
        
    # Rule-Based Score
    rule_score = 0
    max_rule_score = 41 # (5*5=25) + (4*3=12) + (1*1=1) + Age(3) = 41
    
    # High Weight (5 points each) — non-negotiables
    if current_pref.sleep_pref == candidate_pref.sleep_pref:
        rule_score += 5
    if current_pref.guest_policy == candidate_pref.guest_policy:
        rule_score += 5
    if current_pref.noise_tolerance == candidate_pref.noise_tolerance:
        rule_score += 5
    if current_pref.food_pref == candidate_pref.food_pref:
        rule_score += 5
    if current_pref.smoking_habit == candidate_pref.smoking_habit:
        rule_score += 5
    
    # Medium Weight (3 points each) — lifestyle
    if current_pref.personality == candidate_pref.personality:
        rule_score += 3
    if current_pref.living_habit == candidate_pref.living_habit:
        rule_score += 3
    if current_pref.pet_friendly == candidate_pref.pet_friendly:
        rule_score += 3
    if current_pref.ac_usage == candidate_pref.ac_usage:
        rule_score += 3
    
    # Low Weight (1 point) — minor
    if current_pref.sleep_sense == candidate_pref.sleep_sense:
        rule_score += 1
        
    # Age Proximity Weight (up to 3 points)
    if current_user.age is not None and candidate_user.age is not None:
        age_diff = abs(current_user.age - candidate_user.age)
        if age_diff <= 2:
            rule_score += 3
        elif age_diff <= 5:
            rule_score += 2
        elif age_diff <= 10:
            rule_score += 1
            
    normalized_rule_score = rule_score / max_rule_score
    
    # ML Score (0.0 to 1.0)
    ml_score = get_ml_score(current_pref, candidate_pref)
    
    # Combine: 50% rule-based, 50% ML — mapped to 1-10 scale
    final_score = (normalized_rule_score * 0.5 + ml_score * 0.5) * 10
    final_score = round(final_score, 1)
    
    explanation = generate_explanation(current_pref, candidate_pref, final_score)
    
    # Append age relevance to explanation if they are very close
    if current_user.age is not None and candidate_user.age is not None:
        if abs(current_user.age - candidate_user.age) <= 2:
            explanation += " (Similar Age)"
            
    return final_score, explanation
