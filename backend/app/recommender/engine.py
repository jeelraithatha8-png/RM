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
from sklearn.metrics.pairwise import cosine_similarity
from app.models.user import Preference


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
    def encode(p: Preference) -> list:
        return [
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
        ]
        
    vec1 = np.array(encode(u1_pref)).reshape(1, -1)
    vec2 = np.array(encode(u2_pref)).reshape(1, -1)
    
    # Handle zero vectors to avoid division by zero
    if not np.any(vec1) or not np.any(vec2):
        return 0.0
        
    sim = cosine_similarity(vec1, vec2)[0][0]
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


def generate_explanation(u1: Preference, u2: Preference, score: float) -> str:
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


def calculate_compatibility(current_pref: Preference, candidate_pref: Preference):
    """
    Calculate the final compatibility score between two users.
    
    Uses a 50/50 weighted combination of:
    - Rule-Based scoring (weighted exact matches on preference fields)
    - ML Cosine Similarity (one-hot encoded preference vectors)
    
    Args:
        current_pref: The logged-in user's preferences.
        candidate_pref: A candidate user's preferences.
    
    Returns:
        Tuple of (score: float, explanation: str) where score is 0.0-10.0
    """
    if current_pref is None or candidate_pref is None:
        return 0.0, "Missing preferences"
        
    # Rule-Based Score
    rule_score = 0
    max_rule_score = 22  # 3×5 + 2×3 + 1×1 = 22
    
    # High Weight (5 points each) — non-negotiables
    if current_pref.sleep_pref == candidate_pref.sleep_pref:
        rule_score += 5
    if current_pref.guest_policy == candidate_pref.guest_policy:
        rule_score += 5
    if current_pref.noise_tolerance == candidate_pref.noise_tolerance:
        rule_score += 5
    
    # Medium Weight (3 points each) — lifestyle
    if current_pref.personality == candidate_pref.personality:
        rule_score += 3
    if current_pref.living_habit == candidate_pref.living_habit:
        rule_score += 3
    
    # Low Weight (1 point) — minor
    if current_pref.sleep_sense == candidate_pref.sleep_sense:
        rule_score += 1
        
    normalized_rule_score = rule_score / max_rule_score
    
    # ML Score (0.0 to 1.0)
    ml_score = get_ml_score(current_pref, candidate_pref)
    
    # Combine: 50% rule-based, 50% ML — mapped to 1-10 scale
    final_score = (normalized_rule_score * 0.5 + ml_score * 0.5) * 10
    final_score = round(final_score, 1)
    
    explanation = generate_explanation(current_pref, candidate_pref, final_score)
    return final_score, explanation
