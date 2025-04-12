import os
import re
from dotenv import load_dotenv
from helpers.crear_indice import load_data
from helpers.hacer_inferencia import get_similar_chunks
from helpers.LLM_prompts import LLMs_system_prompts
from helpers.hacer_inferencia import get_LLM_response

load_dotenv()

def inferencia_interfaz(question):

    ###### Parámetros
    top_n=int(os.getenv("TOP_N"))
    model_response=os.getenv("LLM_MODEL")
    APIkey=os.getenv("LLM_API_KEY")
    LLM_provider=os.getenv("LLM_PROVIDER")
    ######


    # Parte 2: Responder preguntas
    script_dir = os.path.dirname(os.path.abspath(__file__)) # Path de este script
    save_folder = os.path.join(script_dir, 'Indice')

    # Cargar los datos procesados
    chunks, embeddings, model = load_data(save_folder)

    # Obtener los chunks más similares
    similar_chunks = get_similar_chunks(question, chunks, embeddings, model, top_n)

    # Mostrar los resultados
    user_prompt=f"Pregunta: {question}\n\nConocimiento:\n"
    for i, (chunk, similarity) in enumerate(similar_chunks, 1):
        # Desempaquetar la tupla (doc_id, doc_name, chunk_number, chunk_text)
        doc_id, doc_name, chunk_number, chunk_text = chunk
        user_prompt+=f"[[{doc_name}]]: {chunk_text}\n"

    system_prompt=LLMs_system_prompts("elaborate_responses","","")
    respuesta_LLM=get_LLM_response(LLM_provider,APIkey,model_response,user_prompt,system_prompt)

    patron=r"\[\[.*?\]\]"
    referencias_array=re.findall(patron,respuesta_LLM)
    for ii in range(len(referencias_array)):
        referencias_array[ii]=re.sub(r"\[\[|\]\]|.md","",referencias_array[ii])
    referencias="<br>".join(referencias_array)
    referencias="<br><br>Referencias:<br>"+referencias
    respuesta_LLM=re.sub(patron,"",respuesta_LLM).strip()+referencias

    return respuesta_LLM

