import os
import re

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from openai import APIConnectionError, APIError, APITimeoutError, RateLimitError
from unidecode import unidecode


STOPWORDS = {
    "a",
    "al",
    "algo",
    "como",
    "con",
    "cual",
    "cuales",
    "cuanto",
    "cuantos",
    "de",
    "del",
    "donde",
    "el",
    "en",
    "es",
    "esta",
    "este",
    "hay",
    "la",
    "las",
    "lo",
    "los",
    "para",
    "por",
    "que",
    "quien",
    "se",
    "sobre",
    "su",
    "sus",
    "un",
    "una",
    "y",
}


def _normalize_text(text):
    normalized = unidecode(str(text or "")).lower()
    return " ".join(normalized.split())


def _tokenize(text):
    return [
        token
        for token in re.findall(r"[a-z0-9]+", _normalize_text(text))
        if len(token) > 1 and token not in STOPWORDS
    ]


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


def _document_lookup(documents):
    return {document["doc_id"]: document for document in documents}


def _edge_score(question_normalized, query_tokens, edge, documents_by_id):
    target = documents_by_id[edge["target"]]
    relation_text = f"{edge['relation']} {target['display_name']}"
    relation_tokens = set(_tokenize(relation_text))
    score = 0.0

    target_name = _normalize_text(target["display_name"])
    if target_name and target_name in question_normalized:
        score += 3.0

    overlap = len(query_tokens & relation_tokens)
    if overlap:
        score += overlap * 0.6

    return score


def _build_context(document, edges, documents_by_id):
    relation_lines = []
    for _score, edge in edges[:3]:
        target = documents_by_id[edge["target"]]["display_name"]
        relation = edge["relation"].replace("_", " ")
        relation_lines.append(f"{relation}: {target}")

    summary = document["summary"].strip()
    if relation_lines:
        return f"{summary}\nRelaciones relevantes: " + "; ".join(relation_lines)
    return summary


def get_similar_chunks(question, chunks, embeddings, model, top_n):
    question_normalized = _normalize_text(question)
    query_tokens = set(_tokenize(question))
    documents_by_id = _document_lookup(chunks)
    matched_doc_ids = {
        doc_id
        for normalized_title, doc_id in model.get("title_to_doc_id", {}).items()
        if normalized_title and normalized_title in question_normalized
    }
    scored_results = []

    for document in chunks:
        title_normalized = _normalize_text(document["display_name"])
        title_tokens = set(_tokenize(document["display_name"]))
        document_tokens = set(document.get("tokens", []))

        score = 0.0
        if document["doc_id"] in matched_doc_ids:
            score += 12.0
        if title_normalized and title_normalized in question_normalized:
            score += 5.0

        score += len(query_tokens & title_tokens) * 1.5
        if query_tokens:
            score += (len(query_tokens & document_tokens) / len(query_tokens)) * 3.0

        edge_matches = []
        for edge in embeddings.get(document["doc_id"], []):
            edge_match_score = _edge_score(question_normalized, query_tokens, edge, documents_by_id)
            if edge["target"] in matched_doc_ids:
                edge_match_score += 1.5
            if edge_match_score > 0:
                edge_matches.append((edge_match_score, edge))

        edge_matches.sort(key=lambda item: item[0], reverse=True)
        score += sum(match_score for match_score, _edge in edge_matches[:2])

        context = _build_context(document, edge_matches, documents_by_id)
        scored_results.append(
            (
                (document["doc_id"], document["doc_name"], 0, context),
                float(score),
            )
        )

    scored_results.sort(key=lambda item: item[1], reverse=True)
    return scored_results[:top_n]


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

    except (APIConnectionError, APITimeoutError, APIError, RateLimitError) as error:
        print(f"Error al llamar a Azure OpenAI: {error}")
        return "ERROR"
