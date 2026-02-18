import re
import random
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from rapidfuzz import fuzz

from app.chatbot_data import INTENTS
from app.database import SessionLocal
from app.models import UnansweredQuestion, IntentStat


# =====================================
# TEXT CLEANING
# =====================================

def clean_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", "", text)
    return text


# =====================================
# BUILD INTENT PATTERNS
# =====================================

patterns = []
intent_map = []

for intent in INTENTS:
    for keyword in intent["keywords"]:
        patterns.append(clean_text(keyword))
        intent_map.append(intent)

vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(patterns)


# =====================================
# TRACK INTENT USAGE (ORM SAFE)
# =====================================

def increment_intent_usage(intent_name: str):
    db = SessionLocal()

    stat = db.query(IntentStat).filter(IntentStat.name == intent_name).first()

    if stat:
        stat.count += 1
    else:
        stat = IntentStat(name=intent_name, count=1)
        db.add(stat)

    db.commit()
    db.close()


# =====================================
# STORE UNANSWERED QUESTIONS (ORM SAFE)
# =====================================

def store_unanswered(question: str):
    db = SessionLocal()

    entry = UnansweredQuestion(question=question)
    db.add(entry)

    db.commit()
    db.close()


# =====================================
# MATCH INTENT
# =====================================

def match_intent(user_message: str):
    cleaned = clean_text(user_message)

    user_vec = vectorizer.transform([cleaned])
    similarity_scores = cosine_similarity(user_vec, X)

    best_index = similarity_scores.argmax()
    best_score = similarity_scores[0][best_index]

    fuzzy_scores = [
        fuzz.partial_ratio(cleaned, pattern) / 100
        for pattern in patterns
    ]

    best_fuzzy_index = fuzzy_scores.index(max(fuzzy_scores))
    best_fuzzy_score = fuzzy_scores[best_fuzzy_index]

    final_score = max(best_score, best_fuzzy_score)

    if final_score > 0.45:
        if best_score >= best_fuzzy_score:
            return intent_map[best_index]
        else:
            return intent_map[best_fuzzy_index]

    return None


# =====================================
# CONVERSATIONAL WRAPPER
# =====================================

def conversational_wrap(response_text: str) -> str:
    intros = [
        "Sure 😊 Here's what I found:",
        "Great question! Let me explain:",
        "I'd be happy to help!",
        "Here are the details:",
        "Let me share the information:"
    ]

    intro = random.choice(intros)
    return f"<b>{intro}</b><br><br>{response_text}"


# =====================================
# GENERATE REPLY
# =====================================

def generate_reply(history):

    user_message = history[-1].message

    matched_intent = match_intent(user_message)

    if matched_intent:
        intent_name = matched_intent["name"]

        # Track popularity
        increment_intent_usage(intent_name)

        response_content = matched_intent["response"]

        if callable(response_content):
            response_content = response_content()

        return conversational_wrap(response_content)

    # Store unanswered if no match
    store_unanswered(user_message)

    return """
    <b>I’m not completely sure about that yet.</b><br><br>
    I can help you with information about:<br>
    • Courses & Programs<br>
    • Hostel Facilities<br>
    • Placements<br>
    • College Details<br>
    • Contact Information<br><br>
    Please try asking something related to the college.
    """


# =====================================
# GENERATE TITLE
# =====================================

def generate_title(first_message: str):
    words = first_message.strip().split()
    return " ".join(words[:4]) if words else "New Chat"
