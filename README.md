AI Kiosk: Voice-Aware Kiosk Assistant
🌟 Resumen del Proyecto
Este proyecto es una Prueba de Concepto (PoC) que implementa un Asistente de Quiosco Adaptativo. Su objetivo principal es demostrar la capacidad de fusionar el Reconocimiento Automático de Voz (ASR) con un Modelo de Lenguaje Grande (LLM) para ir más allá de la simple transcripción.

El asistente detecta la intención del usuario (si está confundido o simplemente dictando datos) y genera una respuesta contextual y empática.

💡 Valor Clave
Inteligencia Adaptativa: El LLM (GPT-3.5) analiza el tono y el contenido para responder con ayuda (si hay confusión) o con confirmación (si hay dictado de datos).

Pila de Tecnología Completa: Uso de Python, Streamlit, OpenAI, y empaquetado final con Docker para despliegue (CI/CD).

Manejo de Audio Robusto: Solución de la dependencia de FFmpeg para el procesamiento de archivos de audio comunes (.mp3, .m4a).

🏗️ Arquitectura y Flujo de Procesamiento
El sistema se ejecuta dentro de un contenedor Docker para garantizar la portabilidad y el entorno de audio (FFmpeg).

Entrada: El usuario sube un archivo de audio al frontend de Streamlit.

Conversión: pydub convierte el archivo de entrada a un formato WAV estándar.

Transcripción (ASR): SpeechRecognition transcribe el audio a texto.

Análisis de Intención: El texto se envía a OpenAI con un system prompt que lo dirige a clasificar la intención y generar una Respuesta Adaptativa.

Salida: La respuesta se muestra en la interfaz web.

⚙️ Documentación Técnica y Comandos Paso a Paso
Esta sección detalla cada comando y herramienta utilizada para construir y desplegar el proyecto.

I. Configuración Inicial del Entorno

#,Comando Ejecutado,Propósito,Herramienta
1,source venv/Scripts/activate,Activar el entorno virtual de Python (venv).,MINGW64 / PowerShell
2,pip install streamlit openai SpeechRecognition pydub python-dotenv,Instalar las librerías principales de la aplicación.,pip
3,touch requirements.txt app.py .env Dockerfile .gitignore,Crear los archivos base del proyecto.,MINGW64 (touch)

II. Estructura

Archivo,Contenido Clave,Uso
app.py,"Lógica de ASR, LLM y la interfaz Streamlit.",Ejecuta la lógica central del asistente.
.env,"OPENAI_API_KEY=""...""",Almacena la clave secreta de OpenAI de forma segura.
requirements.txt,Lista de librerías Python.,Define las dependencias para la construcción de Docker.
Dockerfile,Instrucciones de construcción y FFmpeg.,Define el entorno de despliegue.
.gitignore,Excluye venv/ y .env.,Previene la exposición de secretos en GitHub.

III. Gestión de Versiones y Seguridad (Git/GitHub)

#,Comando Ejecutado,Propósito,Herramienta
1,git init,Inicializar un nuevo repositorio Git local.,Git
2,git add .,Añadir todos los archivos nuevos (excepto los ignorados en .gitignore).,Git
3,"git commit -m ""feat: Initial commit...""",Crear el primer punto de control del código.,Git
4,git rm --cached .env,SOLUCIÓN DE ERROR: Eliminar el archivo .env del historial de Git (porque se añadió accidentalmente).,Git
5,git commit --amend --no-edit,Reescribir el último commit para asegurar que el secreto no exista en el historial.,Git
6,git remote add origin [URL],Vincular el repositorio local con el repositorio remoto de GitHub.,Git
7,git push -u origin master --force,"Subir el código limpio a GitHub, forzando la aceptación del historial reescrito.",Git

IV. Despliegue y Ejecución (Docker/CI)
#,Comando Ejecutado,Propósito,Resultado Esperado
1,docker build -t kiosk-assistant .,"Construir la imagen de Docker, instalando FFmpeg como dependencia del sistema.",Una imagen de Docker etiquetada como kiosk-assistant.
2,docker run -d -p 8501:8501 --env-file .env kiosk-assistant,"Ejecutar el contenedor, mapeando el puerto 8501 y pasando la clave API de forma segura.","El contenedor se ejecuta en segundo plano (detached), accesible localmente."
3,(Navegador) http://localhost:8501,Acceder a la aplicación Streamlit en el navegador.,Interfaz lista para recibir audio y procesar el ASR/LLM.
4,docker ps,Verificar que el contenedor esté corriendo.,Mostrar el ID y el estado Up X seconds.
5,docker stop [ID],Detener el contenedor después de la prueba.,Finaliza el proceso de la aplicación.


El link del proyecto: http://localhost:8501/ 
