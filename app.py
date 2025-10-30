import streamlit as st
import openai
import os
import io
import tempfile
from pydub import AudioSegment
import speech_recognition as sr
from dotenv import load_dotenv

# --- 0. Configuración Inicial y Keys ---
# Carga las variables de entorno desde .env
load_dotenv()
try:
    openai.api_key = os.getenv("OPENAI_API_KEY")
    if not openai.api_key:
        st.error("Error: La clave OPENAI_API_KEY no está configurada en el archivo .env. Por favor, revísalo.")
        st.stop()
except Exception:
    st.error("Error al inicializar la API de OpenAI. Revisa tu clave y las variables de entorno.")
    st.stop()

# --- 1. Núcleo ASR (Speech-to-Text) ---
def transcribe_audio(audio_data):
    """
    Usa SpeechRecognition (con el motor de Google) para transcribir datos de audio.
    Utiliza pydub y un archivo temporal para asegurar que el audio es compatible con WAV.
    """
    recognizer = sr.Recognizer()
    
    # Crea un archivo temporal para que pydub pueda trabajar y SpeechRecognition pueda leer
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
        temp_filename = tmp_file.name
        
        try:
            # Pydub estandariza el audio subido (incluso si es .wav, lo formatea correctamente)
            audio_segment = AudioSegment.from_file(io.BytesIO(audio_data.getvalue()))
            audio_segment.export(temp_filename, format="wav")
            
            # SpeechRecognition lee el archivo WAV estandarizado
            with sr.AudioFile(temp_filename) as source:
                audio = recognizer.record(source)
                # Usamos el motor de Google ASR (gratuito y potente para demos)
                transcription = recognizer.recognize_google(audio, language="es-ES")
                return transcription
        
        except sr.UnknownValueError:
            return "No pude entender el audio. Por favor, habla más claro."
        except sr.RequestError as e:
            return f"Error en el servicio de reconocimiento de voz de Google; revisa tu conexión a internet. Error: {e}"
        except Exception as e:
            return f"Error de procesamiento de audio: {e}"
        finally:
            # Asegura la eliminación del archivo temporal, manejando el error de permiso de Windows
            if os.path.exists(temp_filename):
                try:
                    os.remove(temp_filename)
                except PermissionError:
                    # Este bloque ignora el WinError 32 (archivo en uso) para que el demo no falle.
                    # El archivo temporal se eliminará cuando Windows libere el handle.
                    st.warning("Advertencia: No se pudo eliminar el archivo temporal inmediatamente (problema de permisos de Windows).")
                except Exception as e:
                    # Captura otros posibles errores de eliminación
                    st.warning(f"Advertencia al intentar eliminar archivo temporal: {e}")

# --- 2. Cerebro LLM (Respuesta Adaptativa) ---
def get_adaptive_response(transcription: str):
    """
    Genera una respuesta adaptativa basada en la transcripción del usuario,
    detectando si hay confusión o si solo es una declaración de datos.
    """
    system_prompt = f"""
    Eres un asistente digital de quiosco, amable y extremadamente servicial. Tu trabajo es guiar al usuario 
    que está llenando un formulario. Analiza su transcripción y genera una respuesta adaptativa:

    1.  **Detección de Dificultad/Pregunta (Ej: "¿Cómo lleno esto?", "No entiendo").**
    2.  **Respuesta (Confusión):** Responde con calma, reasegurando al usuario y dándole una instrucción *simple y directa* para el siguiente paso, o pidiendo clarificación.
    3.  **Detección de Declaración/Afirmación (Ej: "Mi nombre es Juan", "La siguiente página").**
    4.  **Respuesta (Declaración):** Simplemente confirma brevemente de forma amistosa (Ej: "Entendido.", "Procesando datos.") y espera la siguiente instrucción.

    Mantén la respuesta concisa (máximo 2 frases).

    La transcripción del usuario es: "{transcription}"
    """

    try:
        client = openai.OpenAI()
        response = client.chat.completions.create(
            model="gpt-3.5-turbo", # Elegido por su rapidez y bajo costo para demos
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": transcription}
            ],
            temperature=0.2 # Mantenemos la temperatura baja para respuestas más predecibles
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error al contactar a la API de OpenAI: {e}"

# --- 3. Interfaz Streamlit ---
def main():
    st.set_page_config(page_title="Voice-Aware Kiosk Assistant 🤖", layout="wide")
    st.title("🤖 Asistente de Quiosco por Voz")
    st.subheader("Demo: Detección de Confusión + Respuesta Adaptativa")

    st.markdown("""
        Sube un archivo de audio (.wav, .mp3, .m4a) para simular la voz de un usuario interactuando con el quiosco.
    """)

    uploaded_file = st.file_uploader("🎤 Carga tu audio (.wav, .mp3, .m4a)", type=["wav", "mp3", "m4a"])

    if uploaded_file is not None:
        st.success("Archivo subido con éxito.")
        
        # Mostrar el audio para feedback
        st.audio(uploaded_file, format=uploaded_file.type)
        st.divider()
        
        # --- Lógica de Procesamiento ---
        
        # 1. Transcripción ASR
        with st.spinner("1. Transcribiendo audio (ASR) con Google Speech Recognition..."):
            transcription_text = transcribe_audio(uploaded_file)
        
        st.info(f"**Transcripción del Usuario:**\n\n_{transcription_text}_")
        
        if "No pude entender" in transcription_text or "Error" in transcription_text:
            st.error("No se pudo obtener una transcripción clara. Por favor, intenta de nuevo.")
            return

        # 2. Análisis y Respuesta LLM
        with st.spinner("2. Analizando intención y generando respuesta adaptativa (LLM)..."):
            llm_response = get_adaptive_response(transcription_text)

        st.divider()
        st.subheader("💡 Respuesta del Asistente Adaptativo")
        st.code(llm_response, language='markdown')


if __name__ == "__main__":
    main()