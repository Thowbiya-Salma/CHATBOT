# ============================================================
# DR. URCW AI - ADVANCED NLP ENGINE
# ============================================================

import random
import re
from typing import List
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from rapidfuzz import fuzz
from sqlalchemy.orm import Session
from backend.models import KnowledgeBase, UnansweredQuestion, IntentStat

# ============================================================
# CONFIGURATION
# ============================================================

HIGH_CONFIDENCE = 0.3
MEDIUM_CONFIDENCE = 0.2
FUZZY_THRESHOLD = 60


# ============================================================
# TEXT UTILITIES
# ============================================================

def clean_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", "", text)
    return text.strip()


def intro() -> str:
    return random.choice([
        "Sure 😊 Here's what I found:",
        "Great question! Let me explain:",
        "I'd be happy to help!",
        "Here’s some useful information:",
        "Let’s take a look 👇"
    ])


def generate_title(message: str) -> str:
    words = message.strip().split()
    return " ".join(words[:6]) if words else "New Chat"


# ============================================================
# EXPANDED STUDENT-CENTRIC STATIC INTENTS
# ============================================================

STATIC_INTENTS = [

    # College Info
    {
        "name": "about_college",
        "patterns": [
            "about urcw", "college history", "college background",
            "naac grade", "college ranking", "accreditation details"
        ],
        "response": """
Dr. Umayal Ramanathan College for Women (Dr.URCW) was established in 2006.
It is affiliated with Alagappa University and holds NAAC 'A' Grade accreditation.
More details: https://umayalwomenscollege.co.in/about/about-urcw/
"""
    },

    # UG Courses
    {
        "name": "ug_courses",
        "patterns": [
            "undergraduate courses", "ug programs", "bsc courses",
            "bcom courses", "ba courses", "courses after 12th"
        ],
        "response": """
UG Programs:
• B.A English
• B.Com
• B.Sc Mathematics
• B.Sc Computer Science
More info: https://umayalwomenscollege.co.in/admission/ug-courses/
"""
    },

    # PG Courses
    {
        "name": "pg_courses",
        "patterns": [
            "pg programs", "msc courses", "ma courses", "masters degree"
        ],
        "response": """
PG Programs:
• M.Sc Mathematics
• M.Sc Computer Science
• M.A English
More info: https://umayalwomenscollege.co.in/admission/pg-courses/
"""
    },

    # Fees
    {
        "name": "fees_structure",
        "patterns": [
            "fees structure", "tuition fees", "semester fees", "course fees"
        ],
        "response": """
Fee structure varies by department.
Students can contact the office or visit the official website for updated details.
"""
    },

    # Hostel & Transport
    {
        "name": "hostel_transport",
        "patterns": [
            "hostel facility", "bus facility", "transport", "accommodation"
        ],
        "response": """
Hostel facilities are available with required amenities.
Transport services depend on routes and availability.
Please contact administration for details.
"""
    },

    # Scholarships
    {
        "name": "scholarship",
        "patterns": [
            "scholarship", "fee concession", "financial assistance"
        ],
        "response": """
Government and institutional scholarships are available for eligible students.
Contact the office for application guidance.
"""
    },

    # Admission
    {
        "name": "admission",
        "patterns": [
            "how to apply", "admission process", "application form",
            "cutoff marks", "documents required"
        ],
        "response": """
Admissions are merit-based.
Students must submit application forms with required documents.
More info: https://umayalwomenscollege.co.in/admission/admission-procedure/
"""
    },

    # Placement
    {
        "name": "placement",
        "patterns": [
            "placement", "job opportunities", "internship",
            "campus recruitment"
        ],
        "response": """
The Placement Cell provides:
• Campus recruitment drives
• Internship opportunities
• Resume workshops
More info: https://umayalwomenscollege.co.in/placement/
"""
    },

    # Exams
    {
        "name": "exam_results",
        "patterns": [
            "exam schedule", "semester exam", "result date",
            "internal marks", "arrear exam"
        ],
        "response": """
Exam schedules and results are announced as per university norms.
Students should check official notices for updates.
"""
    },

    # Library & Labs
    {
        "name": "library_lab",
        "patterns": [
            "library timing", "lab facility", "computer lab",
            "science lab"
        ],
        "response": """
The college provides well-equipped labs and library resources
to support academic excellence.
"""
    },

    # Certificates
    {
        "name": "certificates",
        "patterns": [
            "bonafide certificate", "transfer certificate",
            "conduct certificate", "id card"
        ],
        "response": """
Students can apply for certificates through the administrative office.
Processing time may vary.
"""
    },

    # Clubs
    {
        "name": "clubs",
        "patterns": [
            "clubs", "extracurricular activities", "nss",
            "eco club", "cultural activities"
        ],
        "response": """
Various clubs including NSS, Eco Club, and Skill Development Cell
help students grow beyond academics.
"""
    },

    # Grievance
    {
        "name": "grievance",
        "patterns": [
            "complaint", "grievance", "anti ragging",
            "harassment issue"
        ],
        "response": """
The college has grievance redressal mechanisms including
Anti-Ragging and Internal Complaints Committees.
"""
    },

    # Alumni
    {
        "name": "alumni",
        "patterns": [
            "alumni", "former students", "alumni registration"
        ],
        "response": """
Alumni can register through the official portal:
https://www.alagappaalumni.com/user/signup.dz
"""
    }
]


