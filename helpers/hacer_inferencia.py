from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import requests
import json
from litellm import completion



# Función para obtener los chunks más similares
def get_similar_chunks(question, chunks, embeddings, client, model_embeddings, top_n):
    question_embedding = client.embeddings.create(input = [question], model=model_embeddings).data[0].embedding
    similarities = cosine_similarity([question_embedding], embeddings)[0]
    top_indices = np.argsort(similarities)[-top_n:][::-1]
    return [(chunks[i], similarities[i]) for i in top_indices]


# Función para obtener la respuesta de un LLM
def get_LLM_response(proveedor,apikey,endpoint_model,user_prompt,system_prompt):

  try:
    response = completion(
      model=proveedor.lower()+"/"+endpoint_model,
      messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
      ],
      api_key=apikey,
      temperature=0,
      presence_penalty=0,
      )
    return response.choices[0].message.content
  
  except requests.exceptions.RequestException as e:
    # Manejar errores de red o del servidor
    print(f"Error de red o del servidor: {e}")
    return "ERROR"

  except (KeyError, IndexError) as e:
    # Manejar errores de estructura de respuesta inesperada
    print(f"Error en la estructura de la respuesta: {e}")
    return "ERROR"

  except json.JSONDecodeError as e:
    # Manejar errores de decodificación JSON
    print(f"Error al decodificar la respuesta JSON: {e}")
    return "ERROR"

  except Exception as e:
    # Capturar cualquier otro error no previsto
    print(f"Error inesperado: {e}")
    return "ERROR"