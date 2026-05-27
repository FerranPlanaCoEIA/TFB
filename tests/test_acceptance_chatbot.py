import unittest
from unittest.mock import patch

from inferencia_interfaz import inferencia_interfaz, responder_chatbot
from tests.support import FakeResponse, SequenceLLM, sample_index_data


class ChatbotAcceptanceTests(unittest.TestCase):
    def test_greeting_is_answered_without_references(self):
        llm = SequenceLLM([FakeResponse("Hola, viajero del Cosmere.")])

        with patch("helpers.agentic_chatbot_orchestrator.get_chat_llm", return_value=llm):
            with patch("helpers.agentic_chatbot_orchestrator.get_LLM_response", return_value="Resumen saludo"):
                response = inferencia_interfaz("Hola")

        self.assertEqual(response, "Hola, viajero del Cosmere.")

    def test_factual_question_returns_answer_and_clickable_references(self):
        tool_call = {
            "id": "call-1",
            "name": "search_knowledge_base_tool",
            "args": {"query": "Hoid"},
        }
        llm = SequenceLLM(
            [
                FakeResponse("", tool_calls=[tool_call]),
                FakeResponse("Hoid aparece en distintas historias del Cosmere."),
            ]
        )

        with patch("helpers.agentic_chatbot_orchestrator.load_index_data", return_value=sample_index_data()):
            with patch("helpers.agentic_chatbot_orchestrator.get_chat_llm", return_value=llm):
                with patch("helpers.agentic_chatbot_orchestrator.get_LLM_response", return_value="Resumen factual"):
                    result = responder_chatbot("¿Quién es Hoid?", [], "")

        self.assertIn("Hoid aparece", result["assistant_display_content"])
        self.assertIn("Referencias:", result["assistant_display_content"])
        self.assertIn("https://es.coppermind.net/wiki/Hoid", result["assistant_display_content"])
        self.assertEqual(result["conversation_summary"], "Resumen factual")

    def test_insufficient_information_does_not_add_references(self):
        tool_call = {
            "id": "call-1",
            "name": "search_knowledge_base_tool",
            "args": {"query": "Dato imposible"},
        }
        llm = SequenceLLM(
            [
                FakeResponse("", tool_calls=[tool_call]),
                FakeResponse("Lo siento, no puedo responderte a esa pregunta"),
            ]
        )

        with patch("helpers.agentic_chatbot_orchestrator.load_index_data", return_value=sample_index_data()):
            with patch("helpers.agentic_chatbot_orchestrator.get_chat_llm", return_value=llm):
                with patch("helpers.agentic_chatbot_orchestrator.get_LLM_response", return_value="Sin contexto previo relevante."):
                    result = responder_chatbot("¿Cuál es el color favorito de Adonalsium?", [], "")

        self.assertEqual(result["assistant_content"], "Lo siento, no puedo responderte a esa pregunta")
        self.assertNotIn("Referencias:", result["assistant_display_content"])
        self.assertEqual(result["assistant_display_content"], "Lo siento, no puedo responderte a esa pregunta")


if __name__ == "__main__":
    unittest.main()
