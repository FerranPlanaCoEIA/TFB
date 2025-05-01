from sentence_transformers import SentenceTransformer
from openai import AzureOpenAI
import pickle
import os
import time

# Función para procesar todos los archivos Markdown
def process_all_markdown_files(carpeta_path, chunk_size, chunk_overlap):
    files = os.listdir(carpeta_path)
    files_array = sorted([file for file in files if os.path.isfile(os.path.join(carpeta_path, file)) 
                          and file.endswith('.md')])
    all_chunks = []

    for file in files_array:
        doc_id = files_array.index(file)
        file_path = os.path.join(carpeta_path, file)
        chunks = process_markdown(file_path, doc_id, file, chunk_size, chunk_overlap)
        all_chunks.extend(chunks)

    return all_chunks

# Función para procesar archivos Markdown
def process_markdown(file_path, doc_id, doc_name, chunk_size, chunk_overlap):
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
def create_embeddings(chunks, model_embeddings):
    model = SentenceTransformer(model_embeddings)
    embeddings = model.encode([chunk[3] for chunk in chunks])
    return embeddings, model

# Función para crear embeddings con Azure OpenAI con pausas entre solicitudes
def create_embeddings_AzureOpenAI(chunks,client,model_embeddings):
    embeddings=[]
    for chunk in chunks:
        text=chunk[3]
        response=client.embeddings.create(input=[text],model=model_embeddings)
        embeddings.append(response.data[0].embedding)
        print(f"\rEmbeddings creados: {round(len(embeddings)/2054*100,2)} %",end="")
        time.sleep(1.1)
    return embeddings


# Función para guardar datos en Google Drive
def save_data(chunks, embeddings, save_folder):
    os.makedirs(save_folder, exist_ok=True)
    with open(os.path.join(save_folder, 'chunks_with_ids.pkl'), 'wb') as f:
        pickle.dump(chunks, f)
    with open(os.path.join(save_folder, 'embeddings.pkl'), 'wb') as f:
        pickle.dump(embeddings, f)

# Función para cargar datos
def load_data(save_folder):
    with open(os.path.join(save_folder, 'chunks_with_ids.pkl'), 'rb') as f:
        chunks = pickle.load(f)
    with open(os.path.join(save_folder, 'embeddings.pkl'), 'rb') as f:
        embeddings = pickle.load(f)
    return chunks, embeddings