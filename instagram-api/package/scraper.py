import os
import re
import logging
import requests
import json
from bs4 import BeautifulSoup
from tenacity import retry, stop_after_attempt, wait_exponential
import urllib.parse
import time

# लॉगर सेटअप
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# --- स्क्रैपिंग का प्रयास करने वाले फंक्शन ---

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=30))
def attempt_scraping_with_api(url, api_func):
    logger.info(f"Attempting to scrape {url} with {api_func.__name__}")
    return api_func(url)

def scrape_with_scraperapi(url):
    """प्राइमरी स्क्रैपर: ScraperAPI"""
    try:
        api_key = os.environ.get('SCRAPER_API_KEY')
        api_url = f"http://api.scraperapi.com?api_key={api_key}&url={urllib.parse.quote(url)}&render=true&timeout=60"
        response = requests.get(api_url, timeout=65)
        
        # ब्लॉक डिटेक्शन
        if response.status_code == 403:
            raise Exception("ScraperAPI: 403 Forbidden")
        if "blocked" in response.text.lower():
            raise Exception("ScraperAPI blocked by Instagram")
        
        response.raise_for_status()
        return response.text
    except Exception as e:
        logger.error(f"ScraperAPI failed: {str(e)}")
        raise

def scrape_with_scrapingdog(url):
    """बैकअप स्क्रैपर: Scrapingdog (नया API key के साथ)"""
    try:
        api_key = os.environ.get('SCRAPINGDOG_API_KEY')
        api_url = f"https://api.scrapingdog.com/scrape?api_key={api_key}&url={urllib.parse.quote(url)}&dynamic=true&render=true"
        
        # हेडर जोड़ें
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        response = requests.get(api_url, headers=headers, timeout=65)
        
        # ब्लॉक डिटेक्शन
        if "Contact us at info@scrapingdog.com" in response.text:
            raise Exception("Scrapingdog requires Instagram activation")
        if "blocked" in response.text.lower():
            raise Exception("Scrapingdog blocked by Instagram")
        
        response.raise_for_status()
        return response.text
    except Exception as e:
        logger.error(f"Scrapingdog failed: {str(e)}")
        raise

def scrape_with_scrapingbee(url):
    """वैकल्पिक स्क्रैपर: ScrapingBee"""
    try:
        api_key = os.environ.get('SCRAPINGBEE_API_KEY')
        api_url = f"https://app.scrapingbee.com/api/v1?api_key={api_key}&url={urllib.parse.quote(url)}&render_js=true&wait=5000"
        
        # हेडर जोड़ें
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        response = requests.get(api_url, headers=headers, timeout=30)
        
        # ब्लॉक डिटेक्शन
        if response.status_code == 403:
            raise Exception("ScrapingBee: 403 Forbidden")
        if "blocked" in response.text.lower():
            raise Exception("ScrapingBee blocked by Instagram")
        
        response.raise_for_status()
        return response.text
    except Exception as e:
        logger.error(f"ScrapingBee failed: {str(e)}")
        raise

# --- मुख्य स्क्रैपिंग फंक्शन ---

def scrape_url(url, link_type):
    services = [
        scrape_with_scrapingbee,
        scrape_with_scraperapi,
        scrape_with_scrapingdog
    ]
    
    for service in services:
        try:
            logger.info(f"Trying with {service.__name__}...")
            start_time = time.time()
            html_content = attempt_scraping_with_api(url, service)
            elapsed = time.time() - start_time
            
            # HTML सामग्री की जाँच करें
            if not html_content or len(html_content) < 500:
                raise ValueError(f"Empty or invalid HTML content (length: {len(html_content)})")
                
            logger.info(f"Scraped with {service.__name__} in {elapsed:.2f}s, length: {len(html_content)}")
            logger.debug(f"HTML snippet: {html_content[:500]}...") 
            
            soup = BeautifulSoup(html_content, 'html.parser')
            
            if link_type == 'profile':
                return parse_profile(soup, html_content)
            elif link_type == 'post':
                return parse_post(soup, html_content)
                
        except Exception as e:
            logger.error(f"{service.__name__} failed: {str(e)}")
    
    logger.error("All scraping services failed")
    raise Exception("All scraping services failed. Please try again later.")

# --- सरल पार्सिंग फंक्शन ---

def parse_profile(soup, html_content):
    try:
        # सरल विधि: Open Graph मेटाडेटा
        return {
            "name": soup.find("meta", property="og:title")["content"] if soup.find("meta", property="og:title") else "",
            "username": url.split("/")[-2] if url.startswith("https://www.instagram.com/") else "",
            "avatar_url": soup.find("meta", property="og:image")["content"] if soup.find("meta", property="og:image") else ""
        }
    except Exception as e:
        logger.error(f"Profile parse error: {str(e)}")
        return {"error": "Failed to parse profile"}

def parse_post(soup, html_content):
    try:
        # 1. Open Graph विधि
        media_url = ""
        for prop in ['og:video', 'og:video:url', 'og:image', 'og:image:url']:
            tag = soup.find("meta", property=prop)
            if tag and tag.get("content", ""):
                media_url = tag["content"]
                break
        
        # 2. JSON-LD विधि
        if not media_url:
            script_tag = soup.find('script', type='application/ld+json')
            if script_tag:
                try:
                    data = json.loads(script_tag.string)
                    media_url = data.get("video", {}).get("contentUrl", "") or data.get("image", {}).get("url", "")
                except:
                    pass
        
        # 3. डायरेक्ट टैग्स
        if not media_url:
            video = soup.find('video')
            if video:
                media_url = video.get('src') or video.find('source').get('src', '')
        
        if not media_url:
            img = soup.find('img')
            if img:
                media_url = img.get('src', '')
        
        # कैप्शन
        caption = soup.find("meta", property="og:description").get('content', '') if soup.find("meta", property="og:description") else ""
        
        return {
            "download_url": media_url,
            "caption": caption,
            "success": bool(media_url)
        }
    except Exception as e:
        logger.error(f"Post parse error: {str(e)}")
        return {"error": "Failed to parse post"}