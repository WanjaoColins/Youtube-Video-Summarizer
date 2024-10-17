import os
from flask import Flask, request, jsonify, render_template
from googleapiclient.discovery import build
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

# Initialize YouTube API client
YOUTUBE_API_KEY = os.environ.get('YOUTUBE_API_KEY')
if not YOUTUBE_API_KEY:
    print("Error: YouTube API key is not set.")
else:
    youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

# Define the prompt template
SUMMARY_TEMPLATE = """Provide a concise summary of the video's main topic and purpose based on the following information:
Title: {title}
Description: {description}
Extract and list the five most important points from the information provided.
For each point: State the key idea in a clear and concise manner.
- Ensure your summary and key points capture the essence of the video without including unnecessary details.
- Use clear, engaging language that is accessible to a general audience.
- If the information includes any statistical data, expert opinions, or unique insights, prioritize including these in your summary or key points."""

product_description_template = PromptTemplate(
    input_variables=["title", "description"],
    template=SUMMARY_TEMPLATE
)

# Create the chain
chain = RunnableSequence(product_description_template | llm)

def extract_video_id(url):
    if 'youtu.be' in url:
        return url.split('/')[-1]
    elif 'youtube.com' in url:
        if 'v=' in url:
            return url.split('v=')[1].split('&')[0]
        elif 'embed/' in url:
            return url.split('embed/')[-1].split('?')[0]
    return None

def fetch_video_info(video_id):
    try:
        request = youtube.videos().list(
            part="snippet",
            id=video_id
        )
        response = request.execute()
        
        if 'items' in response and len(response['items']) > 0:
            snippet = response['items'][0]['snippet']
            return {
                'title': snippet['title'],
                'description': snippet['description']
            }
        else:
            print(f"No items found for video ID: {video_id}")
            return None
    except Exception as e:
        print(f"Error fetching video info: {str(e)}")
        return None

def generate_summary(video_url):
    video_id = extract_video_id(video_url)
    if not video_id:
        return "Invalid YouTube URL."
    
    video_info = fetch_video_info(video_id)
    if not video_info:
        return "Unable to fetch video information."
    
    try:
        summary = chain.invoke({
            "title": video_info['title'],
            "description": video_info['description']
        })
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
