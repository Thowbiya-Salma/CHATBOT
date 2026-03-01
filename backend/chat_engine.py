import random, re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from rapidfuzz import fuzz
from sqlalchemy.orm import Session
from backend.models import KnowledgeBase, UnansweredQuestion

def clean_text(t): 
    return re.sub(r"[^a-z0-9\s]","",t.lower()).strip()

def generate_title(m): 
    return " ".join(m.strip().split()[:6]) or "New Chat"

INTENTS = [
    {
        "patterns": [
            "hi",
            "hello",
            "hey",
            "morning",
            "evening",
            "namaste",
            "vanakkam",
            "hii",
            "helo"
        ],
        "response": "Hi there! 👋 Welcome to Dr. Umayal Ramanathan College for Women!<br><br>I'm so glad you're here. I can help you learn about our courses, admissions, fees, campus facilities, placements - basically everything you need to know about joining us!<br><br>What brings you here today? Are you looking to join us, or do you have specific questions? 😊"
    },
    {
        "patterns": [
            "about",
            "about college",
            "urcw",
            "naac",
            "university",
            "established",
            "history"
        ],
        "response": "Great question! Let me tell you about our college. 😊<br><br>Dr. Umayal Ramanathan College for Women started in 2006 right here in Karaikudi. We're affiliated with Alagappa University and we're really proud of our NAAC 'A' Grade with 3.22 CGPA! We're also UGC recognized.<br><br>What makes us special? We're all about empowering women through education. Our students have achieved over 300 university ranks - that's something we're incredibly proud of! 🏆<br><br>Want to know more about any specific aspect? Just ask!<br><br>📞 04565-227861 | 🌐 umayalwomenscollege.co.in"
    },
    {
        "patterns": [
            "ug",
            "undergraduate",
            "bachelor",
            "bsc",
            "bcom",
            "ba",
            "bba",
            "12th",
            "courses",
            "degree"
        ],
        "response": "Awesome! We have so many great UG programs to choose from. Let me break them down for you:<br><br>📚 <b>Arts:</b> B.A. English, B.A. Tamil<br>💼 <b>Commerce:</b> B.Com, B.Com (CA), BBA<br>🔬 <b>Science:</b> B.Sc. CS, IT, Maths, Physics, Biotech, Microbiology, Electronics<br><br>All programs are 3 years. You just need to have passed 12th from any recognized board.<br><br>Which field interests you? I can tell you more details about any specific course! 😊"
    },
    {
        "patterns": [
            "pg",
            "postgraduate",
            "masters",
            "msc",
            "ma",
            "mcom",
            "mphil",
            "graduation"
        ],
        "response": "Looking at PG programs? Excellent choice for advancing your career! Here's what we offer:<br><br>📖 M.A. English<br>🔢 M.Sc. Maths, CS, IT, Environmental Science<br>💻 M.Com (CA)<br>🎓 M.Phil in Commerce & CS<br><br>PG programs are 2 years, M.Phil is 1-2 years. You'll need a Bachelor's with 50% (55% for M.Phil).<br><br>These programs are perfect if you're thinking about research, higher studies, or specialized careers. Which one catches your eye?"
    },
    {
        "patterns": [
            "fees",
            "cost",
            "tuition",
            "price",
            "payment",
            "expensive",
            "affordable"
        ],
        "response": "Let's talk about fees - I know it's an important factor! 💰<br><br>Our fees are quite reasonable:<br>• UG: ₹54,000 - ₹1,02,000 per year<br>• PG: ₹50,000 - ₹60,000 per year<br><br>The exact amount depends on your course and category. We accept online payment, bank transfer, and DD.<br><br>Here's the good news - we have lots of scholarships available! So don't worry if fees seem high. Many students get financial support.<br><br>Want to know about scholarships? Or need exact fees for a specific course? Call us at 04565-227861!"
    },
    {
        "patterns": [
            "admission",
            "apply",
            "join",
            "enroll",
            "registration",
            "how to"
        ],
        "response": "Ready to join us? That's exciting! The admission process is pretty straightforward:<br><br>1️⃣ Get the application form (download online or collect from office)<br>2️⃣ Fill it with your details<br>3️⃣ Submit your documents (10th/12th marks, TC, photos, Aadhar)<br>4️⃣ We'll prepare merit list based on your marks<br>5️⃣ Pay fees and you're in! 🎉<br><br>It's merit-based, so your academic performance matters. Want to know if admissions are open now? Give us a call at 04565-227861!"
    },
    {
        "patterns": [
            "eligibility",
            "qualify",
            "cutoff",
            "marks",
            "percentage",
            "criteria"
        ],
        "response": "Let me help you understand the eligibility:<br><br>🎓 <b>For UG:</b> Pass 12th with required percentage (varies by course)<br>🎓 <b>For PG:</b> Bachelor's degree with 50%<br>🎓 <b>For M.Phil:</b> PG degree with 55%<br><br>Cutoff changes every year based on applications. If you're from reserved category (SC/ST/OBC), you get relaxation as per government rules.<br><br>Which course are you interested in? I can give you more specific details!"
    },
    {
        "patterns": [
            "scholarship",
            "financial",
            "aid",
            "concession",
            "free",
            "help with fees"
        ],
        "response": "This is great news! We have plenty of scholarship options: 🎓<br><br>🏆 <b>Government Scholarships:</b><br>SC/ST, OBC, Minority, First Graduate<br><br>💡 <b>Merit Scholarships:</b><br>Academic Excellence, Sports, Cultural<br><br>These are based on your family income, academic performance, and category. Apply through National Scholarship Portal and our Scholarship Cell will guide you.<br><br>Don't let money stop your dreams! Many of our students study with scholarship support. Want help applying?"
    },
    {
        "patterns": [
            "hostel",
            "accommodation",
            "staying",
            "rooms",
            "mess",
            "food"
        ],
        "response": "Our hostel is like a second home! 🏠 Let me tell you about it:<br><br>It's exclusively for women with 24/7 security and CCTV. You'll share rooms with 2-4 students - great way to make friends!<br><br>🍽️ <b>Food:</b> Nutritious veg meals three times daily. The mess food is actually good - students love it! Special dishes on festivals too.<br><br>⚡ <b>Facilities:</b> Wi-Fi, TV room, study room, laundry, water purifier<br><br>Many students prefer hostel life - you get to study together, make lifelong friends, and it's super convenient!<br><br>Contact the Hostel Warden for fees and room availability."
    },
    {
        "patterns": [
            "bus",
            "transport",
            "travel",
            "routes"
        ],
        "response": "We've got you covered for transport! 🚌<br><br>Our college buses run from various locations around Karaikudi. They're safe, comfortable, and driven by experienced drivers. Morning pickup, evening drop - perfectly timed with classes.<br><br>Fees depend on how far you're coming from. It's paid semester-wise.<br><br>Where are you from? Contact our Transport Office and they'll tell you if there's a bus route from your area!"
    },
    {
        "patterns": [
            "library",
            "books",
            "reading",
            "study"
        ],
        "response": "Book lovers, you'll love our library! 📚<br><br>We have 15,000+ books, journals, magazines, newspapers - basically everything you need for studies and research. Plus e-books, digital resources, and INFLIBNET access.<br><br>The reading room is spacious and quiet - perfect for focused studying. Internet facility is there too.<br><br>⏰ Open Mon-Fri 9 AM-5 PM, Sat 9 AM-1 PM<br><br>Whether you're preparing for exams or doing research, our library has got you covered!"
    },
    {
        "patterns": [
            "lab",
            "computer",
            "science",
            "practical",
            "equipment"
        ],
        "response": "Our labs are really well-equipped! 💻🔬<br><br><b>Computer Labs:</b> Latest systems, high-speed internet, all the software you need<br><b>Science Labs:</b> Physics, Chemistry, Biotech, Microbiology, Electronics - all with modern equipment<br><b>Smart Classrooms:</b> Projectors, digital learning<br><br>Everything is maintained well and you'll get plenty of hands-on practice. That's how you really learn, right?<br><br>Wi-Fi throughout campus keeps you connected!"
    },
    {
        "patterns": [
            "placement",
            "job",
            "recruitment",
            "career",
            "companies",
            "internship"
        ],
        "response": "Your career matters to us! Our Placement Cell works hard to get you great opportunities. 💼<br><br>We organize campus recruitment drives with IT companies, banks, corporates, and government organizations. Plus pre-placement training, soft skills, interview prep - everything to make you job-ready!<br><br>We also arrange internships and support entrepreneurship if you want to start your own venture.<br><br>Many of our students are placed in top companies. Your success is what makes us proud! Want to know more about specific companies that recruit here?"
    },
    {
        "patterns": [
            "exam",
            "test",
            "result",
            "marks",
            "semester",
            "internal"
        ],
        "response": "Let me explain how exams work here:<br><br>We follow Alagappa University's semester system. You'll have internal assessments throughout the semester (25 marks) and semester exams by the university (75 marks).<br><br>Results are published on the university portal and our notice board.<br><br>📅 Exam schedules are announced well in advance by the Examination Cell. You'll have enough time to prepare!<br><br>Any specific questions about exams?"
    },
    {
        "patterns": [
            "cs",
            "computer science",
            "bsc cs",
            "msc cs"
        ],
        "response": "Computer Science is one of our most popular programs! 💻<br><br><b>We offer:</b> B.Sc. CS (3 yrs), M.Sc. CS (2 yrs), M.Phil CS<br><br>You'll learn programming (C, C++, Java, Python), data structures, databases, web development, AI, machine learning - all the latest tech!<br><br><b>Career options:</b> Software developer, web developer, database admin, system analyst, IT consultant<br><br>Our computer labs are excellent and faculty are experienced. CS graduates are in high demand everywhere!<br><br>Interested in CS? It's a great choice!"
    },
    {
        "patterns": [
            "it",
            "information technology",
            "bsc it",
            "msc it"
        ],
        "response": "IT is perfect if you love technology! 💻<br><br><b>Programs:</b> B.Sc. IT (3 yrs), M.Sc. IT (2 yrs)<br><br>You'll study networking, cloud computing, cyber security, mobile apps, IoT, system administration - all the trending tech skills!<br><br>We have industry tie-ups for internships and projects. Plus certification programs to boost your resume.<br><br>IT sector has huge demand and great salaries. Our placement support will help you land a good job!<br><br>Want to know more about the curriculum?"
    },
    {
        "patterns": [
            "commerce",
            "bcom",
            "mcom",
            "accounting"
        ],
        "response": "Commerce opens doors to business and finance careers! 💼<br><br><b>Programs:</b> B.Com, B.Com (CA), M.Com (CA), M.Phil Commerce<br><br>You'll learn accounting, business management, economics, taxation, banking, e-commerce, Tally, GST - everything for business world!<br><br><b>Career paths:</b> CA, CS, banking jobs, financial analyst, tax consultant, business manager<br><br>It's also great foundation if you're planning CA or CS. Many of our commerce students go on to become successful professionals!<br><br>Thinking about commerce?"
    },
    {
        "patterns": [
            "english",
            "ba english",
            "ma english",
            "literature"
        ],
        "response": "English programs are perfect for language lovers! 📚<br><br><b>Programs:</b> B.A. English (3 yrs), M.A. English (2 yrs)<br><br>You'll study literature, grammar, creative writing, communication skills, British & American literature, Indian writing - it's fascinating!<br><br><b>Careers:</b> Teaching, content writing, journalism, publishing, translation, corporate communication, civil services<br><br>If you love reading, writing, and expressing yourself, English is your calling! Plus, good English skills are valuable everywhere.<br><br>Passionate about literature?"
    },
    {
        "patterns": [
            "maths",
            "mathematics",
            "bsc maths",
            "msc maths"
        ],
        "response": "Mathematics is the foundation of everything! 🔢<br><br><b>Programs:</b> B.Sc. Maths (3 yrs), M.Sc. Maths (2 yrs)<br><br>Algebra, calculus, statistics, differential equations, numerical methods, operations research - you'll master it all!<br><br><b>Careers:</b> Data scientist, statistician, actuarial science, research analyst, teaching, banking, government jobs<br><br>Strong analytical skills from maths are highly valued everywhere. Plus, it keeps your options open for many careers!<br><br>Good at maths? This could be your path!"
    },
    {
        "patterns": [
            "biotech",
            "biotechnology",
            "bsc biotech"
        ],
        "response": "Biotechnology is where biology meets technology! 🧬<br><br><b>Program:</b> B.Sc. Biotechnology (3 yrs)<br><br>Molecular biology, genetic engineering, microbiology, biochemistry, bioinformatics, immunology - cutting-edge science!<br><br>Our biotech lab has modern equipment and you'll get hands-on research experience.<br><br><b>Careers:</b> Research scientist, pharma industry, healthcare, agricultural biotech, environmental biotech<br><br>It's a growing field with amazing future prospects. Perfect if you're fascinated by how life works!"
    },
    {
        "patterns": [
            "micro",
            "microbiology",
            "clinical lab"
        ],
        "response": "Microbiology & Clinical Lab Tech is perfect for healthcare careers! 🔬<br><br><b>Program:</b> B.Sc. Microbiology & Clinical Lab Technology (3 yrs)<br><br>Medical microbiology, clinical pathology, immunology, virology, lab techniques, diagnostic methods - you'll learn it all!<br><br>You'll get hospital internships and real lab experience with modern equipment.<br><br><b>Careers:</b> Medical lab technician, hospital labs, diagnostic centers, research labs, pharma companies<br><br>Healthcare sector has huge demand! This is a stable, rewarding career."
    },
    {
        "patterns": [
            "bba",
            "business administration",
            "management"
        ],
        "response": "BBA prepares you to be a business leader! 💼<br><br><b>Program:</b> BBA (3 yrs)<br><br>Business management, marketing, HR, finance, entrepreneurship, communication, organizational behavior - complete business education!<br><br>You'll develop leadership, decision-making, problem-solving, team management skills.<br><br><b>Careers:</b> Business manager, marketing executive, HR manager, entrepreneur, or go for MBA<br><br>If you see yourself leading teams and running businesses, BBA is your starting point!"
    },
    {
        "patterns": [
            "physics",
            "bsc physics"
        ],
        "response": "Physics explores how the universe works! ⚛️<br><br><b>Program:</b> B.Sc. Physics (3 yrs)<br><br>Mechanics, quantum physics, thermodynamics, electromagnetism, optics, electronics, nuclear physics - fascinating stuff!<br><br>Well-equipped physics lab with modern instruments for experiments.<br><br><b>Careers:</b> Research scientist, teaching, electronics industry, space research, defense, higher studies<br><br>Physics opens doors to many scientific careers. Love understanding how things work? This is for you!"
    },
    {
        "patterns": [
            "electronics",
            "ece",
            "communication"
        ],
        "response": "Electronics & Communication is for tech enthusiasts! 📡<br><br><b>Program:</b> B.Sc. Electronics & Communication (3 yrs)<br><br>Electronic circuits, digital electronics, communication systems, microprocessors, signal processing, embedded systems<br><br>Hands-on training in electronics lab with circuit design and projects.<br><br><b>Careers:</b> Electronics engineer, telecom industry, hardware design, embedded systems, R&D, IT sector<br><br>High demand in electronics industry with great opportunities!"
    },
    {
        "patterns": [
            "environmental",
            "msc environmental"
        ],
        "response": "Environmental Science is about saving our planet! 🌍<br><br><b>Program:</b> M.Sc. Environmental Science (2 yrs)<br><br>Environmental chemistry, ecology, pollution control, climate change, waste management, conservation, environmental law<br><br>Field work, research projects, industry visits included.<br><br><b>Careers:</b> Environmental consultant, pollution control officer, NGOs, government departments, research, teaching<br><br>With climate change concerns, this field is more important than ever!"
    },
    {
        "patterns": [
            "tamil",
            "ba tamil"
        ],
        "response": "Tamil celebrates our beautiful language and culture! 📖<br><br><b>Program:</b> B.A. Tamil (3 yrs)<br><br>Tamil literature, classical Tamil, modern Tamil, grammar, translation, culture & heritage<br><br><b>Careers:</b> Teaching, translation, journalism, government jobs, publishing, cultural organizations<br><br>Preserve and promote our rich Tamil heritage while building a career!"
    },
    {
        "patterns": [
            "dress",
            "uniform",
            "wear"
        ],
        "response": "We have a simple, comfortable dress code: 👗<br><br>Formal or semi-formal attire - salwar kameez, churidar, or saree. Just keep it modest and professional. Don't forget your ID card!<br><br>Avoid casual wear like jeans on regular days. Special events might have specific dress codes.<br><br>It's all about looking neat and professional while being comfortable!"
    },
    {
        "patterns": [
            "attendance",
            "minimum",
            "required"
        ],
        "response": "Attendance is important for your learning! 📊<br><br>You need minimum 75% attendance as per university rules. We track it daily (biometric/manual).<br><br>Below 75%? You might not be allowed for exams. But if you have genuine medical reasons, submit certificates - we understand emergencies happen!<br><br>Regular attendance = better learning = better results. Simple! 😊"
    },
    {
        "patterns": [
            "holidays",
            "vacation",
            "break"
        ],
        "response": "We follow a good academic calendar with regular breaks! 🗓️<br><br>You get national holidays, state holidays, festival holidays, semester breaks, and summer vacation (May-June). Pongal holidays too!<br><br>Odd semester: July-Nov, Even semester: Dec-April<br><br>Holiday list is announced at the start of the year. Enough time to relax and recharge!"
    },
    {
        "patterns": [
            "canteen",
            "food",
            "mess",
            "cafeteria"
        ],
        "response": "Our cafeteria serves tasty, hygienic food! 🍽️<br><br>Vegetarian menu with South Indian, North Indian items, snacks, beverages, fresh juices. Breakfast, lunch, snacks - all at affordable prices!<br><br>Hostel mess provides three nutritious meals daily. Special food on festivals!<br><br>Clean, comfortable dining area. Students love the food here!"
    },
    {
        "patterns": [
            "wifi",
            "internet",
            "network"
        ],
        "response": "Stay connected with our Wi-Fi! 🌐<br><br>High-speed Wi-Fi throughout campus - classrooms, library, hostel, everywhere! Computer labs have internet too.<br><br>Use it for academic work, research, online learning, projects. Digital learning made easy!<br><br>No connectivity issues here!"
    },
    {
        "patterns": [
            "medical",
            "health",
            "sick",
            "doctor"
        ],
        "response": "Your health matters to us! 🏥<br><br>We have first aid room, basic medical supplies, and tie-ups with nearby hospitals. Emergency contact numbers are available.<br><br>Annual health checkups, health awareness programs, counseling services - we take care of you!<br><br>Medical leave? Just submit certificates. Your wellbeing is our priority!"
    },
    {
        "patterns": [
            "counseling",
            "mental",
            "stress",
            "guidance"
        ],
        "response": "We're here to support you! 🤝<br><br>Personal counseling, academic guidance, career counseling, stress management - all available. Sessions are confidential.<br><br>Academic pressure? Personal issues? Career confusion? Peer problems? Talk to our counselors.<br><br>Don't hesitate to seek help. Everyone needs support sometimes. We've got your back!"
    },
    {
        "patterns": [
            "bank",
            "atm",
            "banking"
        ],
        "response": "Banking facilities are convenient! 🏦<br><br>ATMs near campus, banks in Karaikudi, online banking support. Fee payment through banks is easy.<br><br>All your financial needs covered!"
    },
    {
        "patterns": [
            "parent",
            "parents",
            "pta"
        ],
        "response": "We keep parents in the loop! 👨👩👧<br><br>Regular PTA meetings, progress reports, parent-teacher meetings, updates - parents are partners in your education!<br><br>Open communication ensures everyone's on the same page about your progress."
    },
    {
        "patterns": [
            "ragging",
            "safe",
            "safety"
        ],
        "response": "Absolutely ragging-free campus! 🛡️<br><br>Strict zero-tolerance policy. Severe punishment for offenders. 24/7 helpline: 1800-180-5522. Anti-ragging committee monitors regularly.<br><br>Your safety is 100% guaranteed. Report any incident immediately. You're completely safe here!"
    },
    {
        "patterns": [
            "research",
            "projects",
            "innovation"
        ],
        "response": "We encourage research and innovation! 🔬<br><br>M.Phil programs, research projects, faculty guidance, university collaborations, publications, conferences<br><br>Research labs, library resources, internet, industry collaboration - all support available.<br><br>Build your research career with us!"
    },
    {
        "patterns": [
            "how are you",
            "how r u",
            "whats up"
        ],
        "response": "I'm doing great, thanks for asking! 😊 More importantly, how can I help YOU today? Got questions about admissions, courses, or anything else about Dr. URCW?"
    },
    {
        "patterns": [
            "who are you",
            "what are you",
            "your name"
        ],
        "response": "I'm your friendly virtual assistant for Dr. URCW! 🤖 Think of me as your personal guide to everything about our college. I'm here 24/7 to answer your questions and help you out. What would you like to know?"
    },
    {
        "patterns": [
            "thanks",
            "thank you",
            "thx",
            "appreciate"
        ],
        "response": "You're so welcome! 😊 Happy I could help! Got more questions? I'm right here. Best of luck with everything!"
    },
    {
        "patterns": [
            "bye",
            "goodbye",
            "see you",
            "later"
        ],
        "response": "Goodbye! 👋 It was lovely chatting with you. Come back anytime you need help. Best wishes for your future! Take care! 🌟"
    }
]

