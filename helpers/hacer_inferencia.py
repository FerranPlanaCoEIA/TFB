import os

import numpy as np
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from openai import APIConnectionError, APIError, APITimeoutError, RateLimitError
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


DEFAULT_EMBEDDINGS_MODEL = "distiluse-base-multilingual-cased-v2"


def get_chat_llm(endpoint_model, temperature=0):
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    api_key = os.getenv("AZURE_OPENAI_API_KEY")

    if not endpoint:
        raise RuntimeError("Falta la variable de entorno AZURE_OPENAI_ENDPOINT.")
    if not api_key:
        raise RuntimeError("Falta la variable de entorno AZURE_OPENAI_API_KEY.")

    return ChatOpenAI(
        model=endpoint_model,
        api_key=api_key,
        base_url=endpoint,
        temperature=temperature,
    )


def _patch_transformer_config(model):
    for module in getattr(model, "_modules", {}).values():
        auto_model = getattr(module, "auto_model", None)
        if auto_model is None or not hasattr(auto_model, "config"):
            continue

        config = auto_model.config
        if not hasattr(config, "output_attentions") and hasattr(config, "_output_attentions"):
            config.output_attentions = config._output_attentions
        if not hasattr(config, "output_hidden_states") and hasattr(config, "_output_hidden_states"):
            config.output_hidden_states = config._output_hidden_states
        if not hasattr(auto_model, "_use_flash_attention_2"):
            auto_model._use_flash_attention_2 = False
        if not hasattr(auto_model, "_use_sdpa"):
            auto_model._use_sdpa = False

    return model


def _encode_question(question, model):
    try:
        return model.encode([question]), model
    except AttributeError:
        patched_model = _patch_transformer_config(model)
        try:
            return patched_model.encode([question]), patched_model
        except AttributeError:
            fallback_model = SentenceTransformer(DEFAULT_EMBEDDINGS_MODEL)
            return fallback_model.encode([question]), fallback_model



# Función para obtener los chunks más similares
def get_similar_chunks(question, chunks, embeddings, model, top_n):
    question_embedding, _resolved_model = _encode_question(question, model)
    similarities = cosine_similarity(question_embedding, embeddings)[0]
    top_indices = np.argsort(similarities)[-top_n:][::-1]
    return [(chunks[i], similarities[i]) for i in top_indices]


def search_knowledge_base(question, chunks, embeddings, model, top_n):
    similar_chunks = get_similar_chunks(question, chunks, embeddings, model, top_n)
    search_results = []

    for chunk, similarity in similar_chunks:
        doc_id, doc_name, chunk_number, chunk_text = chunk
        display_name = doc_name[:-3].replace("es.coppermind.net__wiki_", "").replace("_", " ")
        search_results.append(
            {
                "doc_id": doc_id,
                "doc_name": doc_name,
                "display_name": display_name,
                "chunk_number": chunk_number,
                "chunk_text": chunk_text,
                "similarity": float(similarity),
            }
        )

    return search_results


def build_knowledge_block(search_results, max_results=None):
    selected_results = search_results if max_results is None else search_results[:max_results]
    knowledge_lines = []
    for result in selected_results:
        knowledge_lines.append(f"[[{result['display_name']}]]: {result['chunk_text']}")
    return "\n".join(knowledge_lines)


def serialize_search_results(search_results, max_results=5, max_chars=3000):
    if not search_results:
        return "Sin resultados recuperados."

    selected_results = search_results[:max_results]
    lines = []
    for index, result in enumerate(selected_results, 1):
        lines.append(
            f"{index}. Documento: {result['display_name']} | "
            f"Chunk: {result['chunk_number']} | "
            f"Similaridad: {result['similarity']:.4f}\n"
            f"   Contenido: {result['chunk_text']}"
        )

    serialized_results = "\n".join(lines)
    if len(serialized_results) > max_chars:
        return serialized_results[: max_chars - 3] + "..."

    return serialized_results


# Función para obtener la respuesta de un LLM
def get_LLM_response(endpoint_model, user_prompt, system_prompt, temperature=0):
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt),
    ]

    try:
        response = get_chat_llm(endpoint_model, temperature=temperature).invoke(messages)
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