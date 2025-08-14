import os
import sys
import logging
import json
import boto3
import time
import re
import datetime
import traceback

# ======= प्रारंभिक डायग्नोस्टिक लॉगिंग =======
# अस्थायी लॉगर सेटअप (बेसिक)
temp_logger = logging.getLogger()
temp_logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
temp_logger.addHandler(handler)

# महत्वपूर्ण डायग्नोस्टिक जानकारी लॉग करें
temp_logger.info("="*50)
temp_logger.info("Lambda initialization started")
temp_logger.info(f"Python version: {sys.version}")
temp_logger.info(f"Current directory: {os.getcwd()}")
temp_logger.info(f"Files in directory: {os.listdir('.')}")
temp_logger.info(f"Environment variables: {dict(os.environ)}")
temp_logger.info("="*50)

# ======= उन्नत लॉगिंग सेटअप =======
# मुख्य लॉगर कॉन्फ़िगरेशन
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# JSON प्रारूप में लॉगिंग
class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "message": record.getMessage(),
            "service": "instagram-scraper",
            "aws_region": os.environ.get('AWS_REGION', 'ap-south-1'),
            "function_name": record.funcName if hasattr(record, 'funcName') else "",
            "line_number": record.lineno if hasattr(record, 'lineno') else ""
        }
        if hasattr(record, 'exc_info') and record.exc_info:
            log_data["exception"] = traceback.format_exception(*record.exc_info)
        return json.dumps(log_data)

# हैंडलर कॉन्फ़िगर करें
if logger.hasHandlers():
    logger.handlers.clear()
    
handler = logging.StreamHandler()
handler.setFormatter(JsonFormatter())
logger.addHandler(handler)

logger.info("Advanced logger setup completed")

# ======= AWS संसाधन सेटअप =======
TABLE_NAME = os.environ.get('DYNAMODB_TABLE_NAME')
dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
table = dynamodb.Table(TABLE_NAME)
logger.info(f"DynamoDB table configured: {TABLE_NAME}")

# ======= सशक्त स्क्रैपर आयात =======
SCRAPER_LOADED = False
try:
    from scraper import scrape_url
    SCRAPER_LOADED = True
    logger.info("Scraper module loaded successfully")
except ImportError as e:
    logger.error(f"Scraper import error: {str(e)}")
    logger.error(f"Import path: {os.path.abspath('.')}")
    logger.error(f"Files in directory: {', '.join(os.listdir('.'))}")

# ======= सहायक कार्य =======
def get_link_type(url: str):
    """URL के प्रकार का निर्धारण करें (प्रोफाइल या पोस्ट)"""
    if not isinstance(url, str) or not url:
        return "unknown"
        
    clean_url = url.strip().lower()
    if 'instagram.com' not in clean_url:
        return "unknown"
        
    # प्रोफाइल या पोस्ट की जाँच करें
    if re.search(r"instagram\.com/([a-zA-Z0-9_\.]+)/?", clean_url):
        if re.search(r"/(p|reel|tv|reels)/", clean_url):
            return "post"
        else:
            return "profile"
    return "unknown"

def create_response(status_code, body):
    """एक समान प्रतिक्रिया संरचना बनाएँ"""
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "X-Scrape-Success": "true" if body.get("success") else "false"
        },
        "body": json.dumps(body, default=str)
    }

