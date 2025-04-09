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

# Estilo para imagen de fondo y ocultar barra superior
def aplicar_estilos():
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url('data:image/webp;base64,{imagen_base64}');
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            margin-top: -50px;
        }}
        #MainMenu {{visibility: hidden;}}  /* Oculta la barra superior */
        footer {{visibility: hidden;}}    /* Oculta el footer */
        header {{visibility: hidden;}}    /* Oculta el header */
        .respuesta-cuadro {{
            background-color: #f0f0f0; /* Color gris claro */
            padding: 20px; /* Espaciado interno */
            border-radius: 5px; /* Bordes redondeados */
            box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1); /* Sombra */
            background-color: #464646; /* Color del cuadro de texto */
            color: #ffffff;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# Aplicar estilos al inicio
aplicar_estilos()

# Título de la aplicación
st.title("RAG de la Coppermind")

# Estado inicial de la respuesta
if "respuesta" not in st.session_state:
    st.session_state.respuesta = ""

# Función para manejar el envío
def manejar_input():
    texto = st.session_state.texto
    if texto.strip():
        with st.spinner("Generando respuesta..."):  # Mostrar mensaje mientras se genera la respuesta
            st.session_state.respuesta = inferencia_interfaz(texto)
    # Reaplicar estilos después de actualizar el estado
    aplicar_estilos()

# Campo de texto con envío al presionar Enter
st.text_input("Escribe tu pregunta:", key="texto", on_change=manejar_input, placeholder="")

# Botón de envío alternativo
if st.button("Enviar"):
    manejar_input()

# Mostrar la respuesta dentro de un cuadro gris si existe
if st.session_state.respuesta:
    st.markdown(
        f"<div class='respuesta-cuadro'>{st.session_state.respuesta}</div>",
        unsafe_allow_html=True
    )
