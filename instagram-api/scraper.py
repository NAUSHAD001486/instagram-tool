import os
import re
import logging
import requests
import json
from bs4 import BeautifulSoup
from tenacity import retry, stop_after_attempt, wait_exponential
import urllib.parse
import time
import random

# लॉगिंग कॉन्फ़िगर करें
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# पर्यावरण चर से API कुंजियाँ
SCRAPINGDOG_API_KEY = os.environ.get('SCRAPINGDOG_API_KEY', '6880b6230982aa8b8a059c5b')
SCRAPERAPI_KEY = os.environ.get('SCRAPER_API_KEY', 'ef73e97059e19e44e271e17ec8d86c6e')
SCRAPINGBEE_API_KEY = os.environ.get('SCRAPINGBEE_API_KEY', 'U1GQPZ2V3UJYH7T4V6LJ9Y7WZR')

# डिबगिंग के लिए विस्तृत हेडर
DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9,hi;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Referer": "https://www.google.com/",
    "DNT": "1",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
}

@retry(stop=stop_after_attempt(2), wait=wait_exponential(multiplier=1, min=2, max=10))
def api_ke_sath_scraping_kare(url, api_func):
    """API का उपयोग करके स्क्रैपिंग का प्रयास करें"""
    logger.info(f"{api_func.__name__} के साथ {url} स्क्रैप करने का प्रयास कर रहा हूँ")
    return api_func(url)

def scrapingdog_se_scrape_kare(url, link_type):
    """प्राथमिकता: समर्पित एंडपॉइंट्स के साथ ScrapingDog"""
    try:
        base_url = "https://api.scrapingdog.com/"
        params = {
            "api_key": SCRAPINGDOG_API_KEY,
            "proxy_type": "residential"  # रेजिडेंशियल प्रॉक्सी का उपयोग करें
        }
        
        if link_type == 'profile':
            # प्रोफाइल यूजरनेम निकालें
            username = url.split("/")[-1].split("?")[0]
            if not username or username == '':
                username = url.split("/")[-2].split("?")[0]
                
            api_url = f"{base_url}instagram/profile"
            params["username"] = username
            
            logger.info(f"ScrapingDog प्रोफाइल: {username}")
            response = requests.get(api_url, params=params, headers=DEFAULT_HEADERS, timeout=30)
            
            # डिबगिंग जानकारी
            logger.info(f"ScrapingDog स्थिति कोड: {response.status_code}")
            
            if response.status_code != 200:
                # विस्तृत त्रुटि जानकारी
                logger.error(f"ScrapingDog API त्रुटि: {response.text[:500]}")
                raise Exception(f"ScrapingDog API त्रुटि: {response.status_code}")
            
            data = response.json()
            
            # प्रतिक्रिया डेटा लॉग करें
            logger.info(f"ScrapingDog डेटा: {json.dumps(data, indent=2)[:500]}")
            
            return {
                "name": data.get("full_name", ""),
                "username": data.get("username", ""),
                "avatar_url": data.get("profile_pic_url_hd", data.get("profile_pic_url", ""))
            }
            
        else:  # पोस्ट
            # URL से शॉर्टकोड निकालें
            parsed_url = urllib.parse.urlparse(url)
            path_segments = [seg for seg in parsed_url.path.split("/") if seg]
            shortcode = path_segments[-1] if path_segments else ""
            
            if not shortcode:
                shortcode = url.split("/")[-2].split("?")[0]
                
            if not shortcode:
                raise ValueError(f"URL से शॉर्टकोड निकालने में विफल: {url}")
            
            api_url = f"{base_url}instagram/post"
            params["shortcode"] = shortcode
            
            logger.info(f"ScrapingDog पोस्ट: {shortcode}")
            response = requests.get(api_url, params=params, headers=DEFAULT_HEADERS, timeout=35)
            
            # डिबगिंग जानकारी
            logger.info(f"ScrapingDog स्थिति कोड: {response.status_code}")
            
            if response.status_code != 200:
                # विस्तृत त्रुटि जानकारी
                logger.error(f"ScrapingDog API त्रुटि: {response.text[:500]}")
                raise Exception(f"ScrapingDog API त्रुटि: {response.status_code}")
            
            data = response.json()
            
            # प्रतिक्रिया डेटा लॉग करें
            logger.info(f"ScrapingDog डेटा: {json.dumps(data, indent=2)[:500]}")
            
            # मीडिया URL निकालें
            download_url = ""
            if "media" in data and isinstance(data["media"], list) and len(data["media"]) > 0:
                media = data["media"][0]
                download_url = media.get("video_url") or media.get("display_url", "")
            else:
                download_url = data.get("video_url") or data.get("display_url", "")
            
            # अगर फिर भी URL नहीं मिला तो अन्य स्थानों में खोजें
            if not download_url:
                # वैकल्पिक स्थानों से URL निकालें
                if "graphql" in data and "shortcode_media" in data["graphql"]:
                    media_data = data["graphql"]["shortcode_media"]
                    if "video_url" in media_data:
                        download_url = media_data["video_url"]
                    elif "display_url" in media_data:
                        download_url = media_data["display_url"]
            
            return {
                "download_url": download_url,
                "caption": data.get("caption", ""),
                "success": bool(download_url)
            }
                
    except Exception as e:
        logger.error(f"Scrapingdog विफल: {str(e)}", exc_info=True)
        raise

