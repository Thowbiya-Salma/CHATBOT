# chatbot_data.py

# ---------------- RESPONSES ---------------- #

ABOUT = (
    "<b>About Dr. Umayal Ramanathan College for Women (Dr. URCW)</b><br><br>"
    "Established in 2006 and affiliated with Alagappa University, "
    "Dr. Umayal Ramanathan College for Women (Dr. URCW) is a premier institution "
    "dedicated to empowering women through transformative, value-based education.<br><br>"
    "<b>Key Milestones & Recognitions</b><br>"
    "• NAAC ‘A’ Grade (CGPA 3.22 / 4.0)<br>"
    "• ISO 9001:2015 Certified<br>"
    "• UGC 2(f) & 12(B) Recognition<br>"
    "• 461 University Ranks<br>"
    "• Active member of IIC, Ministry of Education<br>"
)

PROGRAMS_OFFERED = (
    "<b>Programmes Offered</b><br><br>"
    "• 13 Undergraduate Programmes<br>"
    "• 5 Postgraduate Programmes<br>"
    "• 1 PG Diploma Programme<br>"
    "• 3 Research Programmes"
)

PRINCIPAL = (
    "<b>Principal</b><br><br>"
    "Dr. A. Hemamalini Ganesan<br>"
    "M.B.A., M.L.M., M.Phil., M.A., Ph.D., SET"
)

EXAM = (
    "<b>Examination Pattern</b><br><br>"
    "• 3 Internal Exams per semester<br>"
    "• UG – 6 Semesters<br>"
    "• PG – 4 Semesters"
)

PLACEMENT = ( 
             "<b>Training and Placement Cell</b><br><br>" 
             "• The Training and Placement Cell brings job opportunities for students of all courses.<br>" 
             "• It acts as a nodal point of contact for companies to identify future workforce from Dr. URCW.<br>" 
             "• The cell strives to secure employment for students in reputed companies during their final year of study.<br>" 
             "• Students get placed directly after college, fulfilling their career aspirations.<br>" 
             "• On-Campus and Off-Campus interview opportunities are facilitated for students.<br>" 
             "• Internship opportunities are provided to support curriculum and industry-ready skills.<br>" 
             "• Career guidance and competitive exam guidance are offered to students.<br>" 
             "• Support is given for resume writing and communication skills development." )

HOSTEL = ( 
          "<b>Hostel Facilities</b><br><br>" 
          "• The college provides excellent hostel facilities in a clean and hygienic environment.<br>" 
          "• The hostel has spacious rooms, dining halls, and a recreation hall with television, newspapers, and magazines.<br>" 
          "• Medical facilities and support services are available for students.<br>" 
          "• The hostel provides good, hygienic, and nutritious food.<br>" 
          "• Uninterrupted power supply, STD/ISD telephone facilities, and high-speed Wi-Fi connectivity are available.<br>" 
          "• The hostel is managed by the Chief Warden, Deputy Wardens, and Mess Representatives who ensure a safe and comfortable atmosphere for students."
          )

LIBRARY = (
    "<b>Library</b><br><br>"
    "Automated library with digital resources and open access system."
)

APPLICATION = (
    "<b>Admissions</b><br><br>"
    "Online applications available at:<br>"
    "https://umayalwomenscollege.co.in/application-form/"
)

CONTACT = (
    "<b>Contact</b><br><br>"
    "Karaikudi, Sivagangai District<br>"
    "Phone: 04565-227861<br>"
    "Email: womenscollege@alagappa.org"
)

GREETING = (
    "<b>Welcome to Dr. URCW</b><br><br>"
    "How can I help you today?"
)

THANKYOU = "You're welcome 😊"

WEBSITE = "https://umayalwomenscollege.co.in/"

# ---------------- NLP INTENTS ---------------- #

INTENTS = [

    {
        "name": "greeting",
        "keywords": ["hi", "hello", "hey", "good morning", "good evening"],
        "response": GREETING
    },

    {
        "name": "about_college",
        "keywords": ["college", "urcw", "umayal", "college details"],
        "response": ABOUT
    },

    {
        "name": "programmes",
        "keywords": ["program", "programme", "courses", "programs offered"],
        "response": PROGRAMS_OFFERED
    },

    {
        "name": "principal",
        "keywords": ["principal", "head", "principal details"],
        "response": PRINCIPAL
    },

    {
        "name": "examination",
        "keywords": ["exam", "examination", "exam pattern", "semester"],
        "response": EXAM
    },

    {
        "name": "placements",
        "keywords": ["placement", "job", "internship", "career"],
        "response": PLACEMENT
    },

    {
        "name": "hostel",
        "keywords": ["hostel", "accommodation", "stay"],
        "response": HOSTEL
    },

    {
        "name": "library",
        "keywords": ["library", "books", "reading"],
        "response": LIBRARY
    },

    {
        "name": "admission",
        "keywords": ["admission", "apply", "application"],
        "response": APPLICATION
    },

    {
        "name": "contact",
        "keywords": ["contact", "phone", "email", "address"],
        "response": CONTACT
    },

    {
        "name": "website",
        "keywords": ["website", "url", "link"],
        "response": WEBSITE
    },

    {
        "name": "thanks",
        "keywords": ["thanks", "thank you"],
        "response": THANKYOU
    }
]

