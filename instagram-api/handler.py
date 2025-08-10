import json
import os
import boto3
import time
import re
import sentry_sdk
from sentry_sdk.integrations.aws_lambda import AwsLambdaIntegration
from scraper import scrape_url

# --- Sentry और AWS सेटअप ---
SENTRY_DSN = os.environ.get('SENTRY_DSN')
TABLE_NAME = os.environ.get('DYNAMODB_TABLE_NAME')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(TABLE_NAME)

sentry_sdk.init(
    dsn=SENTRY_DSN,
    integrations=[AwsLambdaIntegration(timeout_warning=True)],
    traces_sample_rate=1.0,
    profiles_sample_rate=1.0,
)

# --- हेल्पर फंक्शन ---
def get_link_type(url: str):
    if re.search(r"/(p|reel|tv|reels)/", url):
        return "post"
    if re.search(r"instagram\.com/([a-zA-Z0-9_\.]+)/?$", url):
        return "profile"
    return "unknown"

def create_response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
        "body": json.dumps(body)
    }

# --- मुख्य लैम्ब्डा हैंडलर ---
def scrape(event, context):
    try:
        body = json.loads(event.get('body', '{}'))
        url = body.get('url')

        if not url:
            return create_response(400, {"success": False, "error": "URL is required."})

        link_type = get_link_type(url)
        if link_type == "unknown":
            return create_response(400, {"success": False, "error": "Invalid Instagram URL."})

        # 1. कैश में जांच करें
        try:
            response = table.get_item(Key={'url': url})
            if 'Item' in response and response['Item'].get('ttl', 0) > int(time.time()):
                print("Cache HIT")
                return create_response(200, json.loads(response['Item']['data']))
        except Exception as e:
            print(f"DynamoDB get_item error: {e}")
            sentry_sdk.capture_exception(e)

        print("Cache MISS")
        # 2. अगर कैश में नहीं है, तो स्क्रैप करें
        scraped_data = scrape_url(url, link_type)
        
        response_body = {"success": True, "link_type": link_type, "data": scraped_data}

        # 3. नए डेटा को कैश में डालें (40 मिनट TTL)
        try:
            ttl = int(time.time()) + (40 * 60)
            table.put_item(
                Item={
                    'url': url,
                    'data': json.dumps(response_body),
                    'ttl': ttl
                }
            )
        except Exception as e:
            print(f"DynamoDB put_item error: {e}")
            sentry_sdk.capture_exception(e)
            
        return create_response(200, response_body)

    except Exception as e:
        print(f"Unhandled error: {e}")
        sentry_sdk.capture_exception(e)
        return create_response(500, {"success": False, "error": str(e)})