def semantic_match(q, d):
    v = TfidfVectorizer()
    t = v.fit_transform(d + [q])
    s = cosine_similarity(t[-1], t[:-1]).flatten()
    return max(s), s.argmax()

def get_bot_response(message: str, user_id: int, db: Session) -> str:
    c = clean_text(message)
    e = db.query(KnowledgeBase).all()
    
    if e:
        k = [x.keyword for x in e]
        s, i = semantic_match(c, k)
        if s >= 0.18:
            return e[i].answer
    
    p, m = [], []
    for intent in INTENTS:
        for pat in intent["patterns"]:
            p.append(pat)
            m.append(intent)
    
    if p:
        s, i = semantic_match(c, p)
        if s >= 0.18:
            return m[i]["response"]
    
    for intent in INTENTS:
        for pat in intent["patterns"]:
            if fuzz.partial_ratio(c, pat) >= 55:
                return intent["response"]
    
    db.add(UnansweredQuestion(user_id=user_id, question=message, status="pending"))
    db.commit()
    
    return "Hmm, I don't have that info right now. 🤔<br><br>But no worries! I've sent your question to our admin team. They'll get back to you soon with the answer!<br><br>Meanwhile, ask me about admissions, courses, fees, facilities, placements, or campus life. I'm here to help! 😊"
