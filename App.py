import os
import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

# Configuration

load_dotenv()

# Verify API key is loaded
if not os.getenv("GOOGLE_API_KEY"):
    st.error("⚠️ GOOGLE_API_KEY not found! Please set it in your .env file.")
    st.stop()

st.set_page_config(page_title="YouTube Transcript Chat Assistant", page_icon="🎥")
st.title("🎥 YouTube Transcript Chat Assistant")
st.markdown("Ask Questions related to Youtube Video")
st.markdown("---")

# Initialize session state
if 'transcript_text' not in st.session_state:
    st.session_state.transcript_text = ""
if 'video_title' not in st.session_state:
    st.session_state.video_title = ""

# -------------------------
# Step 1: Get YouTube Transcript
# -------------------------
st.subheader("1️⃣ Load YouTube Video")
video_url = st.text_input("Enter YouTube Video URL:", placeholder="https://www.youtube.com/watch?v=...")
fetch_button = st.button("🔄 Fetch Transcript", use_container_width=True)

if fetch_button and video_url:
    # Reset session state
    st.session_state.transcript_text = ""
    st.session_state.video_title = ""

    with st.spinner("Fetching transcript..."):
        try:
            # 1. Extract video ID
            if "v=" in video_url:
                video_id = video_url.split("v=")[1].split("&")[0]
            elif "youtu.be/" in video_url:
                video_id = video_url.split("youtu.be/")[1].split("?")[0]
            else:
                video_id = video_url.strip()

            st.session_state.video_title = f"Video ID: {video_id}"

            # 2. Fetch transcript using the v1.2+ API
            ytt_api = YouTubeTranscriptApi()
            fetched_transcript = ytt_api.fetch(video_id)

            # Convert to text format
            st.session_state.transcript_text = " ".join([snippet.text for snippet in fetched_transcript])

            st.success(f"✅ Transcript successfully fetched!")
            st.info(f"📝 Transcript length: {len(st.session_state.transcript_text)} characters")

            # Display transcript preview
            with st.expander("📄 View Transcript Preview"):
                preview_length = min(2000, len(st.session_state.transcript_text))
                st.text_area(
                    "First 2000 characters:",
                    st.session_state.transcript_text[:preview_length] + (
                        "..." if len(st.session_state.transcript_text) > 2000 else ""),
                    height=300,
                    disabled=True
                )

        except TranscriptsDisabled:
            st.error("❌ Transcripts are disabled for this video.")
        except NoTranscriptFound:
            st.error("❌ No transcript found for this video. The video may not have captions.")
        except Exception as e:
            st.error(f"❌ Error during processing: {str(e)}")
            st.info("💡 Make sure the URL is correct and the video has captions enabled.")


#Chat with Gemini 2.5 Flash

st.markdown("---")
st.subheader("2️⃣ Ask Questions About the Video")

# Only show chat interface if transcript is loaded
if st.session_state.transcript_text:
    st.success(f"✓ Ready to answer questions about: {st.session_state.video_title}")

    user_input = st.text_area(
        "What would you like to know?",
        placeholder="e.g., What are the main topics discussed in this video?",
        height=100
    )

    col1, col2 = st.columns([3, 1])
    with col1:
        generate_button = st.button("💬 Generate Response", type="primary", use_container_width=True)
    with col2:
        if st.button("🗑️ Clear", use_container_width=True):
            st.session_state.transcript_text = ""
            st.session_state.video_title = ""
            st.rerun()

    if generate_button and user_input:
        with st.spinner("🤔 Thinking..."):
            try:
                # Initialize Gemini 2.5 Flash (FREE!)
                llm = ChatGoogleGenerativeAI(
                    model="gemini-2.5-flash",
                    temperature=0.3
                )

                # Create the prompt with full transcript context
                prompt = f"""You are a helpful YouTube Video Assistant. Answer the user's question based on the video transcript below.

IMPORTANT INSTRUCTIONS:
- Use ONLY the information from the video transcript provided
- Provide detailed, well-structured answers
- If the answer cannot be found in the transcript, clearly state: "This information is not available in the video transcript."
- Be conversational and helpful
- Quote relevant parts when helpful

VIDEO TRANSCRIPT:
{st.session_state.transcript_text}

USER QUESTION: {user_input}

DETAILED ANSWER:"""

                # Get response from Gemini
                response = llm.invoke(prompt)

                # Display response
                st.markdown("### 🤖 AI Response:")
                st.markdown(response.content)

            except Exception as e:
                st.error(f"❌ Error generating response: {str(e)}")
                st.info("💡 Try rephrasing your question or check your API key.")
else:
    st.info("👆 Please fetch a YouTube video transcript first to start asking questions.")

# Footer with important info
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.9em;'>
    <p>💡 <b>Tips:</b> This tool works best with videos that have accurate captions/transcripts.</p>
</div>
""", unsafe_allow_html=True)

# Add note about long transcripts
if st.session_state.transcript_text and len(st.session_state.transcript_text) > 50000:
    st.warning("⚠️ This transcript is quite long. For very long videos, responses might be slower or hit token limits.")