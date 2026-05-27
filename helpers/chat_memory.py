def get_recent_history(messages, max_messages=6):
    if max_messages <= 0:
        return []
    return messages[-max_messages:]


def format_history_for_prompt(messages):
    if not messages:
        return "No hay historial previo."

    formatted_messages = []
    for message in messages:
        role = "Usuario" if message["role"] == "user" else "Asistente"
        formatted_messages.append(f"{role}: {message['content'].strip()}")

    return "\n".join(formatted_messages)


def format_exchange_for_summary(user_question, assistant_answer):
    return (
        f"Usuario: {user_question.strip()}\n"
        f"Asistente: {assistant_answer.strip()}"
    )
