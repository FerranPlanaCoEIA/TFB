import unittest
from types import SimpleNamespace
from unittest.mock import patch

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from helpers import agentic_chatbot_orchestrator as orchestrator


class OrchestratorPureFunctionTests(unittest.TestCase):
    def test_extract_references_deduplicates_and_trims(self):
        raw = "Texto [[Hoid]] [[ Roshar ]] [[Hoid]]"
        self.assertEqual(orchestrator._extract_references(raw), ["Hoid", "Roshar"])

    def test_remove_references_strips_markup(self):
        self.assertEqual(orchestrator._remove_references("Hola [[Hoid]]"), "Hola")

    def test_format_response_for_streamlit_keeps_plain_text_without_references(self):
        self.assertEqual(orchestrator._format_response_for_streamlit("Hola", []), "Hola")

    def test_format_response_for_streamlit_adds_reference_links(self):
        formatted = orchestrator._format_response_for_streamlit("Hola", ["Hoid"])
        self.assertIn("Referencias:", formatted)
        self.assertIn("https://es.coppermind.net/wiki/Hoid", formatted)

    def test_merge_results_deduplicates_and_respects_maximum(self):
        existing = [{"doc_name": "a", "chunk_number": 0, "display_name": "A"}]
        new = [
            {"doc_name": "a", "chunk_number": 0, "display_name": "A"},
            {"doc_name": "b", "chunk_number": 1, "display_name": "B"},
            {"doc_name": "c", "chunk_number": 2, "display_name": "C"},
        ]

        merged = orchestrator._merge_results(existing, new, max_results=2)

        self.assertEqual(
            [(item["doc_name"], item["chunk_number"]) for item in merged],
            [("a", 0), ("b", 1)],
        )

    def test_history_to_messages_converts_roles(self):
        conversation_history = [
            {"role": "user", "content": "Hola"},
            {"role": "assistant", "content": "Saludos"},
        ]

        messages = orchestrator._history_to_messages(conversation_history)

        self.assertIsInstance(messages[0], HumanMessage)
        self.assertIsInstance(messages[1], AIMessage)
        self.assertEqual(messages[0].content, "Hola")
        self.assertEqual(messages[1].content, "Saludos")

    def test_update_conversation_summary_keeps_previous_summary_on_error_answer(self):
        summary = orchestrator.update_conversation_summary("Resumen previo", "Pregunta", "ERROR")
        self.assertEqual(summary, "Resumen previo")

    def test_update_conversation_summary_uses_llm_when_available(self):
        with patch("helpers.agentic_chatbot_orchestrator.get_LLM_response", return_value="Resumen nuevo"):
            summary = orchestrator.update_conversation_summary("Resumen previo", "Pregunta", "Respuesta")

        self.assertEqual(summary, "Resumen nuevo")

    def test_build_agent_messages_includes_summary_history_and_question(self):
        history = [{"role": "user", "content": "Antes"}]
        messages = orchestrator._build_agent_messages("Ahora", history, "Resumen")

        self.assertIsInstance(messages[0], SystemMessage)
        self.assertIn("Resumen acumulado", messages[1].content)
        self.assertEqual(messages[-1].content, "Ahora")

    def test_coerce_response_text_supports_string_and_block_lists(self):
        text_response = SimpleNamespace(content="texto")
        block_response = SimpleNamespace(content=[{"text": "a"}, {"text": "b"}])

        self.assertEqual(orchestrator._coerce_response_text(text_response), "texto")
        self.assertEqual(orchestrator._coerce_response_text(block_response), "ab")

    def test_coerce_response_text_raises_on_unsupported_type(self):
        with self.assertRaises(TypeError):
            orchestrator._coerce_response_text(SimpleNamespace(content={"x": 1}))

    def test_run_tool_call_handles_unsupported_and_empty_queries(self):
        unsupported_output, unsupported_results = orchestrator._run_tool_call(
            {"name": "otro", "args": {}},
            [],
        )
        empty_output, empty_results = orchestrator._run_tool_call(
            {"name": "search_knowledge_base_tool", "args": {"query": "   "}},
            [],
        )

        self.assertEqual(unsupported_output, "Tool no soportada.")
        self.assertEqual(unsupported_results, [])
        self.assertEqual(empty_output, "La tool requiere un query no vacío.")
        self.assertEqual(empty_results, [])


if __name__ == "__main__":
    unittest.main()
