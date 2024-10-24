import os
from flask import Flask, request, jsonify, render_template
from urllib.parse import urlparse, parse_qs
from youtube_transcript_api import YouTubeTranscriptApi
from langchain_together import ChatTogether
from langchain.prompts import PromptTemplate
from langchain.schema.runnable import RunnableSequence
from dotenv import load_dotenv
import requests

# Load environment variables from the .env file
load_dotenv()

app = Flask(__name__)

# Initialize LLM model
llm = ChatTogether(api_key=os.environ.get('TOGETHER_API_KEY'), temperature=0.0,
                   model="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo")

# Define the prompt template
SUMMARY_TEMPLATE = """
Read through the entire transcript carefully. Provide a concise summary of the video's main topic and purpose.
Extract and list the five most important points from the transcript.
For each point: State the key idea in a clear and concise manner.
- Ensure your summary and key points capture the essence of the video without including unnecessary details.
- Use clear, engaging language that is accessible to a general audience.
- If the transcript includes any statistical data, expert opinions, or unique insights,
prioritize including these in your summary or key points.
Video transcript: {video_transcript}
"""

product_description_template = PromptTemplate(
    input_variables=["video_transcript"],
    template=SUMMARY_TEMPLATE
)

# Create the chain
chain = RunnableSequence(product_description_template | llm)

# Telegram Bot API token
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

def extract_video_id(url):
    parsed_url = urlparse(url)
    
    if parsed_url.hostname in ['youtu.be']:
        return parsed_url.path[1:]
    if parsed_url.hostname in ['www.youtube.com', 'youtube.com']:
        if parsed_url.path == '/watch':
            return parse_qs(parsed_url.query).get('v', [None])[0]
        if parsed_url.path.startswith(('/embed/', '/v/', '/live/')):
            return parsed_url.path.split('/')[2]
    return None

def fetch_transcript(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return ' '.join([item['text'] for item in transcript])
    except Exception as e:
        print(f"Error fetching transcript: {str(e)}")
        return None

def generate_summary(video_url):
    video_id = extract_video_id(video_url)
    if not video_id:
        return "Invalid YouTube URL."
    try:
        transcript = fetch_transcript(video_id)  # Fetch the transcript
        if transcript is None:
            return "Could not fetch the transcript."
        
        summary = chain.invoke({"video_transcript": transcript})
        # Ensure no extra "Summary" heading is included
        return summary.content.replace("Summary:", "").strip()
    except Exception as e:
        print(f"Error processing video: {str(e)}")  # Log error for debugging
        return f"Error processing video: {str(e)}"

def send_telegram_message(chat_id, text):
    """Send a message to the user via Telegram."""
    url = f"{TELEGRAM_API_URL}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': text
    }
    response = requests.post(url, json=payload)
    return response

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        video_url = request.form['video_url']
        summary = generate_summary(video_url)
        return render_template('result.html', summary=summary)
    return render_template('index.html')

@app.route('/telegram-webhook', methods=['POST'])
def telegram_webhook():
    """Handle incoming Telegram messages."""
    data = request.get_json()

    if 'message' in data:
        chat_id = data['message']['chat']['id']
        text = data['message'].get('text', '').strip().lower()

        if text.startswith(('https://www.youtube.com/', 'https://youtu.be/')):
            summary = generate_summary(text)
            send_telegram_message(chat_id, summary)
        else:
            send_telegram_message(chat_id, "Please send a valid YouTube URL.")

    return '', 200

if __name__ == '__main__':
    app.run(debug=True)