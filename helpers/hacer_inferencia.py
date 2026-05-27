import os

import numpy as np
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from openai import APIConnectionError, APIError, APITimeoutError, RateLimitError
from sklearn.metrics.pairwise import cosine_similarity



# Función para obtener los chunks más similares
def get_similar_chunks(question, chunks, embeddings, model, top_n):
    question_embedding = model.encode([question])
    similarities = cosine_similarity(question_embedding, embeddings)[0]
    top_indices = np.argsort(similarities)[-top_n:][::-1]
    return [(chunks[i], similarities[i]) for i in top_indices]


# Función para obtener la respuesta de un LLM
def get_LLM_response(endpoint_model, user_prompt, system_prompt, temperature=0):
  endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
  api_key = os.getenv("AZURE_OPENAI_API_KEY")

  if not endpoint:
    raise RuntimeError("Falta la variable de entorno AZURE_OPENAI_ENDPOINT.")
  if not api_key:
    raise RuntimeError("Falta la variable de entorno AZURE_OPENAI_API_KEY.")

  llm = ChatOpenAI(
    model=endpoint_model,
    api_key=api_key,
    base_url=endpoint,
    temperature=temperature,
  )

  messages = [
    SystemMessage(content=system_prompt),
    HumanMessage(content=user_prompt),
  ]

  try:
    response = llm.invoke(messages)
    if isinstance(response.content, str):
      return response.content
    if isinstance(response.content, list):
      return "".join(
        block.get("text", "") if isinstance(block, dict) else str(block)
        for block in response.content
      )
    raise TypeError(f"Tipo de respuesta no soportado: {type(response.content)!r}")

  except (APIConnectionError, APITimeoutError, APIError, RateLimitError) as e:
    print(f"Error al llamar a Azure OpenAI: {e}")
    return "ERROR"