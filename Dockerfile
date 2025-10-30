# 1. BASE IMAGE: Usa una imagen base de Python ligera (3.10-slim)
FROM python:3.10-slim

# 2. DIRECTORIO DE TRABAJO: Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# 3. INSTALACIÓN DE DEPENDENCIAS DEL SISTEMA
# Los paquetes 'pydub' y 'SpeechRecognition' a veces requieren utilidades de audio
# como 'ffmpeg' o 'libsndfile1'.
RUN apt-get update && apt-get install -y ffmpeg libsndfile1

# 4. INSTALACIÓN DE DEPENDENCIAS DE PYTHON
# Copia el archivo de requisitos e instala las librerías
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. CÓDIGO DE LA APLICACIÓN
# Copia el resto de los archivos de la aplicación (incluyendo app.py y .env)
COPY . .

# 6. PUERTO
# Expone el puerto por defecto de Streamlit
EXPOSE 8501

# 7. COMANDO DE INICIO
# Comando para ejecutar la aplicación Streamlit al iniciar el contenedor
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]