# ======= मुख्य लैम्ब्डा हैंडलर =======
def scrape(event, context):
    # लैम्ब्डा निष्पादन शुरू होने का लॉग
    start_time = time.time()
    logger.info("Lambda execution started", extra={
        "function_name": context.function_name,
        "memory_limit": context.memory_limit_in_mb,
        "request_id": context.aws_request_id,
        "event": event
    })
    
    try:
        # इवेंट बॉडी को पार्स करें
        body = {}
        if 'body' in event and event['body']:
            try:
                body = json.loads(event['body'])
                logger.info(f"Request body: {body}")
            except json.JSONDecodeError as e:
                error_msg = "Invalid JSON format in request body"
                logger.error(error_msg, extra={
                    "body_content": event.get('body', ''),
                    "error": str(e)
                })
                return create_response(400, {
                    "success": False,
                    "error": error_msg
                })
        
        url = body.get('url', '').strip()
        logger.info(f"Processing URL: {url}")

        # URL सत्यापन
        if not url:
            logger.warning("URL not provided in request")
            return create_response(400, {
                "success": False,
                "error": "URL is required",
                "example": "https://www.instagram.com/p/Cx45fXfN8QZ/"
            })
        
        # URL प्रकार निर्धारित करें
        link_type = get_link_type(url)
        if link_type == "unknown":
            logger.warning(f"Unsupported URL type: {url}")
            return create_response(400, {
                "success": False,
                "error": "Unsupported Instagram URL",
                "supported_types": ["Profile URLs", "Post/Reel URLs"]
            })
        
        logger.info(f"URL type identified: {link_type}")

        # ======= कैश प्रबंधन =======
        cache_key = f"{link_type}:{url}"
        cache_hit = False
        cached_data = None
        
        try:
            # कैश से डेटा प्राप्त करें
            response = table.get_item(Key={'url': cache_key})
            if 'Item' in response:
                item = response['Item']
                current_time = int(time.time())
                item_ttl = item.get('ttl', 0)
                
                if isinstance(item_ttl, int) and item_ttl > current_time:
                    logger.info("Cache hit", extra={"url": url})
                    cache_hit = True
                    cached_data = json.loads(item['data'])
                else:
                    logger.info("Cache expired", extra={
                        "url": url,
                        "ttl": item_ttl,
                        "current_time": current_time
                    })
        except Exception as e:
            logger.error(f"DynamoDB cache read error: {str(e)}")

        # कैश हिट होने पर प्रतिक्रिया दें
        if cache_hit and cached_data:
            cached_data['cache_status'] = "hit"
            return create_response(200, cached_data)

        logger.info("Cache miss - starting scraping")
        
        # ======= स्क्रैपिंग प्रक्रिया =======
        scraped_data = None
        if not SCRAPER_LOADED:
            logger.error("Scraper module not available")
            return create_response(500, {
                "success": False,
                "error": "Internal server error - scraper module missing"
            })
        
        try:
            scraped_data = scrape_url(url, link_type)
            logger.info("Scraping completed successfully", extra={"data": scraped_data})
        except Exception as e:
            error_msg = f"Scraping failed: {str(e)}"
            logger.error(error_msg, extra={
                "url": url,
                "link_type": link_type,
                "traceback": traceback.format_exc()
            })
            return create_response(500, {
                "success": False,
                "error": "Scraping service unavailable",
                "retry_suggested": True,
                "details": error_msg
            })
        
        # प्रतिक्रिया तैयार करें
        response_body = {
            "success": True,
            "link_type": link_type,
            "data": scraped_data,
            "cache_status": "miss"
        }

        # ======= कैश में डेटा सहेजें =======
        try:
            ttl = int(time.time()) + (60 * 60)  # 1 घंटे के लिए कैश
            table.put_item(Item={
                'url': cache_key,
                'data': json.dumps(response_body),
                'ttl': ttl
            })
            logger.info("Data cached successfully", extra={"ttl": ttl})
        except Exception as e:
            logger.error(f"Cache write error: {str(e)}")
        
        # सफल प्रतिक्रिया लौटाएं
        end_time = time.time()
        duration = round(end_time - start_time, 2)
        logger.info("Request processed successfully", extra={
            "duration_sec": duration,
            "url": url
        })
        
        return create_response(200, response_body)

    except Exception as e:
        # अप्रत्याशित त्रुटियों को संभालें
        error_msg = f"Unhandled exception: {str(e)}"
        logger.critical(error_msg, extra={
            "traceback": traceback.format_exc(),
            "event": event
        })
        return create_response(500, {
            "success": False,
            "error": "Internal server error",
            "reference_id": context.aws_request_id,
            "details": error_msg
        })