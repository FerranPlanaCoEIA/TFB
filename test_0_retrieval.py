import os
from dotenv import load_dotenv
import pandas as pd
import time
from unidecode import unidecode
from openai import AzureOpenAI
from helpers.crear_indice import load_data
from helpers.hacer_inferencia import get_similar_chunks

load_dotenv()

###### Parámetros
top_n=10
model_embeddings=os.getenv("AzureOpenAIembeddings_model")
######

client=AzureOpenAI(
  api_key=os.getenv("AzureOpenAIembeddings_APIkey"),  
  api_version=os.getenv("AzureOpenAIembeddings_APIversion"),
  azure_endpoint=os.getenv("AzureOpenAIembeddings_endpoint"),
) 

print("Ejecutando...")

# Definir la carpeta en Google Drive donde se guardaron los datos
script_dir = os.path.dirname(os.path.abspath(__file__)) # Path de este script
save_folder = os.path.join(script_dir, 'Indice')

# Cargar los datos procesados
chunks, embeddings = load_data(save_folder)


# Test Automático (RAG)

ruta_input= os.path.join(script_dir, 'Input Test Automático.xlsx') # Path del input del test
ruta_output= os.path.join(script_dir, 'Output Test Automático.xlsx') # Path del output del test
df=pd.read_excel(ruta_input)


PREGUNTA_array=df["PREGUNTA"].tolist()
DOCSBEST_array=df["DOCS_BEST"].tolist()
RESPUESTABEST_array=df["RESPUESTA_BEST"].tolist()

RESULTADORAG_array=[]
docname_array=[]
testRAG_array=[]
Respuesta_userprompt_array=[]
Respuesta_array=[]
Test_fuentes=[]
LLMasajudge_array=[]
LLMasajudge_valoracion_array=[]
LLMasajudge_razonamiento_array=[]
for k in range(len(PREGUNTA_array)):
  similar_chunks=get_similar_chunks(PREGUNTA_array[k],chunks,embeddings,client,model_embeddings,top_n)
  time.sleep(1.1)

  RESULTADORAG_intermedio_array=[]
  docname_intermedio_array=[]
  user_prompt=f"Pregunta: {PREGUNTA_array[k]}\n\nConocimiento:\n"
  for i, (chunk, similarity) in enumerate(similar_chunks, 1):
    # Desempaquetar la tupla (doc_id, doc_name, chunk_number, chunk_text)
    doc_id, doc_name, chunk_number, chunk_text = chunk
    url=f"https://es.coppermind.net/wiki/{doc_name[:-3].replace('es.coppermind.net__wiki_','').replace('_',' ')}"
    RESULTADORAG_intermedio_array.append(f"{i}. DOCID: {doc_id} | Document Name: {url} | Chunk number: {chunk_number} | Similarity: {similarity:.4f}\n{chunk_text}\n")
    docname_intermedio_array.append(doc_name[:-3].replace('es.coppermind.net__wiki_','').replace('_',' '))
    name_doc=f"{doc_name[:-3].replace('es.coppermind.net__wiki_','').replace('_',' ')}"
    user_prompt+=f"[[{name_doc}]] {chunk_text}\n"

  RESULTADORAG_array.append(RESULTADORAG_intermedio_array)
  docname_intermedio_array=list(dict.fromkeys(docname_intermedio_array))  # Quedarnos con los nombres únicos de la lista en orden de aparición
  docname_array.append(docname_intermedio_array)

  testRAG_array.append("KO")
  for j in docname_intermedio_array:
    if unidecode(j) in unidecode(DOCSBEST_array[k]):
      testRAG_array[k]="OK"
      break

  Respuesta_userprompt_array.append(user_prompt)
  Respuesta_array.append("")
  Test_fuentes.append("")
  LLMasajudge_array.append("")
  LLMasajudge_valoracion_array.append("")
  LLMasajudge_razonamiento_array.append("")



df["RESULTADO_RAG"]=RESULTADORAG_array
df["DOCS_RAG"]=docname_array
df["TEST_RAG"]=testRAG_array
df["RESPUESTA_USERPROMPT"]=Respuesta_userprompt_array
df["RESPUESTA"]=Respuesta_array
df["TEST_FUENTES"]=Test_fuentes
df["LLMasajudge"]=LLMasajudge_array
df["LLMasajudge_valoracion"]=LLMasajudge_valoracion_array
df["LLMasajudge_razonamiento"]=LLMasajudge_razonamiento_array


# Output del Test Automático
df.to_excel(ruta_output,index=False)
print(f'Archivo Excel guardado en: {ruta_output}')