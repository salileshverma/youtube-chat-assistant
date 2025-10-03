import os
import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv

# -------------------------
# Configuration
# -------------------------
# Load environment variables from .env file
load_dotenv()

# Verify API key is loaded
if not os.getenv("GOOGLE_API_KEY"):
    st.error("⚠️ GOOGLE_API_KEY not found! Please set it in your .env file.")
    st.stop()

st.set_page_config(page_title="YouTube Transcript Chat Assistant", page_icon="🎥")
st.title("🎥 YouTube Transcript Chat Assistant")
st.markdown("Ask questions about any YouTube video with transcripts!")
st.markdown("---")

# Initialize session state for transcript and vectorstore
if 'transcript_text' not in st.session_state:
    st.session_state.transcript_text = ""
if 'vectorstore' not in st.session_state:
    st.session_state.vectorstore = None
if 'video_title' not in st.session_state:
    st.session_state.video_title = ""

# -------------------------
# Step 1: Get YouTube Transcript
# -------------------------
st.subheader("1️⃣ Load YouTube Video")
video_url = st.text_input("Enter YouTube Video URL:", placeholder="https://www.youtube.com/watch?v=...")
fetch_button = st.button("🔄 Fetch & Process Transcript", use_container_width=True)

if fetch_button and video_url:
    # Reset session state
    st.session_state.transcript_text = ""
    st.session_state.vectorstore = None
    st.session_state.video_title = ""

    with st.spinner("Fetching and processing transcript..."):
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

            # Convert to the format we need (list of dicts with 'text' key)
            st.session_state.transcript_text = " ".join([snippet.text for snippet in fetched_transcript])

            # 3. Split transcript for embeddings
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                length_function=len
            )
            chunks = splitter.split_text(st.session_state.transcript_text)

            # 4. Create embeddings & FAISS vectorstore
            embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
            st.session_state.vectorstore = FAISS.from_texts(chunks, embeddings)

            st.success(f"✅ Transcript successfully processed! Split into {len(chunks)} chunks.")
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

# -------------------------
# Step 2: Chat with Generative AI (RAG Implementation)
# -------------------------
st.markdown("---")
st.subheader("2️⃣ Ask Questions About the Video")

# Only show chat interface if transcript is loaded
if st.session_state.vectorstore:
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
            st.session_state.vectorstore = None
            st.session_state.video_title = ""
            st.rerun()

    if generate_button and user_input:
        with st.spinner("🤔 Thinking..."):
            try:
                # 1. Define the LLM (using Gemini Flash - corrected model name)
                llm = ChatGoogleGenerativeAI(
                    model="gemini-1.5-flash",  # Fixed model name
                    temperature=0.3
                )

                # 2. Define the Prompt Template for the RAG chain
                template = """You are a helpful YouTube Video Assistant. Your job is to answer questions based on the video transcript provided.

IMPORTANT INSTRUCTIONS:
- Use ONLY the information from the context (video transcript) below
- Provide detailed, well-structured answers
- If the answer cannot be found in the transcript, clearly state: "This information is not available in the video transcript."
- Quote relevant parts when helpful
- Be conversational and helpful

Context from video transcript:
{context}

Question: {question}

Detailed Answer:"""

                RAG_PROMPT = PromptTemplate(
                    template=template,
                    input_variables=["context", "question"]
                )

                # 3. Create the RAG Chain
                qa_chain = RetrievalQA.from_chain_type(
                    llm=llm,
                    chain_type="stuff",
                    retriever=st.session_state.vectorstore.as_retriever(
                        search_kwargs={"k": 4}  # Retrieve top 4 relevant chunks
                    ),
                    chain_type_kwargs={"prompt": RAG_PROMPT},
                    return_source_documents=False
                )

                # 4. Run the chain with the user's question
                response = qa_chain.invoke({"query": user_input})

                # Display response
                st.markdown("### 🤖 AI Response:")
                st.markdown(response['result'])

            except Exception as e:
                st.error(f"❌ Error generating response: {str(e)}")
                st.info("💡 Try rephrasing your question or check your API key.")
else:
    st.info("👆 Please fetch a YouTube video transcript first to start asking questions.")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.9em;'>
    <p>💡 <b>Tips:</b> This tool works best with videos that have accurate captions/transcripts.</p>
    <p>Powered by Google Gemini AI & LangChain</p>
</div>
""", unsafe_allow_html=True)