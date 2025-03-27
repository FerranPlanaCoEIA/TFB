from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import pickle
import os
import requests
import json
from groq import Groq



# Función para procesar archivos Markdown
def process_markdown(file_path, doc_id, doc_name, chunk_size=100, chunk_overlap=20):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            text = file.read()

        # Dividir el texto en chunks
        words = text.split()
        chunks = []
        for i in range(0, len(words), chunk_size - chunk_overlap):
            chunk = ' '.join(words[i:i + chunk_size])
            chunks.append((doc_id, doc_name, i // (chunk_size - chunk_overlap), chunk))

        return chunks
    except Exception as e:
        print(f"Error al procesar el Markdown {doc_name}: {e}")
        return []

# Función para crear embeddings
def create_embeddings(chunks):
    model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
    embeddings = model.encode([chunk[3] for chunk in chunks])
    return embeddings, model

# Función para guardar datos en Google Drive
def save_data(chunks, embeddings, model, save_folder):
    os.makedirs(save_folder, exist_ok=True)
    with open(os.path.join(save_folder, 'chunks_with_ids.pkl'), 'wb') as f:
        pickle.dump(chunks, f)
    with open(os.path.join(save_folder, 'embeddings.pkl'), 'wb') as f:
        pickle.dump(embeddings, f)
    with open(os.path.join(save_folder, 'model.pkl'), 'wb') as f:
        pickle.dump(model, f)

# Función para cargar datos
def load_data(save_folder):
    with open(os.path.join(save_folder, 'chunks_with_ids.pkl'), 'rb') as f:
        chunks = pickle.load(f)
    with open(os.path.join(save_folder, 'embeddings.pkl'), 'rb') as f:
        embeddings = pickle.load(f)
    with open(os.path.join(save_folder, 'model.pkl'), 'rb') as f:
        model = pickle.load(f)
    return chunks, embeddings, model

# Función para procesar todos los archivos Markdown
def process_all_markdown_files(carpeta_path):
    files = os.listdir(carpeta_path)
    files_array = sorted([file for file in files if os.path.isfile(os.path.join(carpeta_path, file)) and file.endswith('.md')])
    all_chunks = []

    for file in files_array:
        doc_id = files_array.index(file)
        file_path = os.path.join(carpeta_path, file)
        chunks = process_markdown(file_path, doc_id, file)
        all_chunks.extend(chunks)

    return all_chunks

# Función para obtener los chunks más similares
def get_similar_chunks(question, chunks, embeddings, model, top_n):
    question_embedding = model.encode([question])
    similarities = cosine_similarity(question_embedding, embeddings)[0]
    top_indices = np.argsort(similarities)[-top_n:][::-1]
    return [(chunks[i], similarities[i]) for i in top_indices]



# Parte 1: Procesar todos los archivos md y guardar los datos
script_dir = os.path.dirname(os.path.abspath(__file__)) # Carpeta raíz
carpeta_path = os.path.join(script_dir, 'Documentacion')
save_folder = os.path.join(script_dir, 'Indice')

print("Procesando archivos Markdown...")

all_chunks = process_all_markdown_files(carpeta_path)

if all_chunks:
    print(f"Chunks generados: {len(all_chunks)}")
    embeddings, model = create_embeddings(all_chunks)
    save_data(all_chunks, embeddings, model, save_folder)
    print(f"Datos procesados y guardados exitosamente en {save_folder}.")
else:
    print("No se generaron chunks. Verifica los archivos Markdown.")