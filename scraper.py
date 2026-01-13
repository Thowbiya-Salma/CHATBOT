import requests
from bs4 import BeautifulSoup

URL = "https://umayalwomenscollege.co.in/"

def get_college_text():
    res = requests.get(URL, timeout=10)
    soup = BeautifulSoup(res.text, "html.parser")
    return [p.get_text() for p in soup.find_all("p") if len(p.get_text()) > 50]
