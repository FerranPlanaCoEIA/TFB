import os
import re
from functools import lru_cache
from urllib.parse import quote

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool
from openai import APIConnectionError, APIError, APITimeoutError, RateLimitError

from helpers.LLM_prompts import LLMs_system_prompts
from helpers.chat_memory import (
    format_exchange_for_summary,
    get_recent_history,
)
from helpers.crear_indice import load_data
from helpers.hacer_inferencia import (
    build_knowledge_block,
    get_chat_llm,
    get_LLM_response,
    search_knowledge_base,
)


DEFAULT_TOP_N = 5
MAX_HISTORY_MESSAGES = 6
MAX_TOOL_ITERATIONS = 4
MAX_ACCUMULATED_RESULTS = 8
MODEL_RESPONSE = "gpt-5.1"
EMPTY_SUMMARY = "Sin contexto previo relevante."
INSUFFICIENT_INFORMATION_RESPONSE = "Lo siento, no puedo responderte a esa pregunta"


@lru_cache(maxsize=1)
def load_index_data():
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    save_folder = os.path.join(repo_root, "Indice")
    return load_data(save_folder)


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


def _print_tool_log(question, tool_queries):
    print("\n=== AGENTIC RAG LOG ===")
    print(f"Pregunta: {question}")
    if not tool_queries:
        print("Tool calls: 0")
        print("Queries: ninguna")
    else:
        print(f"Tool calls: {len(tool_queries)}")
        for index, query in enumerate(tool_queries, 1):
            print(f"{index}. search_knowledge_base_tool(query={query!r})")
    print("=== END AGENTIC RAG LOG ===")


def _merge_results(existing_results, new_results, max_results):
    merged_results = list(existing_results)
    seen_keys = {(result["doc_name"], result["chunk_number"]) for result in merged_results}

    for result in new_results:
        key = (result["doc_name"], result["chunk_number"])
        if key in seen_keys:
            continue
        merged_results.append(result)
        seen_keys.add(key)
        if len(merged_results) >= max_results:
            break

    return merged_results


def _history_to_messages(conversation_history):
    recent_history = get_recent_history(conversation_history, MAX_HISTORY_MESSAGES)
    messages = []
    for message in recent_history:
        if message["role"] == "user":
            messages.append(HumanMessage(content=message["content"]))
        elif message["role"] == "assistant":
            messages.append(AIMessage(content=message["content"]))
    return messages


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


def _build_agent_messages(question, conversation_history, conversation_summary):
    messages = [
        SystemMessage(content=LLMs_system_prompts("agentic_tool_chatbot", "", "")),
        SystemMessage(content=f"Resumen acumulado de la conversación:\n{conversation_summary or EMPTY_SUMMARY}"),
    ]
    messages.extend(_history_to_messages(conversation_history))
    messages.append(HumanMessage(content=question))
    return messages


@tool
def search_knowledge_base_tool(query: str) -> str:
    """Busca en el knowledge graph del Cosmere y devuelve fragmentos relevantes para responder."""
    chunks, embeddings, model = load_index_data()
    results = search_knowledge_base(query, chunks, embeddings, model, DEFAULT_TOP_N)
    if not results:
        return "Sin resultados recuperados."

    knowledge_block = build_knowledge_block(results, max_results=DEFAULT_TOP_N)
    return (
        f"Consulta ejecutada: {query}\n"
        f"Fragmentos recuperados:\n{knowledge_block}"
    )


def _run_tool_call(tool_call, accumulated_results):
    if tool_call["name"] != "search_knowledge_base_tool":
        return "Tool no soportada.", accumulated_results

    query = str(tool_call["args"].get("query", "")).strip()
    if not query:
        return "La tool requiere un query no vacío.", accumulated_results

    chunks, embeddings, model = load_index_data()
    new_results = search_knowledge_base(query, chunks, embeddings, model, DEFAULT_TOP_N)
    merged_results = _merge_results(accumulated_results, new_results, MAX_ACCUMULATED_RESULTS)
    tool_output = search_knowledge_base_tool.invoke({"query": query})
    return tool_output, merged_results


def _invoke_agent(messages):
    try:
        llm = get_chat_llm(MODEL_RESPONSE, temperature=0).bind_tools([search_knowledge_base_tool])
        return llm.invoke(messages)
    except (APIConnectionError, APITimeoutError, APIError, RateLimitError) as e:
        print(f"Error al llamar a Azure OpenAI: {e}")
        return "ERROR"


def _invoke_final_response(messages):
    try:
        return get_chat_llm(MODEL_RESPONSE, temperature=0).invoke(messages)
    except (APIConnectionError, APITimeoutError, APIError, RateLimitError) as e:
        print(f"Error al llamar a Azure OpenAI: {e}")
        return "ERROR"


def _coerce_response_text(response):
    if response == "ERROR":
        return "ERROR"
    if isinstance(response.content, str):
        return response.content
    if isinstance(response.content, list):
        return "".join(
            block.get("text", "") if isinstance(block, dict) else str(block)
            for block in response.content
        )
    raise TypeError(f"Tipo de respuesta no soportado: {type(response.content)!r}")


def generate_agentic_chatbot_response(question, conversation_history, conversation_summary):
    messages = _build_agent_messages(question, conversation_history, conversation_summary)
    accumulated_results = []
    tool_queries = []

    for _ in range(MAX_TOOL_ITERATIONS):
        response = _invoke_agent(messages)
        if response == "ERROR":
            _print_tool_log(question, tool_queries)
            return {
                "assistant_content": "ERROR",
                "assistant_display_content": "ERROR",
                "conversation_summary": conversation_summary or EMPTY_SUMMARY,
            }

        messages.append(response)
        if not response.tool_calls:
            raw_response = _coerce_response_text(response)
            break

        for tool_call in response.tool_calls:
            query = str(tool_call["args"].get("query", "")).strip()
            if query:
                tool_queries.append(query)
            tool_output, accumulated_results = _run_tool_call(tool_call, accumulated_results)
            messages.append(ToolMessage(content=tool_output, tool_call_id=tool_call["id"]))
    else:
        messages.append(
            HumanMessage(
                content=(
                    "Ya has hecho suficientes pasos. Responde ahora al usuario con la información disponible. "
                    f'Si no basta, di exactamente: {INSUFFICIENT_INFORMATION_RESPONSE}'
                )
            )
        )
        final_response = _invoke_final_response(messages)
        raw_response = _coerce_response_text(final_response)

    _print_tool_log(question, tool_queries)

    if (
        accumulated_results
        and "[[" not in raw_response
        and raw_response.strip() not in {"ERROR", INSUFFICIENT_INFORMATION_RESPONSE}
    ):
        reference_lines = []
        seen = set()
        for result in accumulated_results:
            display_name = result["display_name"]
            if display_name in seen:
                continue
            seen.add(display_name)
            reference_lines.append(f"[[{display_name}]]")
        if reference_lines:
            raw_response = f"{raw_response}\n" + "\n".join(reference_lines)

    answer_text = _remove_references(raw_response)
    references = _extract_references(raw_response)
    updated_summary = update_conversation_summary(conversation_summary, question, answer_text)

    return {
        "assistant_content": answer_text,
        "assistant_display_content": _format_response_for_streamlit(answer_text, references),
        "conversation_summary": updated_summary,
    }
