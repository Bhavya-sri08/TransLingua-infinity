import streamlit as st
from googletrans import Translator, LANGUAGES
from gtts import gTTS
import speech_recognition as sr
from pydub import AudioSegment
from pydub.playback import play
import io
import pdfplumber
import chardet
import os
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
# -------------------------
# Function: Translate Text
# -------------------------
def translate_text(text, dest_language):
    """Translate text using Google Translate API."""
    translator = Translator()
    translation = translator.translate(text, dest=dest_language)
    return translation.text

# -------------------------
# Function: Text-to-Speech (TTS)
# -------------------------
def text_to_speech(text, language_code):
    """Convert translated text to speech using gTTS."""
    tts = gTTS(text=text, lang=language_code)
    audio_file = "translated_audio.mp3"
    tts.save(audio_file)
    return audio_file

# -------------------------
# Function: Speech-to-Text (STT)
# -------------------------
def speech_to_text():
    """Convert speech to text using SpeechRecognition."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("🎤 Speak now...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
        st.success("✅ Recording complete. Processing...")

        try:
            text = recognizer.recognize_google(audio)
            return text
        except sr.UnknownValueError:
            return "❌ Could not understand audio."
        except sr.RequestError:
            return "⚠️ Error in connecting to the API."


def read_document_content(uploaded_file):
    if not uploaded_file:
        st.error("No valid file uploaded.")
        return ""
    
    raw_data = uploaded_file.getvalue()
    
    if raw_data is None:
        st.error("Uploaded file content is empty.")
        return ""

    # Check if the file is a PDF
    if uploaded_file.name.endswith('.pdf'):
        try:
            with pdfplumber.open(io.BytesIO(raw_data)) as pdf:
                text = "".join(page.extract_text() or "" for page in pdf.pages)
            return text
        except Exception as e:
            st.error(f"Failed to extract text from PDF: {e}")
            return ""

    # Detect encoding for non-PDF files
    result = chardet.detect(raw_data)
    encoding = result['encoding'] if result['encoding'] else "utf-8"
    
    try:
        document_content = raw_data.decode(encoding)
    except UnicodeDecodeError:
        document_content = raw_data.decode("utf-8", errors="ignore")

    return document_content
def summarize_text(text, num_sentences=3):
    if not text.strip():
        return "No text available for summarization."
    parser = PlaintextParser.from_string(text, Tokenizer("english"))
    summarizer = LsaSummarizer()
    summary = summarizer(parser.document, num_sentences)
    return " ".join(str(sentence) for sentence in summary)

# -------------------------
# Streamlit UI
# -------------------------
st.set_page_config(page_title="TransLingua-infinity(An AI-translator)", layout="wide")
st.title("🔊TransLingua-Infinity")
st.write("Language is the bridge that connects hearts and minds; translation ensures no one is left on the other side.🌍💬")

# Sidebar: Select Mode
mode = st.sidebar.radio("Select Mode:", ["Text-to-Text", "Text-to-Voice", "Voice-to-Text", "Voice-to-Voice", "Document Summarization"])

# -------------------------
# 1️⃣ Text-to-Text Translation
# -------------------------
if mode == "Text-to-Text":
    st.subheader("🔁 Translate Text")

    # User input
    text_input = st.text_area("Enter text to translate:", height=150)

    # Language selection
    selected_language = st.selectbox("Select Target Language:", list(LANGUAGES.values()))
    language_code = list(LANGUAGES.keys())[list(LANGUAGES.values()).index(selected_language)]

    if st.button("Translate"):
        if text_input.strip():
            translated_text = translate_text(text_input, language_code)
            st.success("✅ Translated Text:")
            st.write(f"**{translated_text}**")
        else:
            st.warning("⚠️ Please enter text to translate.")

# -------------------------
# 2️⃣ Text-to-Voice Translation
# -------------------------
elif mode == "Text-to-Voice":
    st.subheader("🎙️ Convert Text to Speech")

    text_input = st.text_area("Enter text to convert to speech:", height=150)

    # Language selection
    selected_language = st.selectbox("Select Language for Speech:", list(LANGUAGES.values()))
    language_code = list(LANGUAGES.keys())[list(LANGUAGES.values()).index(selected_language)]

    if st.button("Convert & Listen"):
        if text_input.strip():
            audio_file = text_to_speech(text_input, language_code)
            st.audio(audio_file, format="audio/mp3")

            with open(audio_file, "rb") as file:
                st.download_button(label="⬇️ Download Audio", data=file, file_name="translated_audio.mp3", mime="audio/mp3")
        else:
            st.warning("⚠️ Please enter text to convert.")

# -------------------------
# 3️⃣ Voice-to-Text
# -------------------------
elif mode == "Voice-to-Text":
    st.subheader("🎤 Speak and Convert to Text")

    if st.button("Start Recording"):
        recognized_text = speech_to_text()
        st.success("✅ Recognized Text:")
        st.write(f"**{recognized_text}**")

# -------------------------
# 4️⃣ Voice-to-Voice Translation
# -------------------------
elif mode == "Voice-to-Voice":
    st.subheader("🎤 Speak and Translate with Voice Output")

    # Select Target Language
    selected_language = st.selectbox("Select Target Language for Translation:", list(LANGUAGES.values()))
    language_code = list(LANGUAGES.keys())[list(LANGUAGES.values()).index(selected_language)]

    if st.button("Record & Translate"):
        recognized_text = speech_to_text()
        if "❌" in recognized_text or "⚠️" in recognized_text:
            st.error(recognized_text)
        else:
            # Translate Recognized Text
            translated_text = translate_text(recognized_text, language_code)
            st.success("✅ Translated Text:")
            st.write(f"**{translated_text}**")

            # Convert Translated Text to Speech
            audio_file = text_to_speech(translated_text, language_code)
            st.audio(audio_file, format="audio/mp3")

            with open(audio_file, "rb") as file:
                st.download_button(label="⬇️ Download Translated Audio", data=file, file_name="translated_audio.mp3", mime="audio/mp3")





# -------------------------
# Document Summarization
# -------------------------
elif mode == "Document Summarization":
    st.subheader("📄 Upload and Summarize Document")
    uploaded_file = st.file_uploader("Upload a PDF or text file:", type=["pdf", "txt"])
    
    if uploaded_file:
        document_text = read_document_content(uploaded_file)
        st.text_area("Extracted Text:", document_text, height=200)
        
        if st.button("Summarize Document"):
            summarized_text = summarize_text(document_text)
            st.success("✅ Summarized Document:")
            st.text_area("Summarized Text:", summarized_text, height=200)
