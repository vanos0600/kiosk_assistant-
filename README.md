Proof of Concept (PoC): Voice-Aware Kiosk Assistant
Author: Oskar David Vanegas Juarez
Technologies: Python, Streamlit, Google Gemini API, Docker, Speech Recognition (ASR)
Alignment with Thales: High-impact solution for biometric interaction and user experience improvement in unattended environments (kiosks).

🎯 Project Objective
The main goal of this PoC was to create a kiosk assistant that responds adaptively to users by distinguishing between:

Confusion/Question: If the user doesn't understand or asks for help ("How do I proceed?"), the assistant should be calm, reassuring, and provide the next simple instruction.

Statement/Data: If the user provides a response ("My name is John"), the assistant should briefly confirm ("Understood") and register the data (simulated).

This demonstrates AI's capability to dynamically adjust support levels based on the user's emotional state and needs, a key requirement for biometrics and digital identity.

🧠 Architecture and Engineering Design
This project was designed with a robust three-layer architecture, ideal for production environments or CI/CD (Continuous Integration/Continuous Deployment):

Layer	Component	Function and Technical Rationale
1. UI/Front-end	Streamlit	Used for rapid Python prototyping (PoC) and its efficient integration with streamlit-mic-recorder component and audio handling.
2. ASR Conversion	speech_recognition, pydub, FFmpeg	Responsible for capturing microphone audio bytes, converting to WAV format, and transcribing with Google Speech Recognition.
3. AI Brain (LLM)	Google Gemini 2.5 Flash	Model chosen after migrating from other vendors to ensure fast performance (Flash) and use of free quota for PoC, demonstrating cost efficiency.
4. Containerization	Dockerfile	Ensures reproducibility and deployment in any environment.
🧩 Technical Challenges Solved (Evidence of Rigor)
To achieve a functional and robust deployment, two crucial engineering challenges were identified and resolved:

1. Audio Dependencies Deployment in Linux (Docker)
When migrating the project to a Docker container (python:3.10-slim), the ASR module failed due to missing low-level operating system libraries.

Solution (Rigor/DevOps): Identified and explicitly included the installation of ffmpeg, libsndfile1, and portaudio19-dev in the Dockerfile to resolve pydub and SpeechRecognition system-level dependencies.

Key Command: RUN apt-get install -y ffmpeg libsndfile1 portaudio19-dev

2. "Invalid Role" Error in Gemini API
After migration, the Gemini API returned a 400 INVALID_ARGUMENT error due to the use of the system role in the conversation history.

Solution (Adaptability/Debugging): Refactored the get_adaptive_response function to move the system instruction (system_prompt) to the system_instruction parameter within the API call configuration, complying with Google's protocol.

🛠️ Usage and Deployment Instructions
To run the PoC on your local machine:

Obtain a free GEMINI_API_KEY from Google AI Studio.

Create and complete a .env file in the root directory.

Execute the Docker commands.

Access http://localhost:8501.

Quick Start
bash
# Clone the repository
git clone <repository-url>
cd <repository-directory>

# Create .env file with your API key
echo "GEMINI_API_KEY=your_api_key_here" > .env

# Build and run with Docker
docker build -t voice-kiosk-poc .
docker run -p 8501:8501 voice-kiosk-poc
⏭️ Next Steps (Future Vision)
TTS (Text-to-Speech) Integration: Add voice response from the assistant for a completely touch-free experience.

Multilingual Support: Implement automatic language detection to assist users in Czech or Spanish (based on my language knowledge).

State Management: Add logic for the assistant to remember previous user responses and guide through a complete form flow.
