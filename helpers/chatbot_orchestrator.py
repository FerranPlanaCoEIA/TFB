import os
import re
from functools import lru_cache
from urllib.parse import quote

from helpers.LLM_prompts import LLMs_system_prompts
from helpers.chat_memory import (
    format_exchange_for_summary,
    format_history_for_prompt,
    get_recent_history,
)
from helpers.crear_indice import load_data
from helpers.hacer_inferencia import get_LLM_response, get_similar_chunks


TOP_N = 10
MODEL_RESPONSE = "gpt-5.1"
MAX_HISTORY_MESSAGES = 6
EMPTY_SUMMARY = "Sin contexto previo relevante."


@lru_cache(maxsize=1)
def load_index_data():
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    save_folder = os.path.join(repo_root, "Indice")
    return load_data(save_folder)


def _doc_name_from_file(doc_name):
    return doc_name[:-3].replace("es.coppermind.net__wiki_", "").replace("_", " ")


def _build_knowledge_block(similar_chunks):
    knowledge_lines = []
    for chunk, _similarity in similar_chunks:
        _doc_id, doc_name, _chunk_number, chunk_text = chunk
        knowledge_lines.append(f"[[{_doc_name_from_file(doc_name)}]]: {chunk_text}")
    return "\n".join(knowledge_lines)


def _extract_references(raw_response):
    references = re.findall(r"\[\[(.*?)\]\]", raw_response)
    unique_references = []
    seen = set()
    for reference in references:
        cleaned_reference = reference.strip()
        if cleaned_reference and cleaned_reference not in seen:
            seen.add(cleaned_reference)
            unique_references.append(cleaned_reference)
    return unique_references


def _remove_references(raw_response):
    return re.sub(r"\[\[.*?\]\]", "", raw_response).strip()


def _format_response_for_streamlit(answer_text, references):
    if not references:
        return answer_text

    reference_lines = []
    for reference in references:
        url = f"https://es.coppermind.net/wiki/{quote(reference)}"
        reference_lines.append(f"- [{reference}]({url})")

    return f"{answer_text}\n\nReferencias:\n" + "\n".join(reference_lines)


def rewrite_question(question, conversation_history, conversation_summary):
    recent_history = get_recent_history(conversation_history, MAX_HISTORY_MESSAGES)
    if not recent_history:
        return question

    user_prompt = (
        f"Resumen acumulado:\n{conversation_summary or EMPTY_SUMMARY}\n\n"
        f"Historial reciente:\n{format_history_for_prompt(recent_history)}\n\n"
        f"Ultima pregunta del usuario:\n{question}"
    )
    rewritten_question = get_LLM_response(
        MODEL_RESPONSE,
        user_prompt,
        LLMs_system_prompts("rewrite_question", "", ""),
    ).strip()

    if rewritten_question and rewritten_question != "ERROR":
        return rewritten_question

    return question


def update_conversation_summary(current_summary, user_question, assistant_answer):
    if assistant_answer == "ERROR":
        return current_summary or EMPTY_SUMMARY

    user_prompt = (
        f"Resumen acumulado actual:\n{current_summary or EMPTY_SUMMARY}\n\n"
        f"Nuevo intercambio:\n"
        f"{format_exchange_for_summary(user_question, assistant_answer)}"
    )
    updated_summary = get_LLM_response(
        MODEL_RESPONSE,
        user_prompt,
        LLMs_system_prompts("conversation_summary", "", ""),
    ).strip()

    if updated_summary and updated_summary != "ERROR":
        return updated_summary

    return current_summary or EMPTY_SUMMARY


def generate_chatbot_response(question, conversation_history, conversation_summary):
    chunks, embeddings, model = load_index_data()

    standalone_question = rewrite_question(question, conversation_history, conversation_summary)
    similar_chunks = get_similar_chunks(standalone_question, chunks, embeddings, model, TOP_N)
    recent_history = get_recent_history(conversation_history, MAX_HISTORY_MESSAGES)

    user_prompt = (
        f"Resumen acumulado:\n{conversation_summary or EMPTY_SUMMARY}\n\n"
        f"Historial reciente:\n{format_history_for_prompt(recent_history)}\n\n"
        f"Pregunta actual del usuario:\n{question}\n\n"
        f"Pregunta reescrita para retrieval:\n{standalone_question}\n\n"
        f"Conocimiento:\n{_build_knowledge_block(similar_chunks)}"
    )
    raw_response = get_LLM_response(
        MODEL_RESPONSE,
        user_prompt,
        LLMs_system_prompts("chatbot_responses", "", ""),
    )

    if raw_response == "ERROR":
        return {
            "assistant_content": "ERROR",
            "assistant_display_content": "ERROR",
            "conversation_summary": conversation_summary or EMPTY_SUMMARY,
        }

    answer_text = _remove_references(raw_response)
    references = _extract_references(raw_response)
    updated_summary = update_conversation_summary(
        conversation_summary,
        question,
        answer_text,
    )

    return {
        "assistant_content": answer_text,
        "assistant_display_content": _format_response_for_streamlit(answer_text, references),
        "conversation_summary": updated_summary,
    }
