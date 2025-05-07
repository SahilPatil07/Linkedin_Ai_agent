from flask import Flask, request, jsonify, redirect, session
from flask_cors import CORS
import requests
import json
import os
from datetime import datetime
import time
from dotenv import load_dotenv
import logging
from config import Config

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, resources={
    r"/*": {
        "origins": Config.CORS_ORIGINS,
        "supports_credentials": True
    }
})
app.secret_key = Config.FLASK_SECRET_KEY

# LinkedIn OAuth configuration
LINKEDIN_CLIENT_ID = os.getenv('LINKEDIN_CLIENT_ID')
LINKEDIN_CLIENT_SECRET = os.getenv('LINKEDIN_CLIENT_SECRET')
LINKEDIN_REDIRECT_URI = 'http://localhost:5000/auth/linkedin/callback'
LINKEDIN_SCOPE = 'r_liteprofile w_member_social'

# LinkedIn API configuration
LINKEDIN_API_URL = "https://api.linkedin.com/v2"
LINKEDIN_AUTH_URL = "https://www.linkedin.com/oauth/v2/authorization"
LINKEDIN_TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken"

# Store generated posts and scheduled posts
generated_posts = []
scheduled_posts = []

class LinkedInPoster:
    def __init__(self, access_token):
        self.access_token = access_token
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0",
            "LinkedIn-Version": "202304"
        }

    def post_to_linkedin(self, text, scheduled_time=None):
        try:
            # Get user profile
            profile_response = requests.get(
                f"{LINKEDIN_API_URL}/me",
                headers=self.headers
            )
            
            if profile_response.status_code != 200:
                return {
                    "success": False,
                    "error": f"Failed to get profile: {profile_response.text}"
                }

            profile_data = profile_response.json()
            author_id = profile_data.get("id")

            # Prepare the post data
            post_data = {
                "author": f"urn:li:person:{author_id}",
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {
                            "text": text
                        },
                        "shareMediaCategory": "NONE"
                    }
                },
                "visibility": {
                    "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
                }
            }

            # If scheduled time is provided, add scheduling parameters
            if scheduled_time:
                post_data["scheduledTime"] = int(scheduled_time.timestamp() * 1000)  # Convert to milliseconds

            # Make the post request
            response = requests.post(
                f"{LINKEDIN_API_URL}/ugcPosts",
                headers=self.headers,
                json=post_data
            )

            if response.status_code == 201:
                return {
                    "success": True,
                    "message": "Post scheduled successfully" if scheduled_time else "Post published successfully",
                    "post_id": response.headers.get("x-restli-id")
                }
            else:
                return {
                    "success": False,
                    "error": f"LinkedIn API error: {response.text}"
                }

        except Exception as e:
            return {
                "success": False,
                "error": f"Error posting to LinkedIn: {str(e)}"
            }

@app.route('/auth/linkedin')
def linkedin_auth():
    """Initiate LinkedIn OAuth flow"""
    try:
        auth_url = f"https://www.linkedin.com/oauth/v2/authorization?response_type=code&client_id={Config.LINKEDIN_CLIENT_ID}&redirect_uri={Config.LINKEDIN_REDIRECT_URI}&scope=w_member_social"
        return redirect(auth_url)
    except Exception as e:
        logger.error(f"LinkedIn auth error: {str(e)}")
        return jsonify({"error": "Authentication failed"}), 500

@app.route('/auth/linkedin/callback')
def linkedin_callback():
    """Handle LinkedIn OAuth callback"""
    try:
        code = request.args.get('code')
        if not code:
            return jsonify({"error": "No code provided"}), 400

        # Exchange code for access token
        token_url = "https://www.linkedin.com/oauth/v2/accessToken"
        data = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': Config.LINKEDIN_REDIRECT_URI,
            'client_id': Config.LINKEDIN_CLIENT_ID,
            'client_secret': Config.LINKEDIN_CLIENT_SECRET
        }
        
        response = requests.post(token_url, data=data)
        if response.status_code != 200:
            logger.error(f"Token exchange failed: {response.text}")
            return jsonify({"error": "Token exchange failed"}), 500

        token_data = response.json()
        session['access_token'] = token_data.get('access_token')
        
        return redirect('http://localhost:3000')
    except Exception as e:
        logger.error(f"Callback error: {str(e)}")
        return jsonify({"error": "Callback processing failed"}), 500

@app.route('/api/post', methods=['POST'])
def create_post():
    """Create a LinkedIn post"""
    try:
        if 'access_token' not in session:
            return jsonify({"error": "Not authenticated"}), 401

        data = request.json
        if not data or 'text' not in data:
            return jsonify({"error": "No text provided"}), 400

        # Get user profile
        profile_url = "https://api.linkedin.com/v2/me"
        headers = {
            'Authorization': f'Bearer {session["access_token"]}',
            'X-Restli-Protocol-Version': '2.0.0'
        }
        
        profile_response = requests.get(profile_url, headers=headers)
        if profile_response.status_code != 200:
            logger.error(f"Profile fetch failed: {profile_response.text}")
            return jsonify({"error": "Failed to fetch profile"}), 500

        profile_data = profile_response.json()
        author_id = f"urn:li:person:{profile_data['id']}"

        # Create post
        post_url = "https://api.linkedin.com/v2/ugcPosts"
        post_data = {
            "author": author_id,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": data['text']
                    },
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            }
        }

        post_response = requests.post(
            post_url,
            headers=headers,
            json=post_data
        )

        if post_response.status_code not in (200, 201):
            logger.error(f"Post creation failed: {post_response.text}")
            return jsonify({"error": "Failed to create post"}), 500

        return jsonify({"message": "Post created successfully"})
    except Exception as e:
        logger.error(f"Post creation error: {str(e)}")
        return jsonify({"error": "Post creation failed"}), 500

@app.route('/api/logout')
def logout():
    """Clear session and logout"""
    session.clear()
    return jsonify({"message": "Logged out successfully"})

@app.route('/api/store-posts', methods=['POST'])
def store_posts():
    try:
        data = request.json
        posts = data.get('posts', [])
        
        if not posts:
            return jsonify({"error": "No posts provided"}), 400

        # Store the generated posts
        global generated_posts
        generated_posts = posts

        return jsonify({
            "message": f"Stored {len(posts)} posts successfully",
            "posts": posts
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/get-posts', methods=['GET'])
def get_posts():
    return jsonify({
        "posts": generated_posts
    })

@app.route('/api/schedule-post', methods=['POST'])
def schedule_post():
    try:
        data = request.json
        post_index = data.get('postIndex')
        scheduled_time = data.get('scheduledTime')
        
        if post_index is None or not scheduled_time:
            return jsonify({"error": "Missing required fields"}), 400

        if post_index >= len(generated_posts):
            return jsonify({"error": "Invalid post index"}), 400

        # Convert scheduled time to datetime
        scheduled_datetime = datetime.fromisoformat(scheduled_time.replace('Z', '+00:00'))
        
        # Store the scheduled post
        scheduled_posts.append({
            "post": generated_posts[post_index],
            "scheduledTime": scheduled_datetime,
            "status": "scheduled"
        })

        return jsonify({
            "message": "Post scheduled successfully",
            "scheduledTime": scheduled_time,
            "post": generated_posts[post_index]
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/get-scheduled-posts', methods=['GET'])
def get_scheduled_posts():
    return jsonify({
        "scheduled_posts": scheduled_posts
    })

if __name__ == '__main__':
    logger.info(f"Starting Flask server on port {Config.FLASK_PORT}...")
    app.run(host='0.0.0.0', port=Config.FLASK_PORT, debug=True) 