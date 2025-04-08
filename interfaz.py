# Ejecutar interfaz: streamlit run interfaz.py

import streamlit as st
import base64
from inferencia_interfaz import inferencia_interfaz

# Función para cargar una imagen en formato base64
def cargar_imagen_base64(ruta_imagen):
    with open(ruta_imagen, "rb") as archivo_imagen:
        return base64.b64encode(archivo_imagen.read()).decode()

# Ruta de la imagen en la carpeta Interfaz-Images
ruta_imagen = "Interfaz-Images/Image1.webp"  # Cambia el nombre del archivo

# Cargar la imagen en base64
imagen_base64 = cargar_imagen_base64(ruta_imagen)

# Estilo para imagen de fondo usando base64
st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url('data:image/jpeg;base64,{imagen_base64}');
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# Título de la aplicación
st.title("RAG de la Coppermind")

# Entrada de texto
texto = st.text_input("Escribe tu pregunta:")

# Botón para enviar el texto
if st.button("Enviar"):
    # Convertir el texto a minúsculas y mostrarlo
    texto_minuscula = inferencia_interfaz(texto)
    st.write(f"Texto en minúsculas: {texto_minuscula}")
