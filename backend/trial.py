import requests
import json

# --- Configuration ---
ACCESS_TOKEN = "AQUc36_AmDQOrCvSzgET0CQvZikD-Df0P8kR190DBnYZA_5ZIxsZc-pzo0wa6wc0pZXB5t2h6EACF8Dct5cHEoSOH-SxgKUQjlnrprxDS6wlLe6AKXVNfB0ooFEkKki0tGhK83VpyULOS4ZG8f71DBUc5CuYGAsbZD0pGCF0iVUKPu-Dyyj2OlcT78XEFEHcOWnOi6NSesUbi1MS1DTffmzEmxKx_fTpCKFwv1d4O0Xss2_Tk5aGsOECAD498202DRm0lb6gl1OXWHlI4E8gFvIFRdUU56WBGW1GjEJna99WOqWe38xiIEEZEv6emDw-d8Ly7997-moDSZRZ5337pt2KN-lv8A"


ORGANIZATION_ID = "107281847"
POST_TEXT = "🚀 Hello World! This post was made using the LinkedIn API."

# LinkedIn API endpoint
API_URL = "https://api.linkedin.com/rest/posts"

# Construct author URN
author_urn = f"urn:li:organization:{ORGANIZATION_ID}"

# Headers
headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json",
    "X-Restli-Protocol-Version": "2.0.0",
    "LinkedIn-Version": "202405"
}

# Post content
post_data = {
    "author": author_urn,
    "commentary": POST_TEXT,
    "visibility": "PUBLIC",
    "distribution": {
        "feedDistribution": "MAIN_FEED",
        "targetEntities": [],
        "thirdPartyDistributionChannels": []
    },
    "lifecycleState": "PUBLISHED",
    "isReshareDisabledByAuthor": False
}

# --- Make the POST Request ---
try:
    response = requests.post(API_URL, headers=headers, json=post_data)
    response.raise_for_status()

    print("✅ Post successfully created!")
    print(f"Status Code: {response.status_code}")

    if 'x-restli-id' in response.headers:
        print(f"🔗 Post URN: {response.headers['x-restli-id']}")
    if response.content:
        try:
            print("📦 Response JSON:", response.json())
        except json.JSONDecodeError:
            print("📄 Response Text:", response.text)

except requests.exceptions.HTTPError as http_err:
    print("❌ HTTP error occurred:", http_err)
    print("🔢 Status Code:", http_err.response.status_code)
    try:
        print("📄 Response JSON:", http_err.response.json())
    except json.JSONDecodeError:
        print("📄 Response Text:", http_err.response.text)

except Exception as e:
    print("❌ An unexpected error occurred:", e)
