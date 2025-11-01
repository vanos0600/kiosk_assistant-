# Importaciones necesarias para Streamlit, Gemini, ASR y manejo de audio
import os
import io
import tempfile
import streamlit as st
import speech_recognition as sr
# REMOVED: from pydub import AudioSegment <-- Ya no se necesita
from dotenv import load_dotenv

# Importar la librería de Google GenAI (Asegúrate de tener google-genai instalado)
# Nota: La importación de tu código original era de 'google import genai'. 
# Lo mantendremos así para evitar conflictos de dependencia, pero se recomienda 'google.genai import Client'
from google import genai 
from google.genai.errors import APIError
from streamlit_mic_recorder import mic_recorder 

# --- Configuración Inicial y Carga de Clave API (Lógica Simplificada para Cloud) ---
# Función de carga segura de la clave. En Streamlit Cloud, solo se usa st.secrets.
# Simplificamos la lógica para asegurar que la clave se lea del lugar correcto en el ambiente Cloud.
def load_gemini_api_key():
    # Intenta leer directamente desde Streamlit Secrets (funciona en Cloud)
    # Si la clave no existe, la expresión st.secrets.get() devolverá None
    key = st.secrets.get("GEMINI_API_KEY")
    
    # Para la ejecución local o con Docker, todavía se necesita dotenv
    if key is None:
        load_dotenv()
        key = os.getenv("GEMINI_API_KEY")
        
    return key

gemini_api_key = load_gemini_api_key()

# Verificación de la clave
if not gemini_api_key:
    # Este mensaje de error ya no confunde al usuario con el .env en la nube
    st.error("Error: La clave GEMINI_API_KEY no se encontró. Por favor, revise la configuración de 'Secrets' en Streamlit Cloud.")
    st.stop()

# Inicializa la API de Gemini (solo si la clave fue cargada)
try:
    # Usando la importación que proporcionaste (google import genai)
    client = genai.Client(api_key=gemini_api_key)
except Exception as e:
    st.error(f"Error inicializando el cliente Gemini: {e}")
    st.stop()
    
# --- 1. ASR Core (Speech-to-Text) ---
def transcribe_audio(audio_bytes):
    """
    Transcribes audio usando la librería SpeechRecognition, 
    leyendo directamente los bytes WAV del grabador de Streamlit,
    eliminando la necesidad de pydub/ffprobe.
    """
    recognizer = sr.Recognizer()  
    
    # Crea un objeto AudioData de SpeechRecognition directamente desde los bytes WAV
    # Los parámetros (sample_rate y sample_width) son los estándares para el formato WAV
    audio_data = sr.AudioData(audio_bytes, sample_rate=44100, sample_width=2)
    
    try:
        # Usa el motor de reconocimiento de Google
        transcription = recognizer.recognize_google(audio_data, language="en-US")
        return transcription
        
    except sr.UnknownValueError:
        return "Could not understand the audio. Please speak more clearly."
    except sr.RequestError as e:
        return f"Error with Google Speech Recognition service; check your internet connection. Error: {e}"
    except Exception as e:
        return f"Audio processing error: {e}"


# --- 2. LLM Brain (Adaptive Response with GEMINI) ---
def get_adaptive_response(transcription: str):
    """
    Generates an adaptive response using Google Gemini (gemini-2.5-flash).
    The system prompt is now correctly passed using system_instruction in the config.
    """
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
    st.set_page_config(page_title="Voice-Aware Kiosk Assistant 🤖", layout="wide")
    st.title("Voice-Aware Kiosk Assistant (Gemini & Mic)")
    st.subheader("Demo: Live Voice Capture + Adaptive Response")

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