def scraperapi_se_scrape_kare(url):
    """बैकअप: ScraperAPI"""
    try:
        api_url = f"http://api.scraperapi.com?api_key={SCRAPERAPI_KEY}&url={urllib.parse.quote(url)}&render=true&timeout=60000"
        logger.info(f"ScraperAPI URL: {api_url}")
        response = requests.get(api_url, headers=DEFAULT_HEADERS, timeout=30)
        logger.info(f"ScraperAPI स्थिति कोड: {response.status_code}")
        response.raise_for_status()
        return response.text
    except Exception as e:
        logger.error(f"ScraperAPI विफल: {str(e)}", exc_info=True)
        raise

def scrapingbee_se_scrape_kare(url):
    """अंतिम विकल्प: ScrapingBee"""
    try:
        api_url = f"https://app.scrapingbee.com/api/v1?api_key={SCRAPINGBEE_API_KEY}&url={urllib.parse.quote(url)}&render_js=true&wait=10000"
        logger.info(f"ScrapingBee URL: {api_url}")
        response = requests.get(api_url, headers=DEFAULT_HEADERS, timeout=30)
        logger.info(f"ScrapingBee स्थिति कोड: {response.status_code}")
        response.raise_for_status()
        return response.text
    except Exception as e:
        logger.error(f"ScrapingBee विफल: {str(e)}", exc_info=True)
        raise

def html_content_ko_parse_kare(html_content, link_type, url):
    """लिंक प्रकार के आधार पर HTML कंटेंट पार्स करें"""
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        
        if link_type == 'profile':
            return profile_parse_kare(soup, url)
        elif link_type == 'post':
            return post_parse_kare(soup)
    except Exception as e:
        logger.error(f"HTML पार्स करने में विफल: {str(e)}")
        raise

def url_ko_scrape_kare(url, link_type):
    # सर्विसेज को प्राथमिकता क्रम में
    services = [
        lambda: scrapingdog_se_scrape_kare(url, link_type),
        lambda: html_content_ko_parse_kare(scraperapi_se_scrape_kare(url), link_type, url),
        lambda: html_content_ko_parse_kare(scrapingbee_se_scrape_kare(url), link_type, url)
    ]
    
    errors = []
    
    # पहले ScrapingDog को 2 बार आज़माएं
    for attempt in range(2):
        try:
            logger.info(f"ScrapingDog का प्रयास #{attempt+1}")
            result = scrapingdog_se_scrape_kare(url, link_type)
            return result
        except Exception as e:
            error_msg = f"ScrapingDog प्रयास #{attempt+1} विफल: {str(e)}"
            logger.error(error_msg)
            errors.append(error_msg)
            time.sleep(random.uniform(1, 3))
    
    # अन्य सेवाएं आज़माएं
    for service in services[1:]:
        try:
            logger.info(f"अगली सेवा का प्रयास: {service.__name__}")
            result = service()
            return result
        except Exception as e:
            error_msg = f"{service.__name__} विफल: {str(e)}"
            logger.error(error_msg)
            errors.append(error_msg)
            time.sleep(random.uniform(1, 3))
    
    # फॉलबैक विधि
    return fallback_scraping(url, link_type, errors)

# बेहतर पार्सिंग के साथ फॉलबैक विधि
def fallback_scraping(url, link_type, errors):
    try:
        logger.warning("उन्नत फॉलबैक विधि का उपयोग कर रहा हूँ")
        
        response = requests.get(url, headers=DEFAULT_HEADERS, timeout=15)
        logger.info(f"फॉलबैक स्थिति कोड: {response.status_code}")
        response.raise_for_status()
        
        html_content = response.text
        parsed = html_content_ko_parse_kare(html_content, link_type, url)
        
        if link_type == 'post' and parsed.get('success'):
            return parsed
        if link_type == 'profile' and parsed.get('username'):
            return parsed
            
        # oEmbed API का प्रयास करें
        logger.warning("oEmbed API का उपयोग कर रहा हूँ")
        oembed_url = f"https://api.instagram.com/oembed/?url={urllib.parse.quote(url)}"
        oembed_response = requests.get(oembed_url, headers=DEFAULT_HEADERS, timeout=10)
        logger.info(f"oEmbed स्थिति कोड: {oembed_response.status_code}")
        
        if oembed_response.status_code == 200:
            oembed_data = oembed_response.json()
            logger.info(f"oEmbed डेटा: {json.dumps(oembed_data, indent=2)}")
            
            if link_type == 'post':
                return {
                    "download_url": oembed_data.get('thumbnail_url', ''),
                    "caption": BeautifulSoup(oembed_data.get('html', ''), 'html.parser').get_text(strip=True),
                    "success": True
                }
            else:  # प्रोफाइल
                username = url.split("/")[-1].split("?")[0]
                return {
                    "name": oembed_data.get('author_name', ''),
                    "username": username,
                    "avatar_url': oembed_data.get('thumbnail_url', '')
                }
        
        return {
            "success": False,
            "error": "सभी विधियाँ विफल",
            "details": " | ".join(errors) if errors else "कोई त्रुटि विवरण उपलब्ध नहीं"
        }
            
    except Exception as e:
        logger.error(f"उन्नत फॉलबैक विफल: {str(e)}", exc_info=True)
        return {
            "success": False,
            "error": "फॉलबैक विफल",
            "details": f"त्रुटियाँ: {' | '.join(errors)} | फॉलबैक: {str(e)}" if errors else str(e)
        }