# ============================================================
# SEMANTIC MATCH FUNCTION
# ============================================================

def semantic_match(query: str, documents: List[str]):
    corpus = documents + [query]
    vectorizer = TfidfVectorizer()
    vectors = vectorizer.fit_transform(corpus)

    similarity = cosine_similarity(
        vectors[-1], vectors[:-1]
    ).flatten()

    best_score = max(similarity)
    best_index = similarity.argmax()

    return best_score, best_index


# ============================================================
# KNOWLEDGE BASE MATCH
# ============================================================

def match_knowledge_base(message: str, db: Session):
    entries = db.query(KnowledgeBase).all()
    if not entries:
        return None, 0

    keywords = [e.keyword for e in entries]
    score, index = semantic_match(message, keywords)

    if score >= HIGH_CONFIDENCE:
        entry = entries[index]
        return f"<b>{intro()}</b><br><br>{entry.answer}", score

    return None, score


# ============================================================
# STATIC INTENT MATCH
# ============================================================

def match_static_intent(message: str, db: Session):
    documents = []
    intent_map = []

    for intent in STATIC_INTENTS:
        for pattern in intent["patterns"]:
            documents.append(pattern)
            intent_map.append(intent)

    if not documents:
        return None, 0

    score, index = semantic_match(message, documents)

    if score >= HIGH_CONFIDENCE:
        intent = intent_map[index]
        return f"<b>{intro()}</b><br><br>{intent['response']}", score

    return None, score


# ============================================================
# FUZZY BACKUP
# ============================================================

def fuzzy_fallback(message: str):
    for intent in STATIC_INTENTS:
        for pattern in intent["patterns"]:
            if fuzz.partial_ratio(message, pattern) >= FUZZY_THRESHOLD:
                return f"<b>{intro()}</b><br><br>{intent['response']}"
    return None


# ============================================================
# CLARIFICATION PROMPT
# ============================================================

def clarification_prompt():
    return (
        "<b>I’m not fully sure what you mean.</b><br><br>"
        "Are you asking about admissions, courses, placement, "
        "fees, hostel, or exams?"
    )


# ============================================================
# MAIN REPLY ENGINE
# ============================================================

def generate_reply(history, db: Session, user_id: int):

    user_message = clean_text(history[-1].message)

    # Context awareness (last 3 messages)
    if len(history) > 1:
        context = " ".join([
            clean_text(msg.message) for msg in history[-3:]
        ])
    else:
        context = user_message

    # 1. Knowledge Base
    kb_response, kb_score = match_knowledge_base(context, db)
    if kb_response:
        return kb_response

    # 2. Static Intent
    static_response, static_score = match_static_intent(context, db)
    if static_response:
        return static_response

    # 3. Medium Confidence Clarification
    if kb_score >= MEDIUM_CONFIDENCE or static_score >= MEDIUM_CONFIDENCE:
        return clarification_prompt()

    # 4. Fuzzy Fallback
    fuzzy = fuzzy_fallback(context)
    if fuzzy:
        return fuzzy

    # 5. Log Unanswered
    db.add(UnansweredQuestion(
        user_id=user_id,
        message_id=history[-1].id,
        question=history[-1].message
    ))
    db.commit()

    return (
        "<b>I’m still learning 🤖</b><br><br>"
        "Your question has been forwarded to the admin. "
        "You will be notified once it is answered."
    )