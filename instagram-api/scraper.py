import os
import requests
from bs4 import BeautifulSoup
import re
import time
import random
from tenacity import retry, stop_after_attempt, wait_exponential

# --- पार्सिंग फंक्शन ---
def parse_profile_page(soup):
    try:
        # मेटा टैग से डेटा निकालना सबसे विश्वसनीय तरीका है
        description = soup.find("meta", property="og:description")
        content = description["content"] if description else ""

        stats = {
            "followers": content.split("Followers")[0].strip(),
            "following": content.split("Following")[0].split(",")[-1].strip(),
            "posts": content.split("Posts")[0].split(",")[-1].strip()
        }
        
        # नाम निकालने की कोशिश करें
        name = soup.find("title").text.split("•")[0].strip()
        username = soup.find("meta", property="og:title")["content"] if soup.find("meta", property="og:title") else name
        
        # बायो निकालने की कोशिश करें (यह मुश्किल हो सकता है)
        bio = "" # इंस्टाग्राम के नए लेआउट में बायो निकालना मुश्किल है, इसे बाद में देखेंगे
        
        return {
            "name": name, "username": username, "stats": stats, "bio": bio,
            "avatar_url": soup.find("meta", property="og:image")["content"]
        }
    except Exception as e:
        print(f"Error parsing profile page: {e}")
        raise ValueError("Could not parse the Instagram profile data.")

def parse_post_page(soup):
    try:
        # वीडियो या इमेज का डायरेक्ट लिंक निकालें
        media_url = soup.find("meta", property="og:video") or soup.find("meta", property="og:image")
        if not media_url:
            raise ValueError("Could not find media URL.")

        return {"download_url": media_url["content"]}
    except Exception as e:
        print(f"Error parsing post page: {e}")
        raise ValueError("Could not parse the Instagram post data.")

# --- मुख्य स्क्रैपिंग फंक्शन ---
@retry(stop=stop_after_attempt(2), wait=wait_exponential(multiplier=1, min=2, max=10))
def attempt_scraping(url, api_func):
    return api_func(url)

def scrape_url(url, link_type):
    # नैतिक स्क्रैपिंग: एक रैंडम डिले जोड़ें
    time.sleep(random.uniform(1, 2))
    
    scraper_api_key = os.environ.get('SCRAPER_API_KEY')
    scrapingdog_api_key = os.environ.get('SCRAPINGDOG_API_KEY')

    def via_scraperapi(target_url):
        print("Trying with ScraperAPI...")
        response = requests.get('https://api.scraperapi.com', params={'api_key': scraper_api_key, 'url': target_url, 'render': 'true'}, timeout=25)
        response.raise_for_status()
        return BeautifulSoup(response.text, 'html.parser')

    def via_scrapingdog(target_url):
        print("Falling back to Scrapingdog...")
        response = requests.get('https://api.scrapingdog.com/scrape', params={'api_key': scrapingdog_api_key, 'url': target_url, 'dynamic': 'true'}, timeout=25)
        response.raise_for_status()
        return BeautifulSoup(response.text, 'html.parser')

    try:
        soup = attempt_scraping(url, via_scraperapi)
    except Exception as e:
        print(f"ScraperAPI failed after retries: {e}")
        try:
            soup = via_scrapingdog(url)
        except Exception as e2:
            print(f"Scrapingdog also failed: {e2}")
            raise Exception("Both scraping services failed.")

    # लिंक के प्रकार के आधार पर सही पार्सर चुनें
    if link_type == "profile":
        return parse_profile_page(soup)
    elif link_type == "post":
        return parse_post_page(soup)
    else:
        raise ValueError("Unknown link type for parsing.")