import os
import sys
import logging
import json
import boto3
import time
import re
import datetime
import traceback
import requests

# ======= प्रारंभिक डायग्नोस्टिक लॉगिंग =======
temp_logger = logging.getLogger()
temp_logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
temp_logger.addHandler(handler)

# ======= उन्नत लॉगिंग सेटअप =======
logger = logging.getLogger()
logger.setLevel(logging.INFO)

if logger.hasHandlers():
    logger.handlers.clear()
    
handler = logging.StreamHandler()
logger.addHandler(handler)

# ======= AWS संसाधन सेटअप =======
TABLE_NAME = os.environ.get('DYNAMODB_TABLE_NAME')
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table(TABLE_NAME)

# ======= सहायक कार्य =======
def get_link_type(url: str):
    if not isinstance(url, str) or not url:
        return "unknown"
        
    clean_url = url.strip().lower()
    if 'instagram.com' not in clean_url:
        return "unknown"
        
    if re.search(r"instagram\.com/([a-zA-Z0-9_\.]+)/?", clean_url):
        if re.search(r"/(p|reel|tv|reels)/", clean_url):
            return "post"
        else:
            return "profile"
    return "unknown"

def create_response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "X-Scrape-Success": "true" if body.get("success") else "false"
        },
        "body": json.dumps(body, default=str)
    }

# ======= इंटरनेट कनेक्टिविटी चेक =======
def check_internet():
    try:
        response = requests.get("https://www.google.com", timeout=5)
        return response.status_code == 200
    except:
        return False

# ======= मुख्य लैम्ब्डा हैंडलर =======
def scrape(event, context):
    start_time = time.time()
    logger.info("Lambda execution started")
    
    # इंटरनेट कनेक्टिविटी चेक
    if not check_internet():
        logger.error("No internet access from Lambda function")
        return create_response(500, {
            "success": False,
            "error": "Lambda function has no internet access"
        })
    
    try:
        body = {}
        if 'body' in event and event['body']:
            try:
                body = json.loads(event['body'])
            except json.JSONDecodeError as e:
                return create_response(400, {
                    "success": False,
                    "error": "Invalid JSON format"
                })
        
        url = body.get('url', '').strip()
        if not url:
            return create_response(400, {
                "success": False,
                "error": "URL is required"
            })
        
        link_type = get_link_type(url)
        if link_type == "unknown":
            return create_response(400, {
                "success": False,
                "error": "Unsupported Instagram URL"
            })
        
        logger.info(f"Processing URL: {url} ({link_type})")
        
        # कैश प्रबंधन
        cache_key = f"{link_type}:{url}"
        cache_hit = False
        
        try:
            response = table.get_item(Key={'url': cache_key})
            if 'Item' in response:
                item = response['Item']
                current_time = int(time.time())
                item_ttl = item.get('ttl', 0)
                
                if item_ttl > current_time:
                    logger.info("Cache hit")
                    cache_hit = True
                    cached_data = json.loads(item['data'])
        except Exception as e:
            logger.error(f"DynamoDB error: {str(e)}")
        
        if cache_hit:
            return create_response(200, cached_data)
        
        logger.info("Cache miss - scraping")
        
        # स्क्रैपिंग प्रक्रिया
        try:
            from scraper import scrape_url
            scraped_data = scrape_url(url, link_type)
        except ImportError as e:
            logger.error(f"Scraper import error: {str(e)}")
            return create_response(500, {
                "success": False,
                "error": "Internal server error"
            })
        except Exception as e:
            logger.error(f"Scraping error: {str(e)}")
            return create_response(500, {
                "success": False,
                "error": "Scraping service unavailable",
                "details": str(e)
            })
        
        response_body = {
            "success": True,
            "link_type": link_type,
            "data": scraped_data,
            "cache_status": "miss"
        }

        # कैश में डेटा सहेजें
        try:
            ttl = int(time.time()) + 3600  # 1 घंटा
            table.put_item(Item={
                'url': cache_key,
                'data': json.dumps(response_body),
                'ttl': ttl
            })
        except Exception as e:
            logger.error(f"Cache save error: {str(e)}")
        
        return create_response(200, response_body)

    except Exception as e:
        logger.error(f"Unhandled exception: {str(e)}")
        return create_response(500, {
            "success": False,
            "error": "Internal server error",
            "details": traceback.format_exc()
        })