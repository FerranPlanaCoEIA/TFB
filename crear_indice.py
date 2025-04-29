import os
from dotenv import load_dotenv
import time
import math
from openai import AzureOpenAI
from helpers.crear_indice import process_all_markdown_files
from helpers.crear_indice import create_embeddings_AzureOpenAI
from helpers.crear_indice import save_data

load_dotenv()


###### Parámetros
chunk_size=100
chunk_overlap=20
model_embeddings=os.getenv("AzureOpenAIembeddings_model")
######

# Parte 1: Procesar todos los archivos md y guardar los datos
script_dir = os.path.dirname(os.path.abspath(__file__)) # Path de este script
carpeta_path = os.path.join(script_dir, 'Base de datos_Cosmere')
save_folder = os.path.join(script_dir, 'Indice')

print("Procesando archivos Markdown...")

start_time = time.time()

all_chunks = process_all_markdown_files(carpeta_path, chunk_size, chunk_overlap)

# Azure OpenAI client for embeddings
client=AzureOpenAI(
  api_key=os.getenv("AzureOpenAIembeddings_APIkey"),  
  api_version=os.getenv("AzureOpenAIembeddings_APIversion"),
  azure_endpoint=os.getenv("AzureOpenAIembeddings_endpoint"),
)

if all_chunks:
    print(f"Chunks generados: {len(all_chunks)}")
    print("Generando embeddings...")
    embeddings = create_embeddings_AzureOpenAI(all_chunks, client, model_embeddings)
    print("Guardando el índice...")
    save_data(all_chunks, embeddings, save_folder)
    print(f"Índice creado y guardado exitosamente en {save_folder}.")
else:
    print("No se generaron chunks. Verifica los archivos Markdown.")

end_time = time.time()
total_time = end_time - start_time
print(f"Tiempo tardado en crear el índice: {math.trunc(total_time/60)} min y \
      {round(total_time-math.trunc(total_time/60)*60)} s")

