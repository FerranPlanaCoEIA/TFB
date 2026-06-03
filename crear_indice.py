import os
import time
import math
from helpers.crear_indice import process_all_markdown_files
from helpers.crear_indice import build_knowledge_graph
from helpers.crear_indice import save_data



###### Parámetros
######

# Parte 1: Procesar todos los archivos md y guardar los datos
script_dir = os.path.dirname(os.path.abspath(__file__)) # Path de este script
carpeta_path = os.path.join(script_dir, 'Base de datos_Cosmere')
save_folder = os.path.join(script_dir, 'Indice')

print("Procesando archivos Markdown para construir el knowledge graph...")

start_time = time.time()

documents = process_all_markdown_files(carpeta_path)

if documents:
    print(f"Documentos procesados: {len(documents)}")
    print("Construyendo relaciones del grafo...")
    adjacency, metadata = build_knowledge_graph(documents)
    print("Guardando el índice del knowledge graph...")
    save_data(documents, adjacency, metadata, save_folder)
    print(f"Índice creado y guardado exitosamente en {save_folder}.")
else:
    print("No se pudieron procesar documentos. Verifica los archivos Markdown.")

end_time = time.time()
total_time = end_time - start_time
print(f"Tiempo tardado en crear el índice: {math.trunc(total_time/60)} min y \
      {round(total_time-math.trunc(total_time/60)*60)} s")
