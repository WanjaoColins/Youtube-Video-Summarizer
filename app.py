# import the necessary libraries
from flask import Flask, render_template, request, jsonify
from langchain_community.document_loaders import YoutubeLoader
from langchain_together import ChatTogether
from langchain.prompts import PromptTemplate
from langchain.schema.runnable import RunnableSequence
import api_key
import sid
from twilio.rest import Client 

app = Flask(__name__)

# Initialize the Twilio client
twilio_account_sid = sid.sid
twilio_auth_token = sid.auth
twilio_client = Client(twilio_account_sid, twilio_auth_token)

# Initialize the language model
llm = ChatTogether(api_key=api_key.api, temperature=0.0, 
                   model="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo")

# Define the prompt template
product_description_template = PromptTemplate(
    input_variables=["video_transcript"],
    template="""
    Read through the entire transcript carefully.
           Provide a concise summary of the video's main topic and purpose.
           Extract and list the five most important points from the transcript. 
           For each point: State the key idea in a clear and concise manner.

        - Ensure your summary and key points capture the essence of the video without including unnecessary details.
        - Use clear, engaging language that is accessible to a general audience.
        - If the transcript includes any statistical data, expert opinions, or unique insights, 
        prioritize including these in your summary or key points.

    Video transcript: {video_transcript}    """
)

# Create the chain
chain = RunnableSequence(
    product_description_template | llm
)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        video_url = request.form['video_url']
        
        # Load and process the YouTube video
        loader = YoutubeLoader.from_youtube_url(video_url, add_video_info=False)
        data = loader.load()
        
        # Generate the summary
        summary = chain.invoke({
            "video_transcript": data[0].page_content
        })
        
        return render_template('result.html', summary=summary.content)
    
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)