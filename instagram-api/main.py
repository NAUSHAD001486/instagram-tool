import os
from fastapi import FastAPI, HTTPException
import httpx
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential
import re

# --- सेटअप ---
load_dotenv() # .env फ़ाइल से API कीज़ लोड करेगा

app = FastAPI()

SCRAPER_API_KEY = os.getenv("SCRAPER_API_KEY")
SCRAPINGDOG_API_KEY = os.getenv("SCRAPINGDOG_API_KEY")

# --- हेल्पर फंक्शन: लिंक का प्रकार पहचानना ---
def get_link_type(url: str):
    if re.search(r"/(p|reel|tv|reels)/", url):
        return "post"
    # प्रोफाइल URL के लिए और भी बेहतर पहचान की जा सकती है
    elif re.search(r"instagram\.com/([a-zA-Z0-9_\.]+)/?$", url):
        return "profile"
    return "unknown"

# --- स्क्रैपिंग लॉजिक ---
# यह फंक्शन 2 बार रिट्राई करेगा और फिर फेल हो जाएगा
@retry(stop=stop_after_attempt(2), wait=wait_exponential(multiplier=1, min=2, max=10))
async def scrape_with_scraperapi(url: str):
    print("Trying with ScraperAPI...")
    scraper_url = f"http://api.scraperapi.com?api_key={SCRAPER_API_KEY}&url={url}"
    async with httpx.AsyncClient() as client:
        response = await client.get(scraper_url)
        response.raise_for_status() # अगर कोई एरर है तो यहीं रुक जाएगा
        return response.json() # या response.text() अगर HTML मिलता है

async def scrape_with_scrapingdog(url: str):
    print("Falling back to Scrapingdog...")
    scraper_url = f"https://api.scrapingdog.com/scrape?api_key={SCRAPINGDOG_API_KEY}&url={url}"
    async with httpx.AsyncClient() as client:
        response = await client.get(scraper_url)
        response.raise_for_status()
        return response.json() # या response.text()

# --- मुख्य API एंडपॉइंट ---
@app.post("/api/scrape")
async def scrape_instagram_url(request: dict):
    url = request.get("url")
    if not url:
        raise HTTPException(status_code=400, detail="URL is required")

    link_type = get_link_type(url)
    if link_type == "unknown":
        raise HTTPException(status_code=400, detail="Invalid Instagram URL provided")

    # TODO: स्टेप 4 में हम यहाँ Redis कैशिंग का लॉजिक जोड़ेंगे
    
    try:
        # पहले ScraperAPI से कोशिश करो
        data = await scrape_with_scraperapi(url)
    except Exception as e:
        print(f"ScraperAPI failed: {e}")
        try:
            # अगर वो फेल हो, तो Scrapingdog से कोशिश करो
            data = await scrape_with_scrapingdog(url)
        except Exception as final_e:
            print(f"Scrapingdog also failed: {final_e}")
            raise HTTPException(status_code=503, detail="Both scraping services failed. Please try again later.")

    # अभी के लिए, हम सिर्फ स्क्रैप किया हुआ डेटा लौटा रहे हैं
    # बाद में हम इसे अपने फॉर्मेट में पार्स करेंगे
    return {"link_type": link_type, "scraped_data": data}


# --- डिप्लॉयमेंट के लिए ---
# हम mangum का उपयोग अभी भी करेंगे, लेकिन उसे serverless.yml में मैनेज किया जाता है
# इसलिए यहाँ से handler हटाने से कोई फर्क नहीं पड़ता, लेकिन रखना बेहतर है
import mangum
handler = mangum.Mangum(app)