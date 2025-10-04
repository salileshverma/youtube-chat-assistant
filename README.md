<img width="2228" height="1512" alt="Screenshot 2025-10-03 at 8 02 05 PM" src="https://github.com/user-attachments/assets/b50058ce-8961-4a72-9af9-3b336357fd21" />
<img width="1738" height="1432" alt="Screenshot 2025-10-03 at 8 02 23 PM" src="https://github.com/user-attachments/assets/abf683f1-668d-4800-9d23-b3a13c350087" />
<img width="1662" height="1430" alt="Screenshot 2025-10-03 at 8 02 43 PM" src="https://github.com/user-attachments/assets/a69d62d4-ec4f-4ea0-8af1-a044a9ea4d73" />

🎥 YouTube Transcript Chat Assistant

An interactive Streamlit app that lets you:

Fetch YouTube video transcripts automatically.

Chat with Gemini 2.5 Flash (Google Generative AI) about the video content.

Get structured, detailed answers based only on the transcript.

Perfect for summarizing, analyzing, or querying long YouTube videos with captions.

🚀 Features

✅ Extract transcripts from YouTube videos (supports normal and shortened URLs).

✅ Handles errors gracefully (e.g., no captions, disabled transcripts).

✅ Interactive Q&A interface with Gemini 2.5 Flash.

✅ Transcript preview with auto-truncation.

✅ Clear session state with one click.

✅ Works best with caption-enabled videos.

🛠️ Installation

Clone this repository:

git clone https://github.com/salileshverma/youtube-transcript-chat-assistant.git
cd youtube-transcript-chat-assistant


Create a virtual environment and activate it:

python -m venv .venv
source .venv/bin/activate   # Mac/Linux


Install dependencies:

pip install -r requirements.txt


Create a .env file in the project root and add your Google API Key:

GOOGLE_API_KEY=your_api_key_here

▶️ Usage

Run the Streamlit app:

streamlit run app.py

🔑 Requirements

Python 3.9+

Streamlit

youtube-transcript-api

langchain-google-genai

python-dotenv

🙌 Acknowledgments

Streamlit

YouTube Transcript API

Google Generative AI
