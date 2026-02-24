import re
import random
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from rapidfuzz import fuzz
from sqlalchemy.orm import Session

from app.chatbot_data import INTENTS
from app.models import UnansweredQuestion, IntentStat


# =====================================
# TEXT CLEANING
# =====================================

def clean_text(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9\s]", "", text)
    return text


# =====================================
# GREETING DETECTION
# =====================================

GREETINGS = ["hi", "hello", "hey", "good morning", "good afternoon", "good evening"]

def is_greeting(text: str) -> bool:
    return text in GREETINGS


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
# MATCH INTENT
# =====================================

def match_intent(user_message: str):
    cleaned = clean_text(user_message)

    if len(cleaned.split()) <= 1:
        return None

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

    if final_score > 0.65:
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

def generate_reply(history, db: Session, student_id: int):

    user_message = history[-1].message
    cleaned = clean_text(user_message)

    # ---------------- GREETING ----------------
    if is_greeting(cleaned):
        return """
        <b>Hello! 😊</b><br><br>
        I'm your DR.URCW AI Assistant.<br><br>
        You can ask me about:<br>
        • Courses & Programs<br>
        • Admissions<br>
        • Placements<br>
        • College Details<br>
        • Clubs & Activities<br><br>
        How can I help you today?
        """

    # ---------------- CHECK ADMIN ANSWERS FIRST ----------------
    admin_answer = db.query(UnansweredQuestion).filter(
        UnansweredQuestion.question.ilike(f"%{user_message}%"),
        UnansweredQuestion.answered == True
    ).first()

    if admin_answer and admin_answer.admin_answer:
        return conversational_wrap(admin_answer.admin_answer)

    # ---------------- MATCH INTENT ----------------
    matched_intent = match_intent(user_message)

    if matched_intent:
        intent_name = matched_intent["name"]

        stat = db.query(IntentStat).filter(
            IntentStat.name == intent_name
        ).first()

        if stat:
            stat.count += 1
        else:
            stat = IntentStat(name=intent_name, count=1)
            db.add(stat)

        db.commit()

        response_content = matched_intent["response"]

        if callable(response_content):
            response_content = response_content()

        return conversational_wrap(response_content)

    # ---------------- STORE UNANSWERED ----------------
    existing = db.query(UnansweredQuestion).filter(
        UnansweredQuestion.question == user_message,
        UnansweredQuestion.student_id == student_id
    ).first()

    if not existing:
        unanswered = UnansweredQuestion(
            student_id=student_id,
            question=user_message,
            answered=False
        )
        db.add(unanswered)
        db.commit()

    return """
    <b>I’m not completely sure about that yet.</b><br><br>
    Your question has been forwarded to the admin team.<br><br>
    Please try asking something related to the college meanwhile.
    """


# =====================================
# GENERATE TITLE
# =====================================

def generate_title(first_message: str):
    words = first_message.strip().split()
    return " ".join(words[:4]) if words else "New Chat"
