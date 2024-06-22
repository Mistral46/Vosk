import os
from vosk import Model, KaldiRecognizer
import pyaudio
import spacy
import pyttsx3
import json

# Inicializa recognizer de Vosk
model = Model("modelos/vosk-model-small-es-0.42") #ruta al modelo en español
recognizer = KaldiRecognizer(model, 16000)

# Inicializa Spacy para procesamiento de lenguaje
nlp = spacy.load("es_core_news_sm")

# Inicializa pyttsx3 para síntesis de voz
engine = pyttsx3.init()

# Base de conocimiento sobre ISO 27001:2022
iso_27001_knowledge = {
    "identificación de activos de datos": """
    La Identificación de Activos de Datos implica catalogar todos los datos que tu organización maneja,
    incluyendo información confidencial, datos personales, documentos administrativos, etc., y clasificarlos
    según su importancia y nivel de sensibilidad.
    """,
    "identificación de riesgos": """
    La Identificación de Riesgos implica definir los posibles riesgos de seguridad que pueden afectar a los activos
    de datos de tu organización. Esto incluye cualquier cosa desde pérdida de datos hasta ataques cibernéticos.
    """,
    "políticas de seguridad": """
    Las Políticas de Seguridad deben establecer directrices claras sobre cómo manejar y proteger la información de la organización.
    Esto puede incluir el control de accesos, encriptación de datos, entrenamiento del personal, etc.
    """,
    "controles de seguridad": """
    Los Controles de Seguridad son medidas prácticas y técnicas que se implementan para proteger los activos de datos.
    Ejemplos incluyen firewalls, sistemas de detección de intrusiones, y copias de seguridad regulares.
    """,
    "mejora continua": """
    La Mejora Continua es esencial para mantener la seguridad de la información. Esto implica revisar y actualizar regularmente
    las políticas y controles de seguridad para adaptarse a nuevas amenazas y vulnerabilidades.
    """
}

def procesar_texto(texto):
    # Procesa el texto de entrada y busca términos clave
    doc = nlp(texto)
    for token in doc:
        palabra_clave = token.lemma_.lower()
        if palabra_clave in iso_27001_knowledge:
            return iso_27001_knowledge[palabra_clave]
    
    # Respuesta por defecto si no se encuentra un término relevante
    return "Lo siento, no tengo información sobre ese tema específico de ISO 27001:2022."

# Configura pyaudio para captura de audio
p = pyaudio.PyAudio()
#stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8192)
#stream.start_stream()
try:
    # Cambia el índice del dispositivo de entrada al valor correcto basado en la salida de arecord -l
    input_device_index = 1  # Utiliza el índice adecuado para tu dispositivo
    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=16000,
                    input=True,
                    input_device_index=input_device_index,
                    frames_per_buffer=8192)
    stream.start_stream()
except IOError as e:
    print(f"Error al abrir el stream de audio: {e}")
    p.terminate()
    exit(1)

print("Comienza a hablar...")

# Captura de audio y reconocimiento
while True:
    try:
        data = stream.read(4096, exception_on_overflow=False)
        if recognizer.AcceptWaveform(data):
            result = recognizer.Result()
            result_dict = json.loads(result)
            texto = result_dict.get('text','')
            if texto:
                print(f"Escuché: {texto}")
                respuesta = procesar_texto(texto)
                print(f"Respuesta: {respuesta}")
                engine.say(respuesta)
                engine.runAndWait()
    except IOError as e:
        print(f"Error al leer el stream de audio: {e}")