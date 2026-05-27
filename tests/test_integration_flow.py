import unittest
from unittest.mock import patch

from inferencia_interfaz import responder_chatbot
from helpers import agentic_chatbot_orchestrator as orchestrator
from tests.support import FakeResponse, SequenceLLM, sample_index_data


class IntegrationFlowTests(unittest.TestCase):
    def test_search_knowledge_base_tool_uses_real_retrieval_pipeline(self):
        with patch("helpers.agentic_chatbot_orchestrator.load_index_data", return_value=sample_index_data()):
            output = orchestrator.search_knowledge_base_tool.invoke({"query": "Hoid"})

        self.assertIn("Consulta ejecutada: Hoid", output)
        self.assertIn("[[Hoid]]", output)

    def test_generate_agentic_response_runs_tool_loop_and_formats_references(self):
        tool_call = {
            "id": "call-1",
            "name": "search_knowledge_base_tool",
            "args": {"query": "Hoid"},
        }
        llm = SequenceLLM(
            [
                FakeResponse("", tool_calls=[tool_call]),
                FakeResponse("Hoid es un personaje importante del Cosmere."),
            ]
        )

        with patch("helpers.agentic_chatbot_orchestrator.load_index_data", return_value=sample_index_data()):
            with patch("helpers.agentic_chatbot_orchestrator.get_chat_llm", return_value=llm):
                with patch("helpers.agentic_chatbot_orchestrator.get_LLM_response", return_value="Resumen actualizado"):
                    result = orchestrator.generate_agentic_chatbot_response("¿Quién es Hoid?", [], "")

        self.assertEqual(result["assistant_content"], "Hoid es un personaje importante del Cosmere.")
        self.assertIn("Referencias:", result["assistant_display_content"])
        self.assertIn("[Hoid](https://es.coppermind.net/wiki/Hoid)", result["assistant_display_content"])
        self.assertEqual(result["conversation_summary"], "Resumen actualizado")

    def test_responder_chatbot_exposes_orchestrator_result(self):
        expected = {
            "assistant_content": "Texto",
            "assistant_display_content": "Texto",
            "conversation_summary": "Resumen",
        }
        with patch("inferencia_interfaz.generate_agentic_chatbot_response", return_value=expected):
            result = responder_chatbot("Pregunta", [], "")

        self.assertEqual(result, expected)


if __name__ == "__main__":
    unittest.main()
