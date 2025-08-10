import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware # <<< इसे इम्पोर्ट करें
import httpx
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential
import re
import mangum

# --- सेटअप ---
load_dotenv()
app = FastAPI()

# === यहाँ बदलाव किया गया है: CORS को सक्षम करें ===
# हम सभी स्रोतों से आने वाले अनुरोधों को अनुमति दे रहे हैं
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # आप इसे और सुरक्षित बनाने के लिए बाद में अपनी Vercel URL डाल सकते हैं
    allow_credentials=True,
    allow_methods=["*"],  # सभी मेथड्स (GET, POST, आदि) को अनुमति दें
    allow_headers=["*"],  # सभी हेडर्स को अनुमति दें
)

SCRAPER_API_KEY = os.getenv("SCRAPER_API_KEY")
SCRAPINGDOG_API_KEY = os.getenv("SCRAPINGDOG_API_KEY")

def get_link_type(url: str):
    if re.search(r"/(p|reel|tv|reels)/", url):
        return "post"
    elif re.search(r"instagram\.com/([a-zA-Z0-9_\.]+)/?$", url):
        return "profile"
    return "unknown"

@retry(stop=stop_after_attempt(2), wait=wait_exponential(multiplier=1, min=2, max=10))
async def scrape_with_scraperapi(url: str):
    print("Trying with ScraperAPI...")
    scraper_url = f"http://api.scraperapi.com?api_key={SCRAPER_API_KEY}&url={url}"
    async with httpx.AsyncClient() as client:
        response = await client.get(scraper_url, timeout=30.0) # टाइमआउट जोड़ें
        response.raise_for_status()
        # यह मानते हुए कि API हमेशा JSON लौटाता है, अगर नहीं तो इसे बदलना होगा
        return response.json()

async def scrape_with_scrapingdog(url: str):
    print("Falling back to Scrapingdog...")
    scraper_url = f"https://api.scrapingdog.com/scrape?api_key={SCRAPINGDOG_API_KEY}&url={url}"
    async with httpx.AsyncClient() as client:
        response = await client.get(scraper_url, timeout=30.0) # टाइमआउट जोड़ें
        response.raise_for_status()
        return response.json()

@app.post("/api/scrape")
async def scrape_instagram_url(request: dict):
    url = request.get("url")
    if not url:
        raise HTTPException(status_code=400, detail="URL is required")

    link_type = get_link_type(url)
    if link_type == "unknown":
        raise HTTPException(status_code=400, detail="Invalid Instagram URL provided")

    # TODO: कैशिंग लॉजिक यहाँ आएगा

    try:
        # अभी के लिए, हम सिर्फ एक डमी प्रतिक्रिया भेज रहे हैं यह जांचने के लिए कि कनेक्शन काम कर रहा है
        print(f"Received request for {url} of type {link_type}")
        return {
            "link_type": link_type,
            "message": "Connection Successful! Scraping logic will be here."
        }
        
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        raise HTTPException(status_code=500, detail="An internal error occurred.")

handler = mangum.Mangum(app)