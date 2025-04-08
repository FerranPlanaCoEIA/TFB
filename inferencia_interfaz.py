import os
from dotenv import load_dotenv
from helpers.crear_indice import load_data
from helpers.hacer_inferencia import get_similar_chunks
from helpers.LLM_prompts import LLMs_system_prompts
from helpers.hacer_inferencia import get_LLM_response

load_dotenv()

def inferencia_interfaz(question):

    ###### Parámetros
    top_n=3
    #question = "¿Es necesario saber mucho del Cosmere para poder leer alguno de los libros?"
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
    #print("Los 10 chunks más similares a tu pregunta son:\n")
    for i, (chunk, similarity) in enumerate(similar_chunks, 1):
        # Desempaquetar la tupla (doc_id, doc_name, chunk_number, chunk_text)
        doc_id, doc_name, chunk_number, chunk_text = chunk
        url=f"https://es.coppermind.net/wiki/{doc_name[:-3].replace('es.coppermind.net__wiki_','').replace('_',' ')}"
        #print(f"{i}. DOCID: {doc_id} | Document Name: {url} | Chunk number: {chunk_number} | Similarity: {similarity:.4f}\n{chunk_text}\n")
        name_doc=f"{doc_name[:-3].replace('es.coppermind.net__wiki_','').replace('_',' ')}"
        user_prompt+=f"{name_doc}: {chunk_text}\n"




    APIkey_OpenRouter=os.getenv("LLMsAPIkey_v7")
    APIkey_Groq=os.getenv("LLMsAPIkey_Groq")
    APIkey_OpenAI=os.getenv("LLMsAPIkey_OpenAI_v5")

    system_prompt=LLMs_system_prompts("elaborate_responses","","")
    respuesta_LLM=get_LLM_response("OpenRouter",APIkey_OpenRouter,"meta-llama/llama-4-scout:free",user_prompt,system_prompt)
    #respuesta_LLM=get_LLM_response("Groq",APIkey_Groq,"llama-3.3-70b-versatile",user_prompt,system_prompt)
    #respuesta_LLM=get_LLM_response("OpenAI",APIkey_OpenAI,"gpt-4o-mini",user_prompt,system_prompt)
    print(respuesta_LLM)

    return respuesta_LLM

