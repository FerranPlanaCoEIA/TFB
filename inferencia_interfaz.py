from dotenv import load_dotenv

from helpers.chatbot_orchestrator import generate_chatbot_response

load_dotenv()


def inferencia_interfaz(question):
    return generate_chatbot_response(question, [], "")["assistant_display_content"]


def responder_chatbot(question, conversation_history, conversation_summary):
    return generate_chatbot_response(question, conversation_history, conversation_summary)
