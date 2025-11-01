import streamlit as st
from google import genai 
from google.genai.errors import APIError
import os
import io
import tempfile
from pydub import AudioSegment
import speech_recognition as sr
from dotenv import load_dotenv
from streamlit_mic_recorder import mic_recorder 

# --- 0. Initial Configuration and Keys ---
load_dotenv()
try:
    gemini_api_key = os.getenv("GEMINI_API_KEY") 
    if not gemini_api_key:
        # NOTE: This error message is essential for debugging in Streamlit
        st.error("Error: The GEMINI_API_KEY is not configured in the .env file. Please check it.")
        st.stop()
    client = genai.Client(api_key=gemini_api_key)
except Exception:
    st.error("Error initializing the Gemini API. Please check your key and environment variables.")
    st.stop()

# --- 1. ASR Core (Speech-to-Text) ---
def transcribe_audio(audio_bytes):
    """Transcribes audio using Google Speech Recognition, standardizing the format via pydub."""
    recognizer = sr.Recognizer()
    
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
        temp_filename = tmp_file.name
        
        try:
            # pydub loads the raw bytes from the microphone recorder
            audio_segment = AudioSegment.from_file(io.BytesIO(audio_bytes))
            audio_segment.export(temp_filename, format="wav")
            
            with sr.AudioFile(temp_filename) as source:
                audio = recognizer.record(source)
                transcription = recognizer.recognize_google(audio, language="en-US")
                return transcription
        
        except sr.UnknownValueError:
            return "Could not understand the audio. Please speak more clearly."
        except sr.RequestError as e:
            return f"Error with Google Speech Recognition service; check your internet connection. Error: {e}"
        except Exception as e:
            return f"Audio processing error: {e}"
        finally:
            if os.path.exists(temp_filename):
                try:
                    os.remove(temp_filename)
                except PermissionError:
                    st.warning("Warning: Could not immediately delete the temporary file (Windows permission issue).")
                except Exception as e:
                    st.warning(f"Warning while trying to delete temporary file: {e}")


# --- 2. LLM Brain (Adaptive Response with GEMINI) ---
def get_adaptive_response(transcription: str):
    """
    Generates an adaptive response using Google Gemini (gemini-2.5-flash).
    The system prompt is now correctly passed using system_instruction in the config.
    """
    # Define the system instruction separately
    system_instruction = f"""
    You are a friendly, highly helpful digital kiosk assistant. Your job is to guide the user filling out a form. Analyze their transcription and generate an adaptive response based on the user's intent:

    1.  **Detect Difficulty/Question (E.g., "How do I fill this out?", "I don't understand").**
    2.  **Response (Confusion):** Respond calmly, reassure the user, and give a *simple, direct* instruction for the next step, or ask for clarification.
    3.  **Detect Statement/Affirmation (E.g., "My name is John", "The next page").**
    4.  **Response (Statement):** Simply confirm briefly in a friendly manner (E.g., "Understood.", "Processing data.") and wait for the next instruction.

    Keep the response very concise (maximum 2 sentences).
    
    The user's transcription is: "{transcription}"
    """

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash", 
            # ONLY the USER content is passed here. The system instruction is handled in config.
            contents=[
                {"role": "user", "parts": [{"text": transcription}]}
            ],
            config={
                "temperature": 0.2,
                # THIS IS THE KEY FIX: Passing the system instruction correctly
                "system_instruction": system_instruction 
            }
        )
        return response.text
    except APIError as e:
        # This catches errors like Invalid API Key (400) or Rate Limits
        return f"Error contacting the Gemini API: {e}. Ensure your GEMINI_API_KEY is correct and your project has API access."
    except Exception as e:
        return f"Unexpected Gemini error: {e}"

# --- 3. Streamlit Interface ---
def main():
    st.set_page_config(page_title="Voice-Aware Kiosk Assistant", layout="wide")
    st.title("Voice-Aware Kiosk Assistant (Gemini & Mic)")
    st.subheader("Demo: Live Voice Capture + Free Adaptive Response")

    st.markdown("""
        **1. Click the microphone button to record.** **2. Click 'Stop'** to transcribe and get the adaptive response from Gemini.
    """)
    st.divider()

    # NEW: Microphone Recording Component
    # Updated start/stop prompts with emojis for better UX
    mic_result = mic_recorder(
        start_prompt="Click to Record",
        stop_prompt="Click to Stop",
        key='mic_recorder',
        format='wav'
    )

    if mic_result and mic_result.get('bytes'):
        audio_bytes = mic_result.get('bytes')
        st.success("Recording captured. Processing...")
        
        st.audio(audio_bytes, format='audio/wav')
        st.divider()
        
        # --- Processing Logic ---
        
        # 1. ASR Transcription
        with st.spinner("1. Transcribing audio (ASR) with Google Speech Recognition..."):
            transcription_text = transcribe_audio(audio_bytes)
        
        st.info(f"**User Transcription:**\n\n_{transcription_text}_")
        
        if "Could not understand" in transcription_text or "Error" in transcription_text:
            st.error("Could not get a clear transcription. Please try again.")
            return

        # 2. LLM Analysis and Response (Gemini)
        with st.spinner("2. Analyzing intent and generating adaptive response (Gemini)..."):
            llm_response = get_adaptive_response(transcription_text)

        st.divider()
        st.subheader("Adaptive Assistant Response (Gemini)")
        st.code(llm_response, language='markdown')


if __name__ == "__main__":
    main()
