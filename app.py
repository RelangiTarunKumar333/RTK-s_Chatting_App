import os
from flask import Flask, request, jsonify, render_template
from groq import Groq
from dotenv import load_dotenv
import requests

# Load environment variables from .env file
load_dotenv()
groq_api_key = os.getenv('GROQ_API_KEY')

# Set the API key for Groq
os.environ['GROQ_API_KEY'] = groq_api_key

app = Flask(__name__)

client = Groq()

def fetch_image(query):
    unsplash_access_key = os.getenv('UNSPLASH_ACCESS_KEY')  # Ensure you have the key in your .env file
    response = requests.get(f"https://api.unsplash.com/search/photos?query={query}&client_id={unsplash_access_key}")
    data = response.json()
    if data['results']:
        img_url = data['results'][0]['urls']['regular']
        return img_url
    return None

def fetch_video(query):
    youtube_api_key = os.getenv('YOUTUBE_API_KEY')  # Ensure you have the key in your .env file
    search_url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={query}&key={youtube_api_key}&type=video&maxResults=1"
    response = requests.get(search_url)
    data = response.json()
    if data['items']:
        video_id = data['items'][0]['id']['videoId']
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        return video_url
    return None

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get("message")
    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": user_message,
                }
            ],
            model="llama3-8b-8192",
        )
        bot_message = chat_completion.choices[0].message.content

        image_url = fetch_image(user_message)
        video_url = fetch_video(user_message)

        response = {"message": bot_message}
        if image_url:
            response["image_url"] = image_url
        if video_url:
            response["video_url"] = video_url

        return jsonify(response)
    except Exception as e:
        return jsonify({"error": f"Unable to get response from Groq API. {e}"}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)
