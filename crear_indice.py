import os
from dotenv import load_dotenv
import time
import math
from helpers.crear_indice import process_all_markdown_files
from helpers.crear_indice import create_embeddings
from helpers.crear_indice import save_data
load_dotenv()


###### Parámetros
chunk_size=int(os.getenv("CHUNK_SIZE"))
chunk_overlap=int(round(0.2*chunk_size))
model_embeddings=os.getenv("EMBEDDINGS_MODEL")
######





# Parte 1: Procesar todos los archivos md y guardar los datos
script_dir = os.path.dirname(os.path.abspath(__file__)) # Path de este script
carpeta_path = os.path.join(script_dir, 'Base de datos RAG general/Markdowns convertidos')
save_folder = os.path.join(script_dir, 'Indice')

print("Procesando archivos Markdown...")

start_time = time.time()

all_chunks = process_all_markdown_files(carpeta_path, chunk_size, chunk_overlap)

if all_chunks:
    print(f"Chunks generados: {len(all_chunks)}")
    print("Generando embeddings...")
    embeddings, model = create_embeddings(all_chunks, model_embeddings)
    print("Guardando el índice...")
    save_data(all_chunks, embeddings, model, save_folder)
    print(f"Índice creado y guardado exitosamente en {save_folder}.")
else:
    print("No se generaron chunks. Verifica los archivos Markdown.")

end_time = time.time()
total_time = end_time - start_time
print(f"Tiempo tardado en crear el índice: {math.trunc(total_time/60)} min y \
      {round(total_time-math.trunc(total_time/60)*60)} s")