# सुधारित पार्सिंग फ़ंक्शंस
def profile_parse_kare(soup, url):
    try:
        # JSON-LD डेटा का प्रयास करें
        script_tag = soup.find('script', type='application/ld+json')
        if script_tag:
            try:
                data = json.loads(script_tag.string)
                logger.info(f"JSON-LD डेटा: {json.dumps(data, indent=2)[:500]}")
                return {
                    "name": data.get("name", ""),
                    "username": data.get("alternateName", ""),
                    "avatar_url": data.get("image", {}).get("url", "") if isinstance(data.get("image"), dict) else data.get("image", "")
                }
            except Exception as e:
                logger.warning(f"JSON-LD पार्स करने में विफल: {str(e)}")
        
        # मेटा टैग्स पर फॉलबैक
        og_title = soup.find("meta", property="og:title")
        og_image = soup.find("meta", property="og:image")
        twitter_title = soup.find("meta", property="twitter:title")
        
        name = ""
        if og_title and og_title.get("content"):
            name = og_title["content"]
        elif twitter_title and twitter_title.get("content"):
            name = twitter_title["content"]
        
        avatar_url = ""
        if og_image and og_image.get("content"):
            avatar_url = og_image["content"]
        
        # यूजरनेम URL से निकालें
        username = ""
        path_segments = [seg for seg in urllib.parse.urlparse(url).path.split("/") if seg]
        if path_segments:
            username = path_segments[-1]
        
        # अंतिम फॉलबैक
        if not username and path_segments and len(path_segments) > 1:
            username = path_segments[-2]
        
        return {
            "name": name,
            "username": username,
            "avatar_url": avatar_url
        }
    except Exception as e:
        logger.error(f"प्रोफाइल पार्स त्रुटि: {str(e)}", exc_info=True)
        return {"error": "प्रोफाइल पार्स करने में विफल"}

def post_parse_kare(soup):
    try:
        # वीडियो या इमेज कंटेंट ढूँढें
        media_url = ""
        video_tag = soup.find('video')
        if video_tag:
            source = video_tag.find('source')
            media_url = source['src'] if source and source.get('src') else video_tag.get('src', '')
        
        # यदि वीडियो नहीं मिला तो इमेज खोजें
        if not media_url:
            img = soup.find('img', src=re.compile(r'\.(jpg|jpeg|png|gif|webp)'))
            if img and img.get('src'):
                media_url = img['src']
        
        # ओपन ग्राफ टैग से मीडिया URL
        if not media_url:
            og_video = soup.find("meta", property="og:video")
            if og_video and og_video.get("content"):
                media_url = og_video["content"]
        
        if not media_url:
            og_image = soup.find("meta", property="og:image")
            if og_image and og_image.get("content"):
                media_url = og_image["content"]
        
        # JSON डेटा से मीडिया URL
        if not media_url:
            script_tags = soup.find_all('script', type='text/javascript')
            for script in script_tags:
                if 'display_url' in script.text:
                    match = re.search(r'"display_url":"(https?://[^"]+)"', script.text)
                    if match:
                        media_url = match.group(1).replace('\\u0026', '&')
                        break
                    
                    match = re.search(r'"video_url":"(https?://[^"]+)"', script.text)
                    if match:
                        media_url = match.group(1).replace('\\u0026', '&')
                        break
        
        # कैप्शन निकालें
        caption = ""
        og_desc = soup.find("meta", property="og:description")
        twitter_desc = soup.find("meta", property="twitter:description")
        
        if og_desc and og_desc.get("content"):
            caption = og_desc["content"]
        elif twitter_desc and twitter_desc.get("content"):
            caption = twitter_desc["content"]
        
        return {
            "download_url": media_url,
            "caption": caption,
            "success": bool(media_url)
        }
    except Exception as e:
        logger.error(f"पोस्ट पार्स त्रुटि: {str(e)}", exc_info=True)
        return {"error": "पोस्ट पार्स करने में विफल"}