from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import requests
import json
from groq import Groq



# Función para obtener los chunks más similares
def get_similar_chunks(question, chunks, embeddings, model, top_n):
    question_embedding = model.encode([question])
    similarities = cosine_similarity(question_embedding, embeddings)[0]
    top_indices = np.argsort(similarities)[-top_n:][::-1]
    return [(chunks[i], similarities[i]) for i in top_indices]


# Función para obtener la respuesta de un LLM
def get_LLM_response(proveedor,apikey,endpoint_model,user_prompt,system_prompt):

  if proveedor=="OpenRouter":
    try:

        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {apikey}",
                "Content-Type": "application/json"
            },
            data=json.dumps({
                "model": endpoint_model,
                "messages": [
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
                ],
                "temperature": 0,
                "repetition_penalty": 0,
            })
            )

        return response.json()['choices'][0]['message']['content']

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


  elif proveedor=="Groq":
    try:

      client = Groq(
        api_key=apikey,
      )

      chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": user_prompt,
            }
        ],
        model=endpoint_model,
        temperature=0,
        frequency_penalty=0
      )

      return chat_completion.choices[0].message.content

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

    #except Exception as e:
      # Capturar cualquier otro error no previsto
      #print(f"Error inesperado: {e}")
      #return "ERROR"


