import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/test_youtube', methods=['GET'])
def test_youtube_connection():
    try:
        # Test a simple GET request to YouTube
        response = requests.get('https://www.youtube.com')
        if response.status_code == 200:
            return jsonify({"message": "Connection to YouTube is successful!"}), 200
        else:
            return jsonify({"message": f"Failed to connect to YouTube, status code: {response.status_code}"}), 500
    except Exception as e:
        return jsonify({"message": f"Error: {e}"}), 500

if __name__ == "__main__":
    app.run(debug=True)


"""
import os
from flask import Flask, request, jsonify, render_template
from urllib.parse import urlparse, parse_qs
from youtube_transcript_api import YouTubeTranscriptApi
from langchain_together import ChatTogether
from langchain.prompts import PromptTemplate
from langchain.schema.runnable import RunnableSequence
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
from dotenv import load_dotenv

load_dotenv()  # This loads the variables from .env file

app = Flask(__name__)

# Initialize clients and models
twilio_client = Client(os.environ.get('TWILIO_ACCOUNT_SID'), os.environ.get('TWILIO_AUTH_TOKEN'))
llm = ChatTogether(api_key=os.environ.get('TOGETHER_API_KEY'), temperature=0.0,
                   model="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo")
"""
"""
# Define the prompt template
SUMMARY_TEMPLATE = """Read through the entire transcript carefully. Provide a concise summary of the video's main topic and purpose.
Extract and list the five most important points from the transcript.
For each point: State the key idea in a clear and concise manner.
- Ensure your summary and key points capture the essence of the video without including unnecessary details.
- Use clear, engaging language that is accessible to a general audience.
- If the transcript includes any statistical data, expert opinions, or unique insights,
prioritize including these in your summary or key points.
Video transcript: {video_transcript}"""

"""

"""
product_description_template = PromptTemplate(
    input_variables=["video_transcript"],
    template=SUMMARY_TEMPLATE
)

# Create the chain
chain = RunnableSequence(product_description_template | llm)

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
    return YouTubeTranscriptApi.get_transcript(video_id)

def generate_summary(video_url):
    video_id = extract_video_id(video_url)
    if not video_id:
        return "Invalid YouTube URL."
    try:
        transcript = fetch_transcript(video_id)
        video_transcript = ' '.join([item['text'] for item in transcript])
        summary = chain.invoke({"video_transcript": video_transcript})
        return summary.content
    except Exception as e:
        print(f"Error processing video: {str(e)}")
        return f"Error processing video: {str(e)}"

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        video_url = request.form['video_url']
        summary = generate_summary(video_url)
        return render_template('result.html', summary=summary)
    return render_template('index.html')

@app.route('/send-message', methods=['POST'])
def send_message():
    data = request.json
    to_number = data.get('to_number')
    message = data.get('message')
    if not to_number or not message:
        return jsonify({"status": "error", "message": "Missing 'to_number' or 'message'"}), 400
    try:
        message = twilio_client.messages.create(
            body=message,
            from_='whatsapp:+14155238886',
            to=f'whatsapp:{to_number}'
        )
        return jsonify({"status": "success", "sid": message.sid}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/whatsapp', methods=['POST'])
def whatsapp_webhook():
    incoming_msg = request.values.get('Body', '').lower()
    resp = MessagingResponse()
    msg = resp.message()
    if incoming_msg.startswith(('https://www.youtube.com/', 'https://youtu.be/')):
        summary = generate_summary(incoming_msg)
        msg.body(summary)
    else:
        msg.body("Please send a valid YouTube URL.")
    return str(resp)

if __name__ == '__main__':
    app.run(debug=True)

"""