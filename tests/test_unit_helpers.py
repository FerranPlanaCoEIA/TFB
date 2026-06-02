import unittest

from helpers.LLM_prompts import LLMs_system_prompts
from helpers.chat_memory import (
    format_exchange_for_summary,
    format_history_for_prompt,
    get_recent_history,
)


class ChatMemoryTests(unittest.TestCase):
    def test_get_recent_history_returns_last_messages(self):
        messages = [{"role": "user", "content": str(i)} for i in range(5)]
        self.assertEqual(get_recent_history(messages, 2), messages[-2:])

    def test_get_recent_history_returns_empty_when_limit_is_non_positive(self):
        self.assertEqual(get_recent_history([{"role": "user", "content": "x"}], 0), [])

    def test_format_history_for_prompt_labels_roles(self):
        formatted = format_history_for_prompt(
            [
                {"role": "user", "content": " Hola "},
                {"role": "assistant", "content": " Mundo "},
            ]
        )
        self.assertEqual(formatted, "Usuario: Hola\nAsistente: Mundo")

    def test_format_history_for_prompt_returns_placeholder_when_empty(self):
        self.assertEqual(format_history_for_prompt([]), "No hay historial previo.")

    def test_format_exchange_for_summary_strips_whitespace(self):
        summary = format_exchange_for_summary(" Hoid? ", " Sí ")
        self.assertEqual(summary, "Usuario: Hoid?\nAsistente: Sí")


class PromptContractTests(unittest.TestCase):
    def test_known_prompts_contain_expected_contract_text(self):
        expected_snippets = {
            "elaborate_responses": "Lo siento, no puedo responderte a esa",
            "LLMasajudge": "[[Valoración: OK/KO]]",
            "rewrite_question": "reescribir la ultima pregunta",
            "chatbot_responses": "usa solo el conocimiento recuperado",
            "conversation_summary": "Sin contexto previo relevante.",
            "agentic_tool_chatbot": "search_knowledge_base_tool(query: str)",
        }

        for use_case, snippet in expected_snippets.items():
            with self.subTest(use_case=use_case):
                prompt = LLMs_system_prompts(use_case, "", "")
                self.assertIn(snippet, prompt)


if __name__ == "__main__":
    unittest.main()
