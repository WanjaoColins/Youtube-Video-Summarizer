# Import necessary libraries
import os
from dotenv import load_dotenv
load_dotenv()
from flask import Flask, render_template, request
from youtube_transcript_api import YouTubeTranscriptApi
from langchain_together import ChatTogether
from langchain.prompts import PromptTemplate
from langchain.schema.runnable import RunnableSequence
from twilio.rest import Client

app = Flask(__name__)

# Initialize the Twilio client
twilio_account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
twilio_auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
twilio_client = Client(twilio_account_sid, twilio_auth_token)

# Initialize the language model
llm = ChatTogether(api_key=os.environ.get('TOGETHER_API_KEY'), temperature=0.0,
                    model="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo")

# Define the prompt template
product_description_template = PromptTemplate(
    input_variables=["video_transcript"],
    template="""Read through the entire transcript carefully. Provide a concise summary of the video's main topic and purpose.
    Extract and list the five most important points from the transcript.
    For each point: State the key idea in a clear and concise manner.
    - Ensure your summary and key points capture the essence of the video without including unnecessary details.
    - Use clear, engaging language that is accessible to a general audience.
    - If the transcript includes any statistical data, expert opinions, or unique insights,
    prioritize including these in your summary or key points.
    Video transcript: {video_transcript}"""
)

# Create the chain
chain = RunnableSequence(product_description_template | llm)

# Define the Flask route
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        video_url = request.form['video_url']
        video_id = video_url.split('v=')[-1]

        try:
            # Fetch transcript using the unofficial API
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            video_transcript = ' '.join([item['text'] for item in transcript])

            # Generate the summary using the loaded video transcript
            summary = chain.invoke({
                "video_transcript": video_transcript
            })
            return render_template('result.html', summary=summary.content)
        except Exception as e:
            print(f"Error loading video: {str(e)}")  # Log the error
            return render_template('error.html', error=f"There was an error processing your request: {str(e)}")  # Show the error
    return render_template('index.html')


# Run the app
if __name__ == '__main__':
    app.run(debug=True)
