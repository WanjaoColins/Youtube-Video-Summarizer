# YouTube Video Summarizer

## Goal
The YouTube Video Summarizer is designed to streamline the process of extracting essential information from YouTube videos, saving users valuable time. Instead of watching long videos, users can quickly grasp the main points through concise summaries. This tool is ideal for students, researchers, and professionals who need to consume information efficiently.

## Features
- Extracts and summarizes YouTube video content.
- Simple, user-friendly interface for inputting YouTube URLs.
- Generates concise summaries of the video's core message and key points.
- Deployed with Ngrok for local testing and webhook setup.

## Tech Stack
This project leverages a combination of powerful tools and libraries to achieve its functionality:

- **Langchain**: Utilized for handling the summarization logic. It allows the creation of pipelines (chains) to process video transcripts and produce structured summaries.
- **TogetherAPI**: Powers the language model that summarizes the transcripts, providing accurate and coherent results.
- **Flask Web Framework**: A lightweight framework used for building the web interface and backend logic to process requests and handle video URL input.
- **Ngrok**: Used for tunneling local applications to the web, allowing public access for webhook integration.

## How It Works
1. **User Input**: The user enters a YouTube URL on the web interface.
2. **Transcript Extraction**: The video ID is extracted, and the YouTube API is used to retrieve the video's transcript.
3. **Summarization**: The transcript is passed to Langchain and TogetherAPI, where it's summarized using a Large Language Model.
4. **Display**: The summary is presented back to the user on a results page, highlighting key points from the video.

## Installation and Setup
Follow these steps to set up the project on your local machine:

### Prerequisites
Ensure you have the following installed:
- Python 3.8+
- Flask
- Ngrok (optional for local testing)
- TogetherAPI account (for generating API keys)

### 1. Clone the Repository
```bash
git clone https://github.com/WanjaoColins/youtube-video-summarizer.git
cd youtube-video-summarizer
```

### 2. Install Required Packages
```bash
pip install -r requirements.txt
```

### 3. Environment Variables
Create a .env file in the project root to store your API keys. Add the following:

- TOGETHER_API_KEY=your_together_api_key
- RAPIDAPI_KEY=your_rapidapi_key

### 4. Run Flask Locally
```bash
python app.py
```

The app will be hosted at http://localhost:5000.

### 5. Using Ngrok (Optional)
To expose your local Flask app to the web for testing, use Ngrok. First, install and run Ngrok:

```bash
ngrok http 5000
```

This will generate a public-facing URL you can use to test the web app from anywhere.

## Key Components
app.py: The main Flask application responsible for handling requests and rendering pages.
youtube_transcript_api: Python library that handles fetching transcripts from YouTube videos
templates/: Contains the HTML files for the web interface.
.env: Stores API keys and other sensitive configuration values.

## Future Enhancements
Add support for multi-language transcripts.
Improve error handling and edge case management.
Integrate more advanced NLP models for even more accurate summaries.
Enhance the UI with additional video information, like metadata and thumbnails.

## License
This project is licensed under the MIT License. Feel free to contribute or modify the project to fit your needs.