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
    top_n=15
    model_response="meta-llama/llama-4-maverick:free"
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
        url=f"https://es.coppermind.net/wiki/{doc_name[:-3].replace('es.coppermind.net__wiki_','').replace('_',' ')}"
        name_doc=f"{doc_name[:-3].replace('es.coppermind.net__wiki_','').replace('_',' ')}"
        user_prompt+=f"[[{name_doc}]]: {chunk_text}\n"

    APIkey_OpenRouter=os.getenv("LLMsAPIkey_v2")

    system_prompt=LLMs_system_prompts("elaborate_responses","","")
    respuesta_LLM=get_LLM_response("OpenRouter",APIkey_OpenRouter,model_response,user_prompt,system_prompt)

    patron=r"\[\[.*?\]\]"
    referencias_array=re.findall(patron,respuesta_LLM)
    for ii in range(len(referencias_array)):
        referencias_array[ii]=re.sub(r"\[\[|\]\]","",referencias_array[ii])
        url="https://es.coppermind.net/wiki/"+referencias_array[ii]
        referencias_array[ii]=f"<a href='{url}'>{referencias_array[ii]}</a>"
    referencias="<br>".join(referencias_array)
    referencias="<br><br>Referencias:<br>"+referencias
    respuesta_LLM=re.sub(patron,"",respuesta_LLM).strip()+referencias

    return respuesta_LLM

