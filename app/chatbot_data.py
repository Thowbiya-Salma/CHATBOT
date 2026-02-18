import random

def intro():
    return random.choice([
        "Sure 😊 Here's what I found:",
        "Great question! Let me explain:",
        "I'd be happy to help!",
        "Here’s some useful information:",
        "Let’s take a look 👇"
    ])

def link(text, url):
    return f"<a href='{url}' target='_blank'>{text}</a>"


INTENTS = [

    # ABOUT
    {
        "name": "about_college",
        "keywords": ["about", "urcw", "college details", "history"],
        "response": lambda: f"""
<b>{intro()}</b><br><br>
Dr. Umayal Ramanathan College for Women (Dr.URCW) was established in 2006 and is affiliated with Alagappa University. 
It holds a NAAC 'A' Grade accreditation and is ISO 9001:2015 certified. The institution focuses on empowering women through value-based and transformative education.<br><br>
More details here: {link("About URCW", "https://umayalwomenscollege.co.in/about/about-urcw/")}
"""
    },

    # UG COURSES
    {
        "name": "ug_courses",
        "keywords": ["ug courses", "undergraduate", "bachelor", "bsc", "bcom", "ba"],
        "response": lambda: f"""
<b>{intro()}</b><br><br>
Here are the Undergraduate programmes offered:<br>
• B.A. English<br>
• B.A. Tamil<br>
• B.B.A<br>
• B.Com (General)<br>
• B.Com (Computer Applications)<br>
• B.Sc Mathematics<br>
• B.Sc Physics<br>
• B.Sc Computer Science<br>
• B.Sc IT<br>
• B.Sc Electronics & Communication<br>
• B.Sc Biotechnology<br>
• B.Sc Microbiology & Clinical Lab Technology<br><br>
Check full details here: {link("UG Courses Page", "https://umayalwomenscollege.co.in/admission/ug-courses/")}
"""
    },

    # PG COURSES
    {
        "name": "pg_courses",
        "keywords": ["pg courses", "postgraduate", "masters", "msc", "ma", "mcom"],
        "response": lambda: f"""
<b>{intro()}</b><br><br>
Postgraduate programmes include:<br>
• M.Sc Mathematics<br>
• M.Sc Computer Science<br>
• M.Sc Information Technology<br>
• M.A English<br>
• M.Com (Computer Applications)<br><br>
These programmes are ideal for advanced academic and research opportunities.<br>
More here: {link("PG Courses Page", "https://umayalwomenscollege.co.in/admission/pg-courses/")}
"""
    },

    # ADMISSION PROCEDURE
    {
        "name": "admission_procedure",
        "keywords": ["admission", "how to apply", "eligibility", "application"],
        "response": lambda: f"""
<b>{intro()}</b><br><br>
Admissions are merit-based and transparent. Students must submit an application form, after which selections are based on academic merit and interview (if required). No capitation fee is charged.<br><br>
For full procedure: {link("Admission Procedure", "https://umayalwomenscollege.co.in/admission/admission-procedure/")}
"""
    },

    # ELIGIBILITY
    {
        "name": "eligibility",
        "keywords": ["eligibility", "who can apply", "qualification"],
        "response": lambda: f"""
<b>{intro()}</b><br><br>
For UG programmes, students must have completed Higher Secondary education (12th grade).<br>
For PG programmes, a relevant Bachelor's degree is required.<br><br>
Specific eligibility varies by department. See detailed rules here: {link("Admission Details", "https://umayalwomenscollege.co.in/admission/admission-procedure/")}
"""
    },

    # PLACEMENT
    {
        "name": "placement",
        "keywords": ["placement", "job", "internship", "career"],
        "response": lambda: f"""
<b>{intro()}</b><br><br>
The Training & Placement Cell prepares students for professional success through:<br>
• Campus recruitment drives<br>
• Internship opportunities<br>
• Resume building workshops<br>
• Communication skills training<br>
• Career guidance<br><br>
More info: {link("Placement Cell", "https://umayalwomenscollege.co.in/placement/")}
"""
    },

    # CLUBS & CELLS
    {
        "name": "clubs",
        "keywords": ["clubs", "cells", "extracurricular", "activities"],
        "response": lambda: f"""
<b>{intro()}</b><br><br>
The college encourages holistic development through various clubs and cells including:<br>
• Entrepreneurship Development Cell<br>
• Eco Club<br>
• Health & Wellness Club<br>
• National Service Scheme<br>
• Skill Development Cell<br><br>
Explore here: {link("Clubs & Cells", "https://umayalwomenscollege.co.in/club_cells/")}
"""
    },

    # COMMITTEES
    {
        "name": "committee",
        "keywords": ["committee", "anti ragging", "grievance", "sc/st"],
        "response": lambda: f"""
<b>{intro()}</b><br><br>
The college has multiple committees to ensure student welfare, including:<br>
• Anti-Ragging Committee<br>
• Grievance Redressal Committee<br>
• SC/ST Committee<br>
• Internal Complaints Committee<br><br>
More here: {link("Committees Page", "https://umayalwomenscollege.co.in/committee/")}
"""
    },

    # ALUMNI
    {
        "name": "alumni",
        "keywords": ["alumni", "former students", "ex students"],
        "response": lambda: f"""
<b>{intro()}</b><br><br>
Alumni are an integral part of the institution’s growth. Former students can connect and register through the alumni portal.<br><br>
Visit: {link("Alumni Registration", "https://www.alagappaalumni.com/user/signup.dz")}
"""
    }

]
