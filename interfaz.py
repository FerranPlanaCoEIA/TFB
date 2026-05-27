import streamlit as st
import base64
from inferencia_interfaz import responder_chatbot

#st.set_page_config(page_title="RAG de la Coppermind", page_icon="📖", layout="centered") # Con un icono
st.set_page_config(page_title="Chatbot RAG agéntico de la Coppermind", page_icon="Interfaz-Images/GhostBloods.jpg", layout="centered") # Con una foto

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
        .stChatMessage {{
            background-color: rgba(46, 46, 46, 0.82);
            border-radius: 12px;
            padding: 0.35rem;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )


# Aplicar estilos al inicio
aplicar_estilos()

# Título de la aplicación
st.title("Chatbot RAG agéntico de la Coppermind")

if "messages" not in st.session_state:
    st.session_state.messages = []

if "conversation_summary" not in st.session_state:
    st.session_state.conversation_summary = ""

def nueva_conversacion():
    st.session_state.messages = []
    st.session_state.conversation_summary = ""


header_col, action_col = st.columns([4, 1])
with header_col:
    st.caption("Haz preguntas enlazadas: el agente decidirá si necesita buscar, repetir búsquedas o responder sin retrieval.")
with action_col:
    if st.button("Nueva conversación"):
        nueva_conversacion()
        st.rerun()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message.get("display_content", message["content"]))

prompt = st.chat_input("Haz una pregunta sobre el Cosmere")
if prompt:
    previous_history = [
        {"role": message["role"], "content": message["content"]}
        for message in st.session_state.messages
    ]

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Generando respuesta..."):
            result = responder_chatbot(
                prompt,
                previous_history,
                st.session_state.conversation_summary,
            )
        st.markdown(result["assistant_display_content"])

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": result["assistant_content"],
            "display_content": result["assistant_display_content"],
        }
    )
    st.session_state.conversation_summary = result["conversation_summary"